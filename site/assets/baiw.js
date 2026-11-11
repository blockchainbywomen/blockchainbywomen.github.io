/* blockch[AI]n by women: menu, click-to-play videos, self-sizing quiz frames */
(function () {
  var menu = document.querySelector('.bw-menu');
  var nav = document.getElementById('bw-nav');
  if (menu && nav) {
    menu.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      menu.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  document.querySelectorAll('.bw-play[data-yt]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var frame = document.createElement('iframe');
      frame.src = 'https://www.youtube.com/embed/' + btn.getAttribute('data-yt') + '?autoplay=1&rel=0';
      frame.title = btn.getAttribute('aria-label') || 'YouTube video';
      frame.allow = 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen';
      frame.allowFullscreen = true;
      btn.replaceWith(frame);
    });
  });

  /* A link such as education/#v-<id> lands on a video card: make it obvious which one */
  function mark() {
    var el = location.hash.indexOf('#v-') === 0 && document.getElementById(location.hash.slice(1));
    document.querySelectorAll('.bw-video.target').forEach(function (v) { v.classList.remove('target'); });
    if (el) el.classList.add('target');
  }
  window.addEventListener('hashchange', mark);
  mark();

  /* The quizzes live in their own small pages; grow each frame to fit its content */
  document.querySelectorAll('iframe.bw-embed').forEach(function (frame) {
    function fit() {
      try {
        var doc = frame.contentDocument;
        if (!doc || !doc.body) return;
        var box = doc.body.firstElementChild || doc.body;
        frame.style.height = Math.ceil(box.getBoundingClientRect().height + 80) + 'px';
      } catch (e) { /* different origin: keep the default height */ }
    }
    frame.addEventListener('load', function () {
      fit();
      try {
        new ResizeObserver(fit).observe(frame.contentDocument.body.firstElementChild || frame.contentDocument.body);
        frame.contentDocument.addEventListener('click', function () { setTimeout(fit, 60); });
      } catch (e) {}
    });
    fit();
  });
})();
