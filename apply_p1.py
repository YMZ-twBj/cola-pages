#!/usr/bin/env python3
# P1 enhancements: reading-progress bar, back-to-top, dark-mode toggle,
# sidebar scrollspy, mobile table horizontal scroll, MTT mobile sidebar toggle.
import re, os, sys

ROOT = "/tmp/cola-pages"
SITES = {
    "nl10-poker-notes": {
        "theme_default": "dark",
        "html_attr": '<html lang="zh-CN" data-theme="dark">',
        # NL10 is variable-based -> clean light theme via variable overrides.
        "extra_css": """
html[data-theme="light"]{
  --bg-primary:#eef1f5; --bg-secondary:#ffffff; --bg-card:#ffffff;
  --bg-table-header:#e7ecf2; --bg-table-row:#ffffff; --bg-table-alt:#f5f7fa;
  --text-primary:#1b2230; --text-secondary:#465061; --text-muted:#7a8694;
  --border:#d6dce4; --shadow:0 4px 20px rgba(20,30,50,.10);
  --felt-green:#1a3a2a; --felt-dark:#0d1f15;
}
html[data-theme="light"] .sidebar{
  --bg-sidebar:#0d1117; --text-primary:#c9d1d9; --text-secondary:#8b949e;
  --text-muted:#545d68; --border:#21262d;
}
""",
        # NL10 already has its own hamburger; do NOT add another.
        "controls": """
<div id="p1-progress"></div>
<button id="p1-theme-toggle" title="切换 深色 / 浅色 (Dark / Light)">☀️</button>
<button id="p1-top" title="回到顶部 (Back to top)">↑</button>
""",
    },
    "tournament-academy": {
        "theme_default": "light",
        "html_attr": '<html lang="zh-CN" data-theme="light">',
        # MTT uses hardcoded Tailwind utility colors -> filter-based dark mode
        # (covers every utility class). Photos re-inverted to stay natural.
        "extra_css": """
html[data-theme="dark"]{ filter: invert(1) hue-rotate(180deg); }
html[data-theme="dark"] img,
html[data-theme="dark"] video,
html[data-theme="dark"] .no-invert{ filter: invert(1) hue-rotate(180deg); }
""",
        "controls": """
<div id="p1-progress"></div>
<button class="p1-hamburger" title="菜单 (Menu)">☰</button>
<div class="sidebar-overlay-p1"></div>
<button id="p1-theme-toggle" title="切换 深色 / 浅色 (Dark / Light)">🌙</button>
<button id="p1-top" title="回到顶部 (Back to top)">↑</button>
""",
    },
}

SHARED_CSS = """
/* === P1-ENHANCE === */
html{ scroll-behavior:smooth; }
#p1-progress{ position:fixed; top:0; left:0; height:3px; width:0; z-index:10000;
  background:linear-gradient(90deg,#00d4ff,#00ff88); transition:width .08s linear; }
#p1-theme-toggle{ position:fixed; top:14px; right:16px; z-index:10000; width:40px; height:40px;
  border-radius:50%; border:1px solid var(--border,#2a2f45); background:var(--bg-card,#161c26);
  color:var(--text-primary,#c9d1d9); cursor:pointer; font-size:17px; display:flex;
  align-items:center; justify-content:center; box-shadow:0 2px 10px rgba(0,0,0,.35); }
#p1-top{ position:fixed; bottom:22px; right:16px; z-index:10000; width:42px; height:42px;
  border-radius:50%; border:1px solid var(--border,#2a2f45); background:var(--bg-card,#161c26);
  color:var(--text-primary,#c9d1d9); cursor:pointer; font-size:18px; display:none;
  align-items:center; justify-content:center; box-shadow:0 2px 10px rgba(0,0,0,.35); }
#p1-top.show{ display:flex; }
.tbl-scroll{ width:100%; overflow-x:auto; -webkit-overflow-scrolling:touch; margin:1em 0; }
.tbl-scroll table{ width:100%; }
a.nav-link.active{ color:#00d4ff !important; font-weight:700;
  border-left-color:#00d4ff !important; background:rgba(0,212,255,.10); }
.p1-hamburger{ position:fixed; top:12px; left:14px; z-index:9998; display:none; width:42px; height:42px;
  border-radius:8px; border:1px solid #fbbf24; background:#fff7ed; color:#b45309; font-size:20px;
  cursor:pointer; align-items:center; justify-content:center; }
.sidebar-overlay-p1{ position:fixed; inset:0; background:rgba(0,0,0,.5); z-index:9996; display:none; }
.sidebar-overlay-p1.show{ display:block; }
@media (max-width:1024px){
  .p1-hamburger{ display:flex; }
  .sidebar{ transform:translateX(-100%); transition:transform .3s ease; z-index:9997; }
  .sidebar.open{ transform:none; }
  .main-wrap{ margin-left:0 !important; padding:70px 18px 60px !important; }
  #p1-theme-toggle{ top:12px; right:12px; }
}
"""

