import stripe
import json, traceback
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseNotFound
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseServerError, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import subscription_required
from django.urls import reverse
from django.views.decorators.http import require_GET
from django.views.decorators.http import require_POST
from .forms import *
from django.contrib import messages
from django.db.models import Count, Q
# Create your views here.

stripe.api_key = settings.STRIPE_SECRET_KEY


from django.db.models import Sum, Case, When, IntegerField
from users.models import CustomUser






@login_required
@subscription_required
def admin(request):
    user = request.user
    plans = SubscriptionPlan.objects.all().order_by('-id')
    events = Event.objects.filter(user=user)
    event_count = events.count()

    # Generate invite URLs for each event (optional, for display)
    for event in events:
        event.invite_url = event.get_invite_url(request)

    # Trial info
    trial = getattr(user, 'trial', None)
    trial_days_left = None
    if trial and trial.is_active:
        trial_days_left = (trial.end_date - timezone.now()).days

    # Total photos + videos for all user's events
    total_media = EventMedia.objects.filter(event__user=user).aggregate(
        total_photos=Sum(Case(
            When(media_type='image', then=1),
            default=0,
            output_field=IntegerField()
        )),
        total_videos=Sum(Case(
            When(media_type='video', then=1),
            default=0,
            output_field=IntegerField()
        ))
    )
    total_photos = total_media['total_photos'] or 0
    total_videos = total_media['total_videos'] or 0
    total_media_count = total_photos + total_videos

    # Total unique contributors (invitees) of the user's events
    total_contributors = EventInvitee.objects.filter(event__user=user).distinct().count()

    if request.method == 'POST':
        if "event_slug" in request.POST:
            slug = request.POST["event_slug"]
            event = get_object_or_404(Event, slug=slug, user=user)

            # Update Event
            if "title" in request.POST:
                form = EventForm(request.POST, request.FILES, instance=event)
                if form.is_valid():
                    event = form.save(commit=False)
                    event.user = user
                    event.save(request=request)  # pass request for QR code
                    messages.success(request, "Event updated successfully.")
                    return redirect('eventadm:admin')

            # Delete Event
            elif "event_slug" in request.POST and not request.FILES:
                event.delete()
                messages.success(request, "Event deleted successfully.")
                return redirect('eventadm:admin')

        else:
            # Create Event
            form = EventForm(request.POST, request.FILES)
            if form.is_valid():
                event = form.save(commit=False)
                event.user = user
                event.save(request=request)  # pass request for QR code
                messages.success(request, "Event created successfully.")
                return redirect('eventadm:admin')
    else:
        form = EventForm()

    return render(request, 'eventsharer_admin/admin.html', {
        'plan': plans,
        'events': events,  # Keep Event objects intact with their properties
        'form': form,
        'event_count': event_count,
        'trial': trial,
        'trial_days_left': trial_days_left,
        'total_videos': total_videos,
        'total_media_count': total_media_count,
        'total_contributors': total_contributors,
    })



@login_required
def edit_event(request, slug):
    event = get_object_or_404(Event, slug=slug, user=request.user)

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('eventadm:admin')  # or wherever you want to go
    else:
        form = EventForm(instance=event)

    return render(request, 'eventsharer_admin/partials/edit_event.html', {
        'form': form,
        'event': event,
    })






@login_required
def delete_event(request, slug):
    event = get_object_or_404(Event, slug=slug, user=request.user)

    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('eventadm:admin')  # Redirect wherever appropriate

    # Optionally, if you want to show a confirmation page before deletion,
    # render a template here instead of deleting immediately.
    # For now, we just redirect if method is not POST.
    messages.error(request, 'Invalid request method.')
    return redirect('eventadm:admin')




