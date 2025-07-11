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

    // Mobile menu toggle
const mobileMenuButton = document.getElementById('mobile-menu-button');
const mobileNav = document.getElementById('mobile-nav');
const closeMenu = document.getElementById('close-menu');

    mobileMenuButton?.addEventListener('click', () => {
      mobileNav?.classList.remove('hidden');
      setTimeout(() => {
        mobileNav?.classList.add('opacity-100');
      }, 10);
    });

    closeMenu?.addEventListener('click', () => {
      mobileNav?.classList.add('hidden');
      mobileNav?.classList.remove('opacity-100');
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

    // Simple form handler
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        alert('Thanks for your submission! In a real implementation, your data would be processed here.');
        this.reset();
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








