from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
import stripe
import uuid
from django.urls import reverse

from django.db.models import Q

from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import os
from django.core.files.base import ContentFile
import qrcode
from io import BytesIO


class SubscriptionPlan(models.Model):
    PLAN_CHOICES = [
        ('Free', 'Free Trial'),
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('business', 'Business'),
    ]

    name = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    description = models.JSONField(blank=True, null=True)
    monthly_price = models.DecimalField(max_digits=7, decimal_places=2)
    yearly_price = models.DecimalField(max_digits=7, decimal_places=2)

    stripe_monthly_price_id = models.CharField(max_length=100, blank=True, null=True)
    stripe_yearly_price_id = models.CharField(max_length=100, blank=True, null=True)

    max_photos = models.PositiveIntegerField(blank=True, null=True)
    max_videos = models.PositiveIntegerField(blank=True, null=True)
    max_file_size_mb = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        return self.get_name_display()

    def save(self, *args, **kwargs):
        # First save the object to the DB
        super().save(*args, **kwargs)

        # Then create Stripe product/prices if missing
        if not self.stripe_monthly_price_id or not self.stripe_yearly_price_id:
            product = stripe.Product.create(name=self.get_name_display())

            if not self.stripe_monthly_price_id:
                monthly_price = stripe.Price.create(
                    unit_amount=int(self.monthly_price * 100),
                    currency="usd",
                    recurring={"interval": "month"},
                    product=product.id,
                )
                self.stripe_monthly_price_id = monthly_price.id

            if not self.stripe_yearly_price_id:
                yearly_price = stripe.Price.create(
                    unit_amount=int(self.yearly_price * 100),
                    currency="usd",
                    recurring={"interval": "year"},
                    product=product.id,
                )
                self.stripe_yearly_price_id = yearly_price.id

            # Save again to store Stripe IDs
            super().save(update_fields=['stripe_monthly_price_id', 'stripe_yearly_price_id'])


class UserSubscription(models.Model):
    BILLING_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CHOICES)
    active = models.BooleanField(default=True)
    started_at = models.DateTimeField(default=timezone.now)
    ends_at = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=255, blank=True, null=True)
    stripe_subscription_id = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        plan_name = self.plan.get_name_display() if self.plan else 'No Plan'
        return f"{self.user.email} - {plan_name} ({self.get_billing_cycle_display()})"





class Event(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    date = models.DateField()
    thumbnail = models.ImageField(upload_to='event/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, null=True)
    slug = models.SlugField(unique=True, blank=True)
    
    # New field for storing QR code image
    qr_code = models.ImageField(upload_to='event_qrcodes/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} by {self.user.email}"

    def get_invite_link(self):
        return reverse('eventadm:event_invite', kwargs={'uuid': self.uuid})

    def get_invite_url(self, request=None):
        """Return absolute URL automatically."""
        relative_url = reverse('eventadm:event_detail', kwargs={'uuid': self.uuid})
        if request:
            return request.build_absolute_uri(relative_url)
        return f"{settings.BASE_URL}{relative_url}"

    @property
    def photo_count(self):
        return self.media.filter(media_type='image').count()

    @property
    def contributor_count(self):
        return self.media.values('uploaded_by').distinct().count()

    def save(self, *args, request=None, **kwargs):
        # Generate slug if missing
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Ensure UUID exists
        if not self.uuid:
            self.uuid = uuid.uuid4()

        # Generate QR code before saving
        try:
            if request:
                invite_url = self.get_invite_url(request=request)  # with absolute URL from request
            else:
                # Fallback: use settings.BASE_URL
                if not hasattr(settings, 'BASE_URL'):
                    raise AttributeError("settings.BASE_URL is missing. Please define it in settings.py")
                invite_url = self.get_invite_url()

            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(invite_url)
            qr.make(fit=True)

            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            filename = f'qr_{self.uuid}.png'

            # Save QR code to ImageField
            self.qr_code.save(filename, ContentFile(buffer.getvalue()), save=False)
        except Exception as e:
            print(f"QR code generation failed: {e}")

        # Final save
        super().save(*args, **kwargs)



class EventInvitee(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='invitees')
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('event', 'first_name', 'last_name')

    def __str__(self):
        return f"{self.first_name} {self.last_name} for {self.event.title}"




class EventMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ('image', 'Image'),
        ('video', 'Video'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='event_media/')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)

    uploaded_by = models.ForeignKey(
        EventInvitee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='media_uploads'
    )

    uploaded_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True, blank=True)

    # New: thumbnail file
    thumbnail_file = models.FileField(
        upload_to='event_media/thumbnails/',
        blank=True,
        null=True
    )

    def __str__(self):
        if self.uploaded_by:
            return f"{self.media_type.capitalize()} by {self.uploaded_by.first_name} {self.uploaded_by.last_name}"
        return f"{self.media_type.capitalize()} (anonymous)"

    def save(self, *args, **kwargs):
        # Generate slug
        if not self.slug:
            base_slug = slugify(f"{self.event.title}-{self.media_type}")
            slug = base_slug
            counter = 1
            while EventMedia.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)  # Save original file first

        # Generate thumbnail for images
        if self.media_type == 'image' and self.file and not self.thumbnail_file:
            try:
                img = Image.open(self.file)
                img.thumbnail((480, 480))  # Resize to 480px max

                thumb_io = BytesIO()
                img.save(thumb_io, format='JPEG', quality=85)
                thumb_name = os.path.basename(self.file.name)

                self.thumbnail_file.save(
                    f"thumb_{thumb_name}",
                    ContentFile(thumb_io.getvalue()),
                    save=False
                )
                super().save(update_fields=['thumbnail_file'])
            except Exception as e:
                print(f"Thumbnail generation failed: {e}")






class SubscriptionSession(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscription_session')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    billing_cycle = models.CharField(max_length=10)  # 'monthly' or 'yearly'
    max_photos = models.PositiveIntegerField(default=0)
    max_videos = models.PositiveIntegerField(default=0)
    max_file_size_mb = models.PositiveIntegerField(default=0)

    active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        plan_name = self.plan.get_name_display() if self.plan else 'No Plan'
        return f"{self.user.email} - {plan_name} ({self.billing_cycle})"





















