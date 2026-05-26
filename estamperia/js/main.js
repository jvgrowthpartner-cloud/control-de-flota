/* ═══════════════════════════════════════════════════════
   EstampaArt — GSAP Animations & Parallax
   Requiere: gsap 3.x + ScrollTrigger
═══════════════════════════════════════════════════════ */

gsap.registerPlugin(ScrollTrigger);

/* ─────────────────────────────────────
   0. NAVBAR — scroll state
───────────────────────────────────── */
const navbar = document.getElementById('navbar');
const navToggle = document.getElementById('navToggle');
const navLinks  = document.querySelector('.nav-links');

ScrollTrigger.create({
  start: 80,
  onEnter  : () => navbar.classList.add('scrolled'),
  onLeaveBack: () => navbar.classList.remove('scrolled'),
});

navToggle.addEventListener('click', () => {
  navLinks.classList.toggle('open');
  navToggle.classList.toggle('active');
});

/* cerrar menú al hacer clic en link */
navLinks.querySelectorAll('a').forEach(a => {
  a.addEventListener('click', () => {
    navLinks.classList.remove('open');
    navToggle.classList.remove('active');
  });
});

/* ─────────────────────────────────────
   1. HERO PARALLAX — imagen se mueve
      mientras bajamos en la página
───────────────────────────────────── */
const heroImg = document.getElementById('heroImg');

if (heroImg) {
  gsap.to(heroImg, {
    yPercent: 25,          // la imagen sube 25% de su tamaño al bajar
    ease: 'none',
    scrollTrigger: {
      trigger: '.hero',
      start: 'top top',
      end: 'bottom top',
      scrub: true,         // sincronizado 1:1 con el scroll
    }
  });
}

/* Hero content — sube más rápido que la imagen (profundidad) */
const heroContent = document.getElementById('heroContent');
if (heroContent) {
  gsap.to(heroContent, {
    yPercent: -15,
    opacity: 0,
    ease: 'none',
    scrollTrigger: {
      trigger: '.hero',
      start: 'top top',
      end: '60% top',
      scrub: true,
    }
  });
}

/* ─────────────────────────────────────
   2. HERO — animación de entrada
      (al cargar la página)
───────────────────────────────────── */
const heroTL = gsap.timeline({ delay: 0.2 });

heroTL
  .from('.hero-badge', {
    opacity: 0, y: 20, duration: .6, ease: 'power3.out'
  })
  .from('.hero-title', {
    opacity: 0, y: 40, duration: .8, ease: 'power3.out'
  }, '-=0.3')
  .from('.hero-sub', {
    opacity: 0, y: 25, duration: .7, ease: 'power3.out'
  }, '-=0.4')
  .from('.hero-btns .btn', {
    opacity: 0, y: 20, stagger: .12, duration: .6, ease: 'power3.out'
  }, '-=0.3')
  .from('.hero-scroll-hint', {
    opacity: 0, y: 10, duration: .5, ease: 'power3.out'
  }, '-=0.1');

/* ─────────────────────────────────────
   3. STATS BAR — contadores animados
───────────────────────────────────── */
const statNums = document.querySelectorAll('.stat-num');

statNums.forEach(el => {
  const target = parseInt(el.dataset.target, 10);

  ScrollTrigger.create({
    trigger: el,
    start: 'top 90%',
    once: true,
    onEnter: () => {
      gsap.to({ val: 0 }, {
        val: target,
        duration: 2,
        ease: 'power2.out',
        onUpdate: function () {
          el.textContent = Math.round(this.targets()[0].val).toLocaleString('es');
        }
      });
    }
  });
});

/* ─────────────────────────────────────
   4. SERVICIOS — cards entran con stagger
───────────────────────────────────── */
gsap.utils.toArray('.servicio-card').forEach((card, i) => {
  gsap.from(card, {
    opacity: 0,
    y: 60,
    duration: .7,
    delay: parseFloat(card.dataset.delay || 0),
    ease: 'power3.out',
    scrollTrigger: {
      trigger: card,
      start: 'top 88%',
      once: true,
    }
  });
});

/* ─────────────────────────────────────
   5. GALERÍA — EFECTO PARALLAX EXPAND
      Las imágenes están sobredimensionadas
      (height: 115%) y se desplazan con el scroll
      creando un efecto de expansión suave
───────────────────────────────────── */
gsap.utils.toArray('.galeria-item').forEach(item => {
  const img   = item.querySelector('img');
  const speed = parseFloat(item.dataset.speed || 0.2);

  if (!img) return;

  /* Estado inicial: imagen ligeramente comprimida hacia arriba */
  gsap.set(img, { yPercent: -8 * speed * 10 });

  /* Parallax: al entrar al viewport la imagen se "expande" visualmente
     desplazándose verticalmente dentro de su contenedor overflow:hidden */
  gsap.to(img, {
    yPercent: 8 * speed * 10,
    ease: 'none',
    scrollTrigger: {
      trigger: item,
      start: 'top bottom',
      end: 'bottom top',
      scrub: 0.6,          /* suavizado: 0 = instantáneo, 1 = muy suave */
    }
  });

  /* Fade-in al entrar al viewport */
  gsap.from(item, {
    opacity: 0,
    scale: 0.95,
    duration: .8,
    ease: 'power3.out',
    scrollTrigger: {
      trigger: item,
      start: 'top 88%',
      once: true,
    }
  });
});

