$(document).ready(function(){
    $('.owl-carousel').owlCarousel({
      items: 1,
      loop: true,
      autoplay: true,
      autoplayTimeout: 6000,
      smartSpeed: 1000,
      nav: false,
      animateOut: 'fadeOut'
    });
});




// Lightbox functions - make them globally accessible
function openLightbox(src) {
    const lightboxModal = document.getElementById('lightboxModal');
    const lightboxImage = document.getElementById('lightboxImage');
    lightboxImage.src = src;

    // Ensure image sizing is responsive and object-fit is applied
    lightboxImage.style.maxHeight = '90vh';
    lightboxImage.style.maxWidth = '100%';
    lightboxImage.style.objectFit = 'contain'; // ensures whole image is visible
    lightboxImage.style.width = 'auto';
    lightboxImage.style.height = 'auto';

    lightboxModal.classList.remove('hidden');
}

function closeLightbox() {
    const lightboxModal = document.getElementById('lightboxModal');
    lightboxModal.classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', function () {
    // Owl Carousel - Testimonial Slider
    $('.testimonial-slider').owlCarousel({
      loop: true,
      margin: 30,
      dots: false,
      autoplay: true,
      autoplayTimeout: 5000,
      responsive: {
        0: { items: 1 },
        768: { items: 2 },
        1024: { items: 3 }
      }
});

const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileNav = document.getElementById('mobile-nav');
const closeMenu = document.getElementById('close-menu');

// Open mobile nav
mobileMenuButton?.addEventListener('click', () => {
    mobileNav?.classList.remove('hidden');
    setTimeout(() => {
        mobileNav?.classList.add('opacity-100');
        mobileNav?.classList.remove('opacity-0');
    }, 10);
});

// Close mobile nav
closeMenu?.addEventListener('click', () => {
    mobileNav?.classList.remove('opacity-100');
    mobileNav?.classList.add('opacity-0');
    
    // Wait for transition to finish before hiding
    setTimeout(() => {
        mobileNav?.classList.add('hidden');
    }, 300); // Match your CSS duration
});



    // Back to top button
    const backToTopButton = document.getElementById('back-to-top');
    window.addEventListener('scroll', () => {
      if (window.pageYOffset > 500) {
        backToTopButton.classList.remove('opacity-0', 'invisible');
        backToTopButton.classList.add('opacity-100', 'visible');
      } else {
        backToTopButton.classList.remove('opacity-100', 'visible');
        backToTopButton.classList.add('opacity-0', 'invisible');
      }
    });

    backToTopButton?.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href'))?.scrollIntoView({ behavior: 'smooth' });
        mobileNav?.classList.add('hidden');
      });
    });


    // FAQ Accordion
    document.querySelectorAll('.faq-item').forEach(item => {
      const question = item.querySelector('[onclick^="toggleFAQ"]');
      const targetId = question?.getAttribute('onclick')?.match(/'([^']+)'/)?.[1];
      const content = document.getElementById(`${targetId}-content`);
      const icon = document.getElementById(`${targetId}-icon`);

      if (content) content.style.maxHeight = '0';

      if (question) {
        question.onclick = (e) => {
          e.preventDefault();
          const isExpanding = !content.style.maxHeight || content.style.maxHeight === '0px';

          document.querySelectorAll('.faq-content').forEach(otherContent => {
            if (otherContent.id !== `${targetId}-content`) {
              otherContent.style.maxHeight = '0';
              const otherIconId = otherContent.id.replace('-content', '-icon');
              document.getElementById(otherIconId)?.classList.remove('rotate-180');
            }
          });

          if (isExpanding) {
            content.style.maxHeight = content.scrollHeight + 'px';
            icon?.classList.add('rotate-180');
          } else {
            content.style.maxHeight = '0';
            icon?.classList.remove('rotate-180');
          }
        };
      }
    });

    // Close lightbox when clicking outside the image
    const lightboxModal = document.getElementById('lightboxModal');
    lightboxModal?.addEventListener('click', function (e) {
      if (e.target.id === 'lightboxModal') closeLightbox();
    });
  });





  // Back to top button logic
const backToTopButton = document.getElementById('back-to-top');

window.addEventListener('scroll', () => {
  if (window.pageYOffset > 300) {
    backToTopButton.classList.remove('opacity-0', 'invisible');
    backToTopButton.classList.add('opacity-100', 'visible');
  } else {
    backToTopButton.classList.remove('opacity-100', 'visible');
    backToTopButton.classList.add('opacity-0', 'invisible');
  }
});

