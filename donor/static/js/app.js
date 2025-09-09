// ==========================
// GSAP + Locomotive Scroll Setup
// ==========================
gsap.registerPlugin(ScrollTrigger);

// Initialize Locomotive Scroll
const locoScroll = new LocomotiveScroll({
  el: document.querySelector(".main"),
  smooth: true
});

// Sync ScrollTrigger with Locomotive Scroll
locoScroll.on("scroll", ScrollTrigger.update);

// Proxy setup for ScrollTrigger (because Locomotive hijacks scroll)
ScrollTrigger.scrollerProxy(".main", {
  scrollTop(value) {
    return arguments.length
      ? locoScroll.scrollTo(value, 0, 0)
      : locoScroll.scroll.instance.scroll.y;
  },
  getBoundingClientRect() {
    return {
      top: 0,
      left: 0,
      width: window.innerWidth,
      height: window.innerHeight
    };
  },
  pinType: document.querySelector(".main").style.transform
    ? "transform"
    : "fixed"
});

// Refresh ScrollTrigger and Locomotive Scroll when window updates
ScrollTrigger.addEventListener("refresh", () => locoScroll.update());
ScrollTrigger.refresh();

// ==========================
// GSAP Animations
// ==========================
gsap.from(".hero-content", {
  y: 100,
  duration: 0.6,
  ease: "power1.inOut",
  delay: 2.2,
  opacity: 0
});

// Loader animation (uncomment if needed)
// gsap.to(".loader", {
//   y: -1000,
//   duration: 1,
//   ease: "power1.inOut",
//   delay: 2,
// });

// ==========================
// FAQ Toggle with jQuery
// ==========================
$(document).ready(function () {
  // Load previously opened FAQ from localStorage
  const openId = localStorage.getItem("openFaqId");
  if (openId) {
    const $item = $(`.faq-item[data-id="${openId}"]`);
    $item.addClass("active");
    $item.find(".faq-answer").slideDown();
  }

  // Toggle FAQ items
  $(".faq-question").on("click", function () {
    const $item = $(this).closest(".faq-item");

    // Collapse all other FAQs
    $(".faq-item").not($item).removeClass("active").find(".faq-answer").slideUp();

    // Toggle selected FAQ
    $item.toggleClass("active");
    $item.find(".faq-answer").slideToggle();

    // Save or remove state in localStorage
    if ($item.hasClass("active")) {
      localStorage.setItem("openFaqId", $item.data("id"));
      // Optional: Scroll smoothly to opened FAQ
      // $('html, body').animate({ scrollTop: $item.offset().top - 100 }, 500);
    } else {
      localStorage.removeItem("openFaqId");
    }
  });
});
