#!/usr/bin/env python3
"""
Convert public poker notes → Cyberpunk-themed single-page HTML
"""
import re
import html as html_mod

MD_PATH = "/Users/ymz/.cola/outputs/扑克笔记-公开版/poker-notes-public.md"
OUT_PATH = "/Users/ymz/.cola/outputs/扑克笔记-公开版/index.html"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def escape(s):
    return html_mod.escape(s)

def parse_md_table(lines, start_idx):
    """Parse a markdown table starting at lines[start_idx]. Returns (html, end_idx)."""
    header_line = lines[start_idx].strip()
    if not header_line.startswith("|"):
        return None, start_idx
    if start_idx + 1 >= len(lines) or not re.match(r'^\|[\s\-:|]+\|', lines[start_idx + 1]):
        return None, start_idx
    header_cells = [c.strip() for c in header_line.split("|")[1:-1]]
    rows = []
    idx = start_idx + 2
    while idx < len(lines):
        line = lines[idx].strip()
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.split("|")[1:-1]]
        rows.append(cells)
        idx += 1
    html = '            <table>\n'
    html += '              <thead>\n                <tr>\n'
    for cell in header_cells:
        html += f'                  <th>{format_inline(cell)}</th>\n'
    html += '                </tr>\n              </thead>\n'
    html += '              <tbody>\n'
    for row in rows:
        html += '                <tr>\n'
        for cell in row:
            html += f'                  <td>{format_inline(cell)}</td>\n'
        html += '                </tr>\n'
    html += '              </tbody>\n            </table>'
    return html, idx