backToTopButton?.addEventListener('click', () => {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});







    
document.addEventListener("DOMContentLoaded", function () {
    const toggle = document.getElementById("billingToggle");
    const toggleWrapper = document.getElementById("toggleWrapper");
    const monthlyPrices = document.querySelectorAll(".price-monthly");
    const yearlyPrices = document.querySelectorAll(".price-yearly");
    const billingCycleLabels = document.querySelectorAll(".billing-cycle");

    yearlyPrices.forEach(el => {
        const price = parseFloat(el.textContent.replace('$', '').trim());
        const discounted = (price * 0.9).toFixed(2);
        el.textContent = `$${discounted}`;
    });

    function updatePrices() {
        const isYearly = toggle.checked;
        monthlyPrices.forEach(el => el.classList.toggle("hidden", isYearly));
        yearlyPrices.forEach(el => el.classList.toggle("hidden", !isYearly));
        billingCycleLabels.forEach(el => el.textContent = isYearly ? "year" : "month");
        toggleWrapper.classList.toggle("checked", isYearly);
    }

    toggle.addEventListener("change", updatePrices);
    toggle.checked = false;
    updatePrices();

    // Bind click handlers to all "Get Started" buttons
    document.querySelectorAll("button").forEach(button => {
        button.addEventListener("click", async function () {
            const planCard = this.closest("[data-plan-id]");
            const planId = planCard.getAttribute("data-plan-id");
            const billingCycle = toggle.checked ? "yearly" : "monthly";

            const response = await fetch("{% url 'eventadm:create_checkout_session' %}", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                    "X-CSRFToken": "{{ csrf_token }}",
                },
                body: new URLSearchParams({
                    plan_id: planId,
                    billing_cycle: billingCycle
                })
            });

            const data = await response.json();

            if (response.ok && data.sessionId) {
                const stripe = Stripe("{{ STRIPE_PUBLIC_KEY }}");
                stripe.redirectToCheckout({ sessionId: data.sessionId });
            } else {
                alert("Error creating checkout session");
            }
        });
    });
});















// JavaScript for handling event modals in the admin panel
function openEditModal(slug, title, date, description, location) {
  console.log('openEditModal called with:', slug, title, date, description, location);

  document.getElementById('edit_event_slug').value = slug;
  document.getElementById('edit_title').value = title;
  document.getElementById('edit_date').value = date;
  document.getElementById('edit_description').value = description;
  document.getElementById('edit_location').value = location;

  document.getElementById('editEventModal').classList.remove('hidden');
}







// Function to open the edit modal and populate data
function openEditModal(eventData) {
  const modal = document.getElementById('editEventModal');
  modal.classList.remove('hidden');

  // Populate form fields
  document.getElementById('edit_event_slug').value = eventData.slug;
  document.getElementById('edit_title').value = eventData.title;
  document.getElementById('edit_date').value = eventData.date;
  document.getElementById('edit_description').value = eventData.description || '';
  document.getElementById('edit_location').value = eventData.location || '';
  // Note: File input cannot be populated for security reasons, user must re-upload if desired
}

// Close modal function
function closeEditModal() {
  const modal = document.getElementById('editEventModal');
  modal.classList.add('hidden');
  // Clear form if needed
  document.getElementById('editEventForm').reset();
}

// Close modal if clicked outside the modal content
document.getElementById('editEventModal').addEventListener('click', function(e) {
  if (e.target === this) {
    closeEditModal();
  }
});









function openEditModal(eventSlug, title, date, description, location) {
  // Show modal
  const modal = document.getElementById('editEventModal');
  modal.classList.remove('hidden');

  // Fill in the form fields with data
  document.getElementById('edit_event_slug').value = eventSlug;
  document.getElementById('edit_title').value = title;
  document.getElementById('edit_date').value = date;
  document.getElementById('edit_description').value = description || '';
  document.getElementById('edit_location').value = location || '';
  
  // Clear thumbnail input (file inputs cannot be prefilled for security reasons)
  document.getElementById('edit_thumbnail').value = '';
}

function closeEditModal() {
  const modal = document.getElementById('editEventModal');
  modal.classList.add('hidden');
}

// Optional: Close modal if click outside content area
document.getElementById('editEventModal').addEventListener('click', function(e) {
  if (e.target === this) {
    closeEditModal();
  }
});