SHARED_JS = """
<!-- === P1-ENHANCE JS === -->
<script>
(function(){
  var root=document.documentElement;
  var THEME_KEY='poker-site-theme';
  function applyTheme(t){
    root.setAttribute('data-theme',t);
    var btn=document.getElementById('p1-theme-toggle');
    if(btn) btn.textContent=(t==='dark')?'☀️':'🌙';
  }
  var saved=null;
  try{ saved=localStorage.getItem(THEME_KEY); }catch(e){}
  applyTheme(saved || root.getAttribute('data-theme') || 'dark');
  var tbtn=document.getElementById('p1-theme-toggle');
  if(tbtn) tbtn.addEventListener('click',function(){
    var t=(root.getAttribute('data-theme')==='dark')?'light':'dark';
    applyTheme(t);
    try{ localStorage.setItem(THEME_KEY,t); }catch(e){}
  });
  var bar=document.getElementById('p1-progress');
  var top=document.getElementById('p1-top');
  function onScroll(){
    var d=document.documentElement;
    var max=d.scrollHeight-d.clientHeight;
    var y=d.scrollTop||document.body.scrollTop||0;
    bar.style.width=(max>0?(y/max*100):0)+'%';
    if(top) top.classList.toggle('show', y>400);
  }
  window.addEventListener('scroll',onScroll,{passive:true});
  window.addEventListener('resize',onScroll);
  onScroll();
  if(top) top.addEventListener('click',function(){ window.scrollTo({top:0,behavior:'smooth'}); });
  var links=[].slice.call(document.querySelectorAll('a.nav-link[href^="#"]'));
  var map={};
  links.forEach(function(a){ var id=a.getAttribute('href').slice(1); if(id) map[id]=a; });
  var targets=Object.keys(map).map(function(id){return document.getElementById(id);}).filter(Boolean);
  if('IntersectionObserver' in window && targets.length){
    var io=new IntersectionObserver(function(entries){
      entries.forEach(function(e){
        if(e.isIntersecting){
          links.forEach(function(l){ l.classList.remove('active'); });
          var a=map[e.target.id]; if(a) a.classList.add('active');
        }
      });
    },{rootMargin:'-15% 0px -75% 0px',threshold:0});
    targets.forEach(function(t){ io.observe(t); });
  }
  var ham=document.querySelector('.p1-hamburger');
  if(ham){
    var sb=document.querySelector('.sidebar');
    var ov=document.querySelector('.sidebar-overlay-p1');
    function tog(){ if(sb) sb.classList.toggle('open'); if(ov) ov.classList.toggle('show'); }
    ham.addEventListener('click',tog);
    if(ov) ov.addEventListener('click',tog);
  }
})();
</script>
"""

for site, cfg in SITES.items():
    p = os.path.join(ROOT, site, "index.html")
    html = open(p, encoding="utf-8", errors="replace").read()
    if "<!-- === P1-ENHANCE ===" in html:
        print(f"[skip] {site}: P1 already applied"); continue

    # 1) theme attribute on <html>
    html = html.replace('<html lang="zh-CN">', cfg["html_attr"], 1)

    # 2) inject CSS before </head>
    css = f"/* === P1-ENHANCE === */\n{SHARED_CSS}\n{cfg['extra_css']}\n"
    html = html.replace("</head>", css + "</head>", 1)

    # 3) inject controls right after <body ...>
    html = re.sub(r"(<body[^>]*>)", r"\1\n" + cfg["controls"], html, count=1)

    # 4) wrap every <table> in .tbl-scroll (idempotent: skip already-wrapped)
    def wrap_table(m):
        block = m.group(0)
        if 'class="tbl-scroll"' in block[:60]:
            return block
        return '<div class="tbl-scroll">\n' + block + "\n</div>"
    html = re.sub(r"<table.*?</table>", wrap_table, html, flags=re.S)

    # 5) inject JS before </body>
    html = html.replace("</body>", SHARED_JS + "\n</body>", 1)

    open(p, "w", encoding="utf-8").write(html)
    print(f"[done] {site}: css+controls+tables+js injected")
print("P1 injection complete.")
