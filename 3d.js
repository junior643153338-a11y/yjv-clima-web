(function () {
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var rig = document.querySelector('.rig3d');
  if (rig && !reduce) {
    var set = function (x, y) {
      rig.style.setProperty('--ry', (-24 + x * 30).toFixed(1) + 'deg');
      rig.style.setProperty('--rx', (-12 - y * 16).toFixed(1) + 'deg');
    };
    window.addEventListener('pointermove', function (e) {
      set(e.clientX / innerWidth - 0.5, e.clientY / innerHeight - 0.5);
    }, { passive: true });
    window.addEventListener('deviceorientation', function (e) {
      if (e.gamma == null) return;
      set(Math.max(-1, Math.min(1, e.gamma / 30)) / 2, Math.max(-1, Math.min(1, (e.beta - 45) / 30)) / 2);
    }, { passive: true });
  }
  if ('IntersectionObserver' in window && !reduce) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.01, rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll('section:not(.hero), .trust').forEach(function (el) { el.classList.add('reveal3d'); io.observe(el); });
  }
})();