def event_detail(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)

    # Check if current user is the owner of the event
    is_owner = request.user.is_authenticated and (event.user == request.user)

    # Check for invitee cookie (invitee_id stored in cookie)
    invitee_id = request.COOKIES.get(f'event_{event.id}_invitee_id')
    invitee = None
    show_invitee_form = False

    if invitee_id:
        try:
            invitee = EventInvitee.objects.get(id=invitee_id, event=event)
        except EventInvitee.DoesNotExist:
            invitee = None

    # Show invitee popup if NOT owner and no valid invitee cookie
    if not is_owner and not invitee:
        show_invitee_form = True

    if request.method == 'POST':
        # Handle invitee registration form submission
        if 'first_name' in request.POST and 'last_name' in request.POST and not invitee:
            first_name = request.POST['first_name'].strip()
            last_name = request.POST['last_name'].strip()
            if first_name and last_name:
                # Create or get existing invitee for this event & name
                invitee, created = EventInvitee.objects.get_or_create(
                    event=event,
                    first_name=first_name,
                    last_name=last_name
                )
                response = JsonResponse({'success': True})
                # Set cookie to expire in 48 hours
                response.set_cookie(f'event_{event.id}_invitee_id', invitee.id, max_age=172800)
                return response
            else:
                return JsonResponse({'success': False, 'error': 'Both first and last name are required.'})

        # Handle media upload POST (file upload)
        if 'file' in request.FILES:
            if not (is_owner or invitee):
                # Unauthorized upload attempt
                return JsonResponse({'success': False, 'error': 'You must be an invitee or owner to upload.'})

            uploaded_file = request.FILES['file']

            # Determine media_type by file content-type or extension
            if uploaded_file.content_type.startswith('image'):
                media_type = 'image'
            elif uploaded_file.content_type.startswith('video'):
                media_type = 'video'
            else:
                return JsonResponse({'success': False, 'error': 'Unsupported file type.'})

            # Save the media object linked to the event
            media_obj = EventMedia.objects.create(
                event=event,
                file=uploaded_file,
                media_type=media_type,
                uploaded_by=invitee if invitee else None  # Owners are not stored as invitee
            )

            # Prepare response data to update UI
            if invitee:
                first_name = invitee.first_name
                last_name = invitee.last_name
            elif is_owner:
                first_name = event.user.first_name
                last_name = event.user.last_name
            else:
                first_name = 'anonymous'
                last_name = ''

            media_data = {
                'id': media_obj.id,
                'file_url': media_obj.file.url,
                'media_type': media_obj.media_type,
                'uploaded_at': media_obj.uploaded_at.strftime('%b %d, %Y'),
                'uploaded_by_first_name': first_name,
                'uploaded_by_last_name': last_name,
            }
            return JsonResponse({'success': True, 'media': media_data})

    # Get all media for the event, ordered newest first
    media = event.media.all().order_by('-uploaded_at')

    context = {
        'event': event,
        'media': media,
        'show_invitee_form': show_invitee_form,
        'is_owner': is_owner,
    }

    return render(request, 'eventsharer_admin/album_detail.html', context)












 

