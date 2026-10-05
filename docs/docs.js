/* jddavenport.com/docs: site nav, docs drawer, copy buttons, on-this-page highlight, search.
   Source: tools/docs/assets/docs.js. Copied to docs/docs.js by tools/docs/build.py. No dependencies. */
(function () {
  'use strict';
  var d = document, root = d.documentElement;

  /* Site nav toggle (same behavior as the homepage) */
  var navBtn = d.getElementById('navToggle'), nav = d.getElementById('siteNav');
  if (navBtn && nav) {
    navBtn.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      navBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) { nav.classList.remove('open'); navBtn.setAttribute('aria-expanded', 'false'); }
    });
  }

  /* Docs drawer (narrow screens) */
  var menuBtn = d.getElementById('docsMenuBtn'), sidebar = d.getElementById('docsSidebar'),
      overlay = d.getElementById('drawerOverlay'), closeBtn = d.getElementById('drawerClose');
  function setDrawer(open) {
    if (!menuBtn || !sidebar) return;
    root.classList.toggle('drawer-open', open);
    menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (overlay) overlay.hidden = !open;
    if (open) {
      var cur = sidebar.querySelector('[aria-current="page"]');
      if (cur) cur.scrollIntoView({ block: 'center' });
      (closeBtn || sidebar).focus({ preventScroll: true });
    } else {
      menuBtn.focus({ preventScroll: true });
    }
  }
  if (menuBtn && sidebar) {
    menuBtn.addEventListener('click', function () { setDrawer(!root.classList.contains('drawer-open')); });
    if (overlay) overlay.addEventListener('click', function () { setDrawer(false); });
    if (closeBtn) closeBtn.addEventListener('click', function () { setDrawer(false); });
    sidebar.addEventListener('click', function (e) {
      var a = e.target.closest('a');
      if (a && root.classList.contains('drawer-open')) {
        root.classList.remove('drawer-open');
        if (overlay) overlay.hidden = true;
        menuBtn.setAttribute('aria-expanded', 'false');
      }
    });
    try {
      window.matchMedia('(min-width: 900px)').addEventListener('change', function (m) {
        if (m.matches && root.classList.contains('drawer-open')) setDrawer(false);
      });
    } catch (err) { /* old Safari: no MediaQueryList.addEventListener */ }
  }
  d.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      if (root.classList.contains('drawer-open')) setDrawer(false);
      if (nav && nav.classList.contains('open')) { nav.classList.remove('open'); navBtn.setAttribute('aria-expanded', 'false'); }
    }
  });

  /* Copy buttons */
  function copyText(text) {
    if (navigator.clipboard && window.isSecureContext) return navigator.clipboard.writeText(text);
    return new Promise(function (res, rej) {
      var ta = d.createElement('textarea');
      ta.value = text; ta.setAttribute('readonly', ''); ta.style.position = 'fixed'; ta.style.opacity = '0';
      d.body.appendChild(ta); ta.select();
      try { d.execCommand('copy') ? res() : rej(); } catch (err) { rej(err); }
      d.body.removeChild(ta);
    });
  }
  Array.prototype.forEach.call(d.querySelectorAll('.copy-btn'), function (btn) {
    btn.hidden = false;
    btn.addEventListener('click', function () {
      var code = btn.closest('.code-block').querySelector('code');
      copyText(code.textContent).then(function () {
        btn.textContent = 'Copied'; btn.classList.add('copied');
      }, function () { btn.textContent = 'Select and copy'; })
        .then(function () { setTimeout(function () { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 1600); });
    });
  });

  /* On this page: highlight the section in view */
  var tocLinks = d.querySelectorAll('.docs-toc a');
  if (tocLinks.length && 'IntersectionObserver' in window) {
    var map = {}, heads = [];
    Array.prototype.forEach.call(tocLinks, function (a) {
      var h = d.getElementById(decodeURIComponent(a.getAttribute('href').slice(1)));
      if (h) { map[h.id] = a; heads.push(h); }
    });
    var visible = {};
    var setActive = function () {
      var current = null;
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top < 140) current = heads[i]; else break;
      }
      if (!current) current = heads[0];
      Array.prototype.forEach.call(tocLinks, function (a) { a.classList.toggle('active', map[current.id] === a); });
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { visible[en.target.id] = en.isIntersecting; });
      setActive();
    }, { rootMargin: '-80px 0px -60% 0px' });
    heads.forEach(function (h) { io.observe(h); });
    window.addEventListener('scroll', function () { window.requestAnimationFrame(setActive); }, { passive: true });
  }

  /* Search: client-side, no library. Every query word must match somewhere;
     title and heading matches outrank body text; a one-letter typo still matches. */
  var boxes = d.querySelectorAll('[data-search]');
  if (!boxes.length) return;
  var index = null, loading = null;
  function norm(s) { return (s || '').toLowerCase().normalize('NFKD').replace(/[̀-ͯ]/g, ''); }
  function words(s) { return norm(s).split(/[^a-z0-9]+/).filter(Boolean); }
  function load() {
    if (index) return Promise.resolve(index);
    if (loading) return loading;
    loading = fetch('/docs/search-index.json').then(function (r) { return r.json(); }).then(function (docs) {
      index = docs.map(function (doc) {
        var heads = (doc.headings || []).join(' ');
        return {
          doc: doc,
          t: norm(doc.title), tw: words(doc.title),
          h: norm(heads), hw: words(heads),
          o: norm(doc.description + ' ' + doc.section + ' ' + (doc.group || '')),
          ow: words(doc.description + ' ' + doc.section + ' ' + (doc.group || '')),
          x: norm(doc.text)
        };
      });
      return index;
    });
    return loading;
  }
  function near(a, b) { /* edit distance <= 1 */
    if (Math.abs(a.length - b.length) > 1) return false;
    var i = 0, j = 0, edits = 0;
    while (i < a.length && j < b.length) {
      if (a[i] === b[j]) { i++; j++; continue; }
      if (++edits > 1) return false;
      if (a.length > b.length) i++; else if (b.length > a.length) j++; else { i++; j++; }
    }
    return edits + (a.length - i) + (b.length - j) <= 1;
  }
  function wordScore(list, q, exact, prefix) {
    var best = 0;
    for (var i = 0; i < list.length; i++) {
      var w = list[i];
      if (w === q) return exact;
      if (w.indexOf(q) === 0) best = Math.max(best, prefix);
    }
    return best;
  }
  function score(e, q, terms) {
    var total = 0;
    for (var k = 0; k < terms.length; k++) {
      var t = terms[k];
      var s = Math.max(
        wordScore(e.tw, t, 12, 9), e.t.indexOf(t) >= 0 ? 6 : 0,
        wordScore(e.hw, t, 6, 5), e.h.indexOf(t) >= 0 ? 3 : 0,
        wordScore(e.ow, t, 4, 3), e.o.indexOf(t) >= 0 ? 2 : 0,
        e.x.indexOf(t) >= 0 ? 1 : 0);
      if (!s && t.length >= 4) {
        var pool = e.tw.concat(e.hw, e.ow);
        for (var i = 0; i < pool.length; i++) {
          if (near(pool[i], t) || (pool[i].length > t.length && near(pool[i].slice(0, t.length), t))) {
            s = pool[i] && e.tw.indexOf(pool[i]) >= 0 ? 4 : 2; break;
          }
        }
      }
      if (!s) return 0;
      total += s;
    }
    if (e.t.indexOf(q) >= 0) total += 10;
    else if (e.h.indexOf(q) >= 0) total += 4;
    if (e.doc.section === 'Section') total -= 1;
    return total;
  }
  function search(q) {
    var nq = norm(q).trim(), terms = words(q);
    if (!terms.length) return [];
    return index.map(function (e) { return { e: e, s: score(e, nq, terms) }; })
      .filter(function (r) { return r.s > 0; })
      .sort(function (a, b) { return b.s - a.s || a.e.doc.title.localeCompare(b.e.doc.title); })
      .slice(0, 8).map(function (r) { return r.e.doc; });
  }

  Array.prototype.forEach.call(boxes, function (box) {
    box.hidden = false;
    var input = box.querySelector('input'), list = box.querySelector('.search-results'),
        status = box.querySelector('.search-status'), active = -1, results = [];
    function close() { list.hidden = true; input.setAttribute('aria-expanded', 'false'); active = -1; }
    function mark() {
      Array.prototype.forEach.call(list.children, function (li, i) {
        li.setAttribute('aria-selected', i === active ? 'true' : 'false');
        if (i === active) li.scrollIntoView({ block: 'nearest' });
      });
    }
    function render() {
      var q = input.value;
      if (!q.trim()) { close(); list.innerHTML = ''; return; }
      load().then(function () {
        if (input.value !== q) return;
        results = search(q); active = results.length ? 0 : -1;
        list.innerHTML = '';
        if (!results.length) {
          var li = d.createElement('li'); li.className = 'sr-empty'; li.textContent = 'Nothing matches "' + q.trim() + '".';
          list.appendChild(li);
        }
        results.forEach(function (doc, i) {
          var li = d.createElement('li'), a = d.createElement('a');
          li.setAttribute('role', 'option'); li.id = input.id + '-opt-' + i;
          a.href = doc.url; a.tabIndex = -1;
          var t = d.createElement('span'); t.className = 'sr-title'; t.textContent = doc.title;
          var m = d.createElement('span'); m.className = 'sr-meta'; m.textContent = doc.section === 'Section' ? 'Section' : doc.section + (doc.group ? ' · ' + doc.group : '');
          var ds = d.createElement('span'); ds.className = 'sr-desc'; ds.textContent = doc.description;
          a.appendChild(t); a.appendChild(m); a.appendChild(ds); li.appendChild(a); list.appendChild(li);
        });
        list.hidden = false; input.setAttribute('aria-expanded', 'true');
        if (status) status.textContent = results.length + ' result' + (results.length === 1 ? '' : 's');
        mark();
      }).catch(function () {
        list.innerHTML = '<li class="sr-empty">Search is unavailable right now.</li>'; list.hidden = false;
      });
    }
    input.addEventListener('focus', function () { load(); if (input.value.trim()) render(); });
    input.addEventListener('input', render);
    input.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowDown' && results.length) { e.preventDefault(); active = (active + 1) % results.length; mark(); }
      else if (e.key === 'ArrowUp' && results.length) { e.preventDefault(); active = (active - 1 + results.length) % results.length; mark(); }
      else if (e.key === 'Enter' && active >= 0 && results[active] && !list.hidden) { e.preventDefault(); window.location.href = results[active].url; }
      else if (e.key === 'Escape') { if (!list.hidden) { e.stopPropagation(); close(); } else input.blur(); }
    });
    d.addEventListener('click', function (e) { if (!box.contains(e.target)) close(); });
  });

  /* "/" focuses the first visible search box */
  d.addEventListener('keydown', function (e) {
    if (e.key !== '/' || e.metaKey || e.ctrlKey || e.altKey) return;
    var tag = (e.target.tagName || '').toLowerCase();
    if (tag === 'input' || tag === 'textarea' || e.target.isContentEditable) return;
    var inputs = d.querySelectorAll('[data-search] input');
    for (var i = 0; i < inputs.length; i++) {
      if (inputs[i].offsetParent !== null) { e.preventDefault(); inputs[i].focus(); return; }
    }
  });
})();