/* ─────────────────────────────────────
   6. PROCESO — pasos entran en cascada
───────────────────────────────────── */
gsap.utils.toArray('.paso').forEach((paso, i) => {
  gsap.from(paso, {
    opacity: 0,
    x: i % 2 === 0 ? -30 : 30,
    duration: .7,
    ease: 'power3.out',
    scrollTrigger: {
      trigger: paso,
      start: 'top 85%',
      once: true,
    }
  });
});

gsap.utils.toArray('.paso-connector').forEach(conn => {
  gsap.from(conn, {
    scaleX: 0,
    transformOrigin: 'left center',
    duration: .6,
    ease: 'power2.out',
    scrollTrigger: {
      trigger: conn,
      start: 'top 85%',
      once: true,
    }
  });
});

/* ─────────────────────────────────────
   7. SECTION HEADERS — entran suaves
───────────────────────────────────── */
gsap.utils.toArray('.section-header').forEach(header => {
  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: header,
      start: 'top 88%',
      once: true,
    }
  });

  tl.from(header.querySelector('.section-tag'), {
    opacity: 0, y: 16, duration: .5, ease: 'power3.out'
  })
  .from(header.querySelector('.section-title'), {
    opacity: 0, y: 24, duration: .65, ease: 'power3.out'
  }, '-=0.2')
  .from(header.querySelector('.section-sub'), {
    opacity: 0, y: 16, duration: .5, ease: 'power3.out'
  }, '-=0.2');
});

/* ─────────────────────────────────────
   8. TESTIMONIOS
───────────────────────────────────── */
gsap.utils.toArray('.testimonio-card').forEach((card, i) => {
  gsap.from(card, {
    opacity: 0,
    y: 50,
    duration: .7,
    delay: i * 0.12,
    ease: 'power3.out',
    scrollTrigger: {
      trigger: card,
      start: 'top 88%',
      once: true,
    }
  });
});

/* ─────────────────────────────────────
   9. CONTACTO — entrada split
───────────────────────────────────── */
gsap.from('.contacto-info', {
  opacity: 0,
  x: -50,
  duration: .9,
  ease: 'power3.out',
  scrollTrigger: {
    trigger: '.contacto-inner',
    start: 'top 80%',
    once: true,
  }
});

gsap.from('.contacto-form', {
  opacity: 0,
  x: 50,
  duration: .9,
  delay: .15,
  ease: 'power3.out',
  scrollTrigger: {
    trigger: '.contacto-inner',
    start: 'top 80%',
    once: true,
  }
});

/* ─────────────────────────────────────
   10. STATS BAR PARALLAX sutil
───────────────────────────────────── */
gsap.from('.stats-bar', {
  opacity: 0,
  duration: .6,
  ease: 'power2.out',
  scrollTrigger: {
    trigger: '.stats-bar',
    start: 'top 90%',
    once: true,
  }
});

/* ─────────────────────────────────────
   11. SMOOTH SCROLL para anchor links
───────────────────────────────────── */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (!target) return;
    e.preventDefault();

    const offset = parseInt(getComputedStyle(document.documentElement)
      .getPropertyValue('--nav-h')) || 72;

    gsap.to(window, {
      duration: 1,
      scrollTo: { y: target, offsetY: offset },
      ease: 'power3.inOut',
    });
  });
});

/* ─────────────────────────────────────
   12. FORMULARIO — feedback visual
───────────────────────────────────── */
const form = document.getElementById('contactForm');
if (form) {
  form.addEventListener('submit', function (e) {
    e.preventDefault();

    const btn = this.querySelector('button[type="submit"]');
    const original = btn.innerHTML;

    btn.innerHTML = '✓ ¡Solicitud enviada correctamente!';
    btn.style.background = '#22c55e';
    btn.disabled = true;

    gsap.from(btn, {
      scale: .97,
      duration: .3,
      ease: 'back.out(2)'
    });

    setTimeout(() => {
      btn.innerHTML = original;
      btn.style.background = '';
      btn.disabled = false;
      form.reset();
    }, 3500);
  });
}

/* ─────────────────────────────────────
   13. SCROLL TO PLUGIN (fallback)
       Si no está disponible gsap.to(window,scrollTo)
───────────────────────────────────── */
if (!gsap.plugins || !gsap.plugins.scrollTo) {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
      const target = document.querySelector(this.getAttribute('href'));
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
  });
}

/* ─────────────────────────────────────
   Refresh ScrollTrigger tras cargar imgs
───────────────────────────────────── */
window.addEventListener('load', () => {
  ScrollTrigger.refresh();
});
