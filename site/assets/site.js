/* Minimal replacement for the Squarespace (Bedford template) runtime. */
(function () {
  var body = document.body;
  var header = document.getElementById('header');
  var mainNav = document.getElementById('mainNavigation');

  /* --- Mobile navigation: build the sidecar menu from the main nav --- */
  if (mainNav && !document.getElementById('sidecarNav')) {
    var sidecar = document.createElement('div');
    sidecar.id = 'sidecarNav';
    var nav = document.createElement('nav');
    nav.innerHTML = mainNav.innerHTML;
    var acct = nav.querySelector('.user-account-link'); if (acct) acct.remove();
    sidecar.appendChild(nav);
    body.appendChild(sidecar);
    var overlay = document.createElement('div');
    overlay.className = 'body-overlay';
    body.appendChild(overlay);
    overlay.addEventListener('click', function () { body.classList.remove('mobile-nav-open'); });
  }
  document.querySelectorAll('.mobile-nav-toggle').forEach(function (t) {
    t.addEventListener('click', function () { body.classList.toggle('mobile-nav-open'); });
  });

  function checkNavFit() {
    var wasOpen = body.classList.contains('mobile-nav-open');
    body.classList.remove('force-mobile-nav');
    var force = window.innerWidth <= 640;
    if (!force && header) {
      var inner = header.querySelector('.header-inner');
      var logo = document.getElementById('logoWrapper');
      var headerNav = document.getElementById('headerNav');
      if (inner && logo && headerNav) {
        var navW = 0; mainNav.querySelectorAll(':scope > div').forEach(function (d) { navW += d.getBoundingClientRect().width; });
        var logoW = logo.offsetWidth, avail = inner.clientWidth;
        if (logoW + navW + 40 > avail) force = true;
      }
    }
    if (force) body.classList.add('force-mobile-nav'); else body.classList.remove('mobile-nav-open');
    if (force && wasOpen) body.classList.add('mobile-nav-open');
  }
  checkNavFit();
  window.addEventListener('resize', checkNavFit);
  window.addEventListener('load', checkNavFit);

  /* --- Sticky header that appears once the banner has scrolled away --- */
  if (header && header.classList.contains('show-on-scroll')) {
    var wrapper = document.createElement('div');
    wrapper.className = 'show-on-scroll-wrapper';
    var clone = header.cloneNode(true);
    clone.classList.remove('show-on-scroll');
    wrapper.appendChild(clone);
    body.appendChild(wrapper);
    clone.querySelectorAll('.mobile-nav-toggle').forEach(function (t) {
      t.addEventListener('click', function () { body.classList.toggle('mobile-nav-open'); });
    });
    var offsetSel = header.getAttribute('data-offset-el') || '.banner-thumbnail-wrapper';
    function onScroll() {
      var el = document.querySelector(offsetSel) || document.querySelector('.banner-thumbnail-wrapper');
      var threshold = el ? el.getBoundingClientRect().bottom + window.scrollY : 300;
      if (window.scrollY > threshold - 50) wrapper.classList.add('show'); else wrapper.classList.remove('show');
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  /* --- Focal points for cover images --- */
  document.querySelectorAll('img[data-image-focal-point]').forEach(function (img) {
    var fp = img.getAttribute('data-image-focal-point').split(',');
    if (fp.length === 2) img.style.setProperty('--focal', (parseFloat(fp[0]) * 100) + '% ' + (parseFloat(fp[1]) * 100) + '%');
  });
})();

/* Videos page: swap a thumbnail for the YouTube player when clicked */
document.querySelectorAll('.video-item[data-yt]').forEach(function (item) {
  item.addEventListener('click', function () {
    var id = item.getAttribute('data-yt');
    item.innerHTML = '<iframe src="https://www.youtube.com/embed/' + id + '?autoplay=1&rel=0" title="YouTube video" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe>';
    item.removeAttribute('data-yt');
  }, { once: true });
});