def event_invite(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    token = request.COOKIES.get('invitee_token')

    invitee = None
    if token:
        invitee = EventInvitee.objects.filter(event=event, token=token).first()

    if invitee:
        # Invitee recognized, show event details or upload form, no name form
        context = {'event': event, 'invitee': invitee, 'identified': True}
        return render(request, 'eventsharer_admin/event_invite.html', context)

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if first_name and last_name:
            invitee, created = EventInvitee.objects.get_or_create(
                event=event,
                first_name=first_name,
                last_name=last_name,
            )
            response = HttpResponseRedirect(request.path)
            response.set_cookie('invitee_token', str(invitee.token), max_age=60*60*24*30)  # 30 days
            return response

        # If invalid, fall through and show form again with errors (optional)

    # No token or invitee -> show form
    context = {'event': event, 'identified': False}
    return render(request, 'eventsharer_admin/event_invite.html', context)


















@login_required
def subscription_plans(request):
    plans = SubscriptionPlan.objects.all().order_by('id')
    return render(request, 'eventsharer_admin/plan_list.html', {
        'plans': plans,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
    })






@login_required
@require_POST
def create_checkout_session(request):
    print("POST data:", request.POST)

    plan_id = request.POST.get('plan_id')
    billing_cycle = request.POST.get('billing_cycle')

    print(f"Plan ID: {plan_id}, Billing Cycle: {billing_cycle}")

    try:
        plan = SubscriptionPlan.objects.get(id=plan_id)

        # Choose correct Stripe price ID
        price_id = plan.stripe_monthly_price_id if billing_cycle == 'monthly' else plan.stripe_yearly_price_id
        if not price_id:
            return JsonResponse({"error": "Stripe price ID is missing."}, status=400)

        # Build absolute success/cancel URLs
        success_url = request.build_absolute_uri(
            reverse('eventadm:checkout_success')
        ) + '?session_id={CHECKOUT_SESSION_ID}'  # Important!
        cancel_url = request.build_absolute_uri(reverse('eventadm:checkout_cancel'))

        # Create Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=success_url,
            cancel_url=cancel_url,
            metadata={
                'user_id': request.user.id,
                'plan_id': str(plan.id),
                'billing_cycle': billing_cycle,
            }
        )

        return JsonResponse({'sessionId': checkout_session.id})

    except SubscriptionPlan.DoesNotExist:
        return JsonResponse({"error": "Invalid plan"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)






@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        print("✅ Webhook received:", event['type'])

    except Exception as e:
        print("❌ Signature verification failed:", traceback.format_exc())
        return JsonResponse({"error": "Invalid signature"}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        print("✅ Checkout Session Completed:", session)

        try:
            user_id = session['metadata']['user_id']
            plan_id = session['metadata']['plan_id']
            billing_cycle = session['metadata']['billing_cycle']
            subscription_id = session.get('subscription')
            customer_id = session.get('customer')

            User = get_user_model()
            user = User.objects.get(id=user_id)
            plan = SubscriptionPlan.objects.get(id=plan_id)

            # Save user subscription
            UserSubscription.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'stripe_customer_id': customer_id,
                    'stripe_subscription_id': subscription_id,
                    'active': True,
                    'started_at': now(),
                    'ends_at': None,
                }
            )

            # Apply limits
            PLAN_LIMITS = {
                'basic': {'max_photos': 5, 'max_videos': 1, 'max_file_size_mb': 20},
                'pro': {'max_photos': 50, 'max_videos': 5, 'max_file_size_mb': 100},
                'business': {'max_photos': 500, 'max_videos': 50, 'max_file_size_mb': 250},
            }

            limits = PLAN_LIMITS.get(plan.name.lower(), {})
            SubscriptionSession.objects.update_or_create(
                user=user,
                defaults={
                    'plan': plan,
                    'billing_cycle': billing_cycle,
                    'max_photos': limits.get('max_photos', 0),
                    'max_videos': limits.get('max_videos', 0),
                    'max_file_size_mb': limits.get('max_file_size_mb', 0),
                    'active': True,
                }
            )

            print("✅ Subscription updated for user:", user.email)

        except Exception as e:
            print("❌ Error processing session:", traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=500)

    return HttpResponse(status=200)







@login_required
@require_GET
def checkout_success(request):
    session_id = request.GET.get('session_id')
    if not session_id:
        return HttpResponseBadRequest("Missing session ID.")

    try:
        session = stripe.checkout.Session.retrieve(session_id)
        subscription_id = session.get('subscription')
        customer_id = session.get('customer')
        metadata = session.get('metadata', {})

        plan_id = metadata.get('plan_id')
        billing_cycle = metadata.get('billing_cycle')
        user_id = metadata.get('user_id')

        if str(request.user.id) != str(user_id):
            return HttpResponseForbidden("User mismatch.")

        plan = SubscriptionPlan.objects.get(id=plan_id)

        # Save subscription
        UserSubscription.objects.update_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'billing_cycle': billing_cycle,
                'stripe_customer_id': customer_id,
                'stripe_subscription_id': subscription_id,
                'active': True,
                'started_at': now(),
                'ends_at': None,
            }
        )

        # Apply plan limits directly from SubscriptionPlan
        SubscriptionSession.objects.update_or_create(
            user=request.user,
            defaults={
                'plan': plan,
                'billing_cycle': billing_cycle,
                'max_photos': plan.max_photos or 0,
                'max_videos': plan.max_videos or 0,
                'max_file_size_mb': plan.max_file_size_mb or 0,
                'active': True,
            }
        )

        print("✅ Subscription successfully registered via checkout_success.")
        return render(request, 'eventsharer_adm/success.html')

    except Exception as e:
        print("❌ Error during checkout_success:", traceback.format_exc())
        return HttpResponseServerError("Something went wrong.")



@login_required
def checkout_cancel(request):
    return render(request, 'eventsharer_admin/cancel.html')