def format_inline(text):
    """Convert inline markdown to HTML."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em>\1</em>', text)
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    text = escape(text)
    text = text.replace('&lt;strong&gt;', '<strong>').replace('&lt;/strong&gt;', '</strong>')
    text = text.replace('&lt;em&gt;', '<em>').replace('&lt;/em&gt;', '</em>')
    text = text.replace('&lt;code&gt;', '<code>').replace('&lt;/code&gt;', '</code>')
    return text

def parse_content(lines, start_idx, end_idx):
    """Parse body content between start and end. Returns HTML string."""
    html_parts = []
    idx = start_idx
    while idx < end_idx:
        line = lines[idx].rstrip()
        if not line:
            idx += 1
            continue
        if line.startswith("```"):
            code_lines = []
            idx += 1
            while idx < end_idx and not lines[idx].rstrip().startswith("```"):
                code_lines.append(escape(lines[idx].rstrip()))
                idx += 1
            idx += 1
            html_parts.append(f'            <pre><code>{"<br>".join(code_lines)}</code></pre>')
            continue
        if line.startswith("> "):
            quote_lines = []
            while idx < end_idx and lines[idx].rstrip().startswith("> "):
                quote_lines.append(format_inline(lines[idx].rstrip()[2:]))
                idx += 1
            html_parts.append(f'            <blockquote>{"<br>".join(quote_lines)}</blockquote>')
            continue
        if line.strip() == "---":
            html_parts.append('            <hr>')
            idx += 1
            continue
        table_html, new_idx = parse_md_table(lines, idx)
        if table_html:
            html_parts.append(table_html)
            idx = new_idx
            continue
        if line.startswith("### "):
            text = format_inline(line[4:])
            html_parts.append(f'            <h4>{text}</h4>')
            idx += 1
            continue
        if line.startswith("- ") or line.startswith("* "):
            list_items = []
            while idx < end_idx and (lines[idx].rstrip().startswith("- ") or lines[idx].rstrip().startswith("* ")):
                item_text = format_inline(lines[idx].rstrip()[2:])
                sub_items = []
                idx += 1
                while idx < end_idx and lines[idx].rstrip().startswith("  - "):
                    sub_items.append(format_inline(lines[idx].rstrip()[4:]))
                    idx += 1
                if sub_items:
                    subs = "".join(f"<li>{s}</li>" for s in sub_items)
                    list_items.append(f"<li>{item_text}<ul>{subs}</ul></li>")
                else:
                    list_items.append(f"<li>{item_text}</li>")
            html_parts.append(f'            <ul>{"".join(list_items)}</ul>')
            continue
        if re.match(r'^\d+\.\s', line):
            list_items = []
            while idx < end_idx and re.match(r'^\d+\.\s', lines[idx].rstrip()):
                cleaned = re.sub(r'^\d+\.\s', '', lines[idx].rstrip())
                list_items.append(f"<li>{format_inline(cleaned)}</li>")
                idx += 1
            html_parts.append(f'            <ol>{"".join(list_items)}</ol>')
            continue
        if any(line.strip().startswith(e) for e in ['⚠️', '🔥', '📞', '🗑️', '✅', '❌', '🔴', '🟢', '🟡']):
            html_parts.append(f'            <div class="insight">{format_inline(line)}</div>')
            idx += 1
            continue
        para_lines = []
        while idx < end_idx and lines[idx].rstrip() and not lines[idx].rstrip().startswith(("#", "```", "> ", "- ", "* ", "|", "---")) and not re.match(r'^\d+\.\s', lines[idx].rstrip()):
            if not lines[idx].rstrip().startswith("⚠️") and not lines[idx].rstrip().startswith("🔥") and not lines[idx].rstrip().startswith("📞") and not lines[idx].rstrip().startswith("🗑️"):
                para_lines.append(lines[idx].rstrip())
            idx += 1
        if para_lines:
            text = format_inline(" ".join(para_lines))
            html_parts.append(f'            <p>{text}</p>')
        else:
            idx += 1
    return "\n".join(html_parts)

def main():
    content = read_file(MD_PATH)
    lines = content.split("\n")

    # Find H1 title
    title = "扑克深度学习笔记"
    for i, line in enumerate(lines):
        if line.startswith("# "):
            title = line[2:].strip()
            break

    # Find chapters: ## N.
    chapters = []
    current_start = None
    current_title = ""

    for i, line in enumerate(lines):
        stripped = line.strip()
        if re.match(r'^#{1,2}\s+\d+\.', stripped):
            if current_start is not None:
                chapters.append((current_title, current_start, i))
            current_title = stripped[2:].strip()
            slug = re.sub(r'[^a-zA-Z0-9\u4e00-\u9fff]+', '-', current_title).strip('-').lower()
            current_start = (i, slug)

    if current_start is not None:
        chapters.append((current_title, current_start, len(lines)))

    # Pre-header content (between H1 and first chapter)
    pre_start = 0
    for i, line in enumerate(lines):
        if line.startswith("# "):
            pre_start = i + 1
            break

    first_chapter_idx = chapters[0][1][0] if chapters else len(lines)
    pre_header_html = parse_content(lines, pre_start, first_chapter_idx)

    # Build sidebar nav
    nav_items = []
    for c_title, (start, slug), end in chapters:
        nav_items.append(f'            <a href="#{slug}" class="nav-link">{c_title}</a>')

    # Build chapter sections
    sections_html = []
    for c_title, (c_start, c_slug), c_end in chapters:
        content_start = c_start + 1
        section_body = parse_content(lines, content_start, c_end)
        sections_html.append(f'''      <section id="{c_slug}" class="chapter">
        <h2>{format_inline(c_title)}</h2>
{section_body}
      </section>''')

    total_chapters = len(chapters)

    # HTML template — public version (no personal stats, no WIZARDYMC branding)
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{escape(title)} — NL10 公开版</title>
  <meta name="description" content="NL10 线上 6-max 扑克深度学习笔记 — 公开教育版。涵盖翻前策略、翻后牌面分类、玩家分类与剥削、Overbet、盲注防守等 18 章系统内容。">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Noto+Sans+SC:wght@300;400;500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-primary: #0a0e14;
      --bg-secondary: #11161f;
      --bg-card: #161c26;
      --bg-table-header: #1a2030;
      --bg-table-row: #121820;
      --bg-table-alt: #161e28;
      --bg-sidebar: #0d1117;
      --text-primary: #c9d1d9;
      --text-secondary: #8b949e;
      --text-muted: #545d68;
      --accent-cyan: #00d4ff;
      --accent-green: #00ff88;
      --accent-amber: #ffb347;
      --accent-red: #ff4757;
      --accent-purple: #a855f7;
      --border: #21262d;
      --border-focus: #00d4ff44;
      --felt-green: #1a3a2a;
      --felt-dark: #0d1f15;
      --shadow: 0 4px 24px rgba(0, 0, 0, 0.4);
      --radius: 8px;
      --transition: 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      font-family: 'Noto Sans SC', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.7;
      display: flex;
      min-height: 100vh;
    }}

    /* Sidebar */
    .sidebar {{
      position: fixed;
      top: 0;
      left: 0;
      width: 260px;
      height: 100vh;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border);
      overflow-y: auto;
      z-index: 100;
      padding: 0 0 32px;
      scrollbar-width: thin;
      scrollbar-color: var(--text-muted) transparent;
    }}

    .sidebar::-webkit-scrollbar {{ width: 4px; }}
    .sidebar::-webkit-scrollbar-thumb {{ background: var(--text-muted); border-radius: 4px; }}

    .sidebar-header {{
      padding: 28px 24px 20px;
      border-bottom: 1px solid var(--border);
      position: sticky;
      top: 0;
      background: var(--bg-sidebar);
      z-index: 10;
    }}

    .sidebar-header h3 {{
      font-size: 16px;
      font-weight: 600;
      color: var(--accent-cyan);
      letter-spacing: 0.5px;
      font-family: 'JetBrains Mono', monospace;
    }}

    .sidebar-header .subtitle {{
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 4px;
      font-family: 'JetBrains Mono', monospace;
    }}

    .nav {{
      padding: 16px 0;
    }}

    .nav-link {{
      display: block;
      padding: 7px 24px;
      color: var(--text-secondary);
      text-decoration: none;
      font-size: 13px;
      transition: all var(--transition);
      border-left: 2px solid transparent;
      letter-spacing: 0.3px;
    }}

    .nav-link:hover {{
      color: var(--accent-cyan);
      background: rgba(0, 212, 255, 0.04);
      border-left-color: var(--accent-cyan);
    }}

    .nav-link.active {{
      color: var(--accent-cyan);
      background: rgba(0, 212, 255, 0.06);
      border-left-color: var(--accent-cyan);
    }}

    /* Main content */
    .main {{
      margin-left: 260px;
      flex: 1;
      max-width: 900px;
      padding: 48px 56px 80px;
    }}

    .hero {{
      margin-bottom: 48px;
      padding-bottom: 32px;
      border-bottom: 1px solid var(--border);
    }}

    .hero h1 {{
      font-size: 36px;
      font-weight: 700;
      color: #fff;
      letter-spacing: 1px;
      background: linear-gradient(135deg, var(--accent-cyan), var(--accent-green));
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }}

    .hero-meta {{
      display: flex;
      gap: 24px;
      margin-top: 16px;
      font-size: 13px;
      color: var(--text-secondary);
      font-family: 'JetBrains Mono', monospace;
    }}

    .hero-meta span {{
      display: flex;
      align-items: center;
      gap: 6px;
    }}

    .hero-meta .dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
    }}

    .dot-green {{ background: var(--accent-green); box-shadow: 0 0 8px var(--accent-green); }}
    .dot-cyan {{ background: var(--accent-cyan); box-shadow: 0 0 8px var(--accent-cyan); }}

    /* Notice banner */
    .notice {{
      background: rgba(255, 179, 71, 0.08);
      border: 1px solid rgba(255, 179, 71, 0.2);
      border-radius: var(--radius);
      padding: 12px 18px;
      margin-bottom: 32px;
      font-size: 13px;
      color: var(--text-secondary);
    }}

    .notice strong {{
      color: var(--accent-amber);
    }}

    /* Chapter styles */
    .chapter {{
      margin-bottom: 56px;
      padding-top: 24px;
    }}

    .chapter h2 {{
      font-size: 24px;
      font-weight: 600;
      color: #fff;
      padding-bottom: 12px;
      border-bottom: 1px solid var(--border);
      margin-bottom: 24px;
      letter-spacing: 0.5px;
    }}

    .chapter h3 {{
      font-size: 18px;
      font-weight: 600;
      color: var(--accent-cyan);
      margin: 28px 0 12px;
    }}

    .chapter h4 {{
      font-size: 15px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 20px 0 8px;
    }}

    .chapter p {{
      margin: 10px 0;
      color: var(--text-secondary);
      font-size: 14px;
    }}

    .chapter p strong {{
      color: var(--text-primary);
    }}

    /* Tables */
    .chapter table {{
      width: 100%;
      border-collapse: collapse;
      margin: 20px 0;
      font-size: 13px;
      font-family: 'JetBrains Mono', 'Noto Sans SC', monospace;
      background: var(--bg-table-row);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      overflow: hidden;
    }}

    .chapter thead {{
      background: var(--bg-table-header);
    }}

    .chapter th {{
      padding: 10px 14px;
      text-align: left;
      font-weight: 600;
      color: var(--accent-cyan);
      font-size: 12px;
      letter-spacing: 0.5px;
      border-bottom: 1px solid var(--border);
      white-space: nowrap;
    }}

    .chapter td {{
      padding: 8px 14px;
      color: var(--text-secondary);
      border-bottom: 1px solid rgba(33, 38, 45, 0.5);
    }}

    .chapter tbody tr:hover {{
      background: rgba(0, 212, 255, 0.04);
    }}

    .chapter tbody tr:nth-child(even) {{
      background: var(--bg-table-alt);
    }}

    .chapter tbody tr:nth-child(even):hover {{
      background: rgba(0, 212, 255, 0.04);
    }}

    .chapter td strong {{
      color: var(--accent-green);
    }}

    /* Code */
    pre {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 18px 20px;
      margin: 16px 0;
      overflow-x: auto;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      line-height: 1.6;
      color: var(--accent-green);
    }}

    code {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      background: var(--bg-card);
      color: var(--accent-cyan);
      padding: 2px 6px;
      border-radius: 3px;
    }}

    /* Blockquote */
    blockquote {{
      border-left: 3px solid var(--accent-cyan);
      background: rgba(0, 212, 255, 0.03);
      padding: 14px 18px;
      margin: 16px 0;
      border-radius: 0 var(--radius) var(--radius) 0;
      color: var(--text-secondary);
      font-size: 13px;
      font-style: italic;
    }}

    /* Insight boxes */
    .insight {{
      background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(0, 255, 136, 0.03));
      border: 1px solid rgba(0, 212, 255, 0.15);
      border-radius: var(--radius);
      padding: 12px 18px;
      margin: 14px 0;
      font-size: 13px;
      color: var(--text-primary);
    }}

    .insight strong {{
      color: var(--accent-amber);
    }}

    hr {{
      border: none;
      border-top: 1px solid var(--border);
      margin: 24px 0;
    }}

    ul, ol {{
      margin: 10px 0;
      padding-left: 24px;
      color: var(--text-secondary);
      font-size: 14px;
    }}

    li {{
      margin: 4px 0;
    }}

    /* Scrollbar */
    .main::-webkit-scrollbar {{ width: 6px; }}
    .main::-webkit-scrollbar-thumb {{ background: var(--text-muted); border-radius: 4px; }}

    /* Hamburger */
    .hamburger {{
      display: none;
      position: fixed;
      top: 16px;
      left: 16px;
      z-index: 200;
      background: var(--bg-card);
      border: 1px solid var(--border);
      color: var(--text-primary);
      padding: 8px 12px;
      border-radius: var(--radius);
      cursor: pointer;
      font-size: 18px;
    }}

    .sidebar-overlay {{
      display: none;
    }}

    @media (max-width: 768px) {{
      .sidebar {{
        transform: translateX(-100%);
        transition: transform var(--transition);
      }}
      .sidebar.open {{
        transform: translateX(0);
      }}
      .sidebar-overlay {{
        display: none;
        position: fixed;
        inset: 0;
        background: rgba(0,0,0,0.6);
        z-index: 99;
      }}
      .sidebar-overlay.open {{
        display: block;
      }}
      .hamburger {{
        display: block;
      }}
      .main {{
        margin-left: 0;
        padding: 24px 20px 60px;
      }}
      .hero h1 {{
        font-size: 24px;
      }}
      .chapter h2 {{
        font-size: 20px;
      }}
      .chapter table {{
        font-size: 11px;
      }}
      .chapter th, .chapter td {{
        padding: 6px 8px;
      }}
    }}
  </style>
</head>
<body>
  <button class="hamburger" onclick="toggleSidebar()">☰</button>
  <div class="sidebar-overlay" id="overlay" onclick="toggleSidebar()"></div>

  <nav class="sidebar" id="sidebar">
    <div class="sidebar-header">
      <h3>♠ NL10 STUDY NOTES</h3>
      <div class="subtitle">SYSTEMATIC POKER · 公开版</div>
    </div>
    <div class="nav">
{"".join(nav_items)}
    </div>
  </nav>

  <main class="main">
    <div class="hero">
      <h1>{escape(title)}</h1>
      <div class="hero-meta">
        <span><span class="dot dot-green"></span> {total_chapters} 章</span>
        <span><span class="dot dot-cyan"></span> NL10 6-Max 现金桌</span>
        <span>GG Poker · GTO 理论 + 实战</span>
      </div>
    </div>
    <div class="notice">
      <strong>说明：</strong>本文档基于个人学习笔记整理，已移除日记内容和私人数据，保留全部核心教育内容。适合 NL10-NL25 线上现金桌玩家参考。
    </div>
{pre_header_html}
{"".join(sections_html)}
  </main>

  <script>
    function toggleSidebar() {{
      document.getElementById('sidebar').classList.toggle('open');
      document.getElementById('overlay').classList.toggle('open');
    }}

    document.querySelectorAll('.nav-link').forEach(link => {{
      link.addEventListener('click', () => {{
        document.getElementById('sidebar').classList.remove('open');
        document.getElementById('overlay').classList.remove('open');
      }});
    }});

    const observer = new IntersectionObserver(entries => {{
      entries.forEach(entry => {{
        const id = entry.target.id;
        const link = document.querySelector(`a[href="#${{id}}"]`);
        if (entry.isIntersecting) {{
          document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
          if (link) link.classList.add('active');
        }}
      }});
    }}, {{ rootMargin: '-20% 0px -70% 0px' }});

    document.querySelectorAll('.chapter').forEach(ch => observer.observe(ch));
  </script>
</body>
</html>'''

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)

    # Verify
    with open(OUT_PATH, "r", encoding="utf-8") as f:
        out = f.read()

    checks = [
        ("Title", "扑克深度学习笔记"),
        ("Ch 1", "心态与纪律"),
        ("Ch 13", "Overbet"),
        ("Ch 18", "River Bluff"),
        ("Sidebar", "NL10 STUDY NOTES"),
        ("CSS vars", "--bg-primary"),
        ("Notice", "本文档基于个人学习笔记整理"),
        ("No stats", "HANDS"),
    ]

    all_ok = True
    for name, keyword in checks:
        if name == "No stats":
            if keyword in out:
                print(f"  ⚠️  {name} — '{keyword}' STILL PRESENT")
                all_ok = False
            else:
                print(f"  ✅ {name} — correctly absent")
        elif keyword in out:
            print(f"  ✅ {name} — found '{keyword}'")
        else:
            print(f"  ❌ {name} — MISSING '{keyword}'")
            all_ok = False

    print(f"\nOutput: {OUT_PATH}")
    print(f"Size: {len(out):,} chars")
    print(f"Status: {'ALL CHECKS PASSED' if all_ok else 'SOME CHECKS FAILED'}")

if __name__ == "__main__":
    main()
