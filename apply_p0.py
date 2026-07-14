# -*- coding: utf-8 -*-
import os, shutil

REPO = "/tmp/cola-pages"
ICLOUD = "/Users/ymz/Library/Mobile Documents/com~apple~CloudDocs/Documents/poker"
EX = "/Users/ymz/WorkBuddy/2026-07-14-10-16-11/examples"

def img(src, alt, caption=None):
    s = '<figure style="margin:18px 0">'
    s += f'<img src="{src}" alt="{alt}" loading="lazy" style="max-width:100%;height:auto;border-radius:10px;box-shadow:0 4px 18px rgba(0,0,0,.3)">'
    if caption:
        s += f'<figcaption style="color:#8b9bb4;font-size:12px;margin-top:6px;text-align:center">{caption}</figcaption>'
    s += '</figure>'
    return s

def banner(other_href, other_label, other_color):
    return ('<div style="position:sticky;top:0;z-index:50;background:#0f1424ee;'
            'backdrop-filter:blur(6px);border-bottom:1px solid #243049;'
            'padding:10px 16px;text-align:center;font-size:14px;margin-bottom:8px">'
            f'📖 <a href="../nl10-poker-notes/" style="color:#5b8def;text-decoration:none;font-weight:700">NL10 扑克笔记（主站）</a>'
            ' &nbsp;·&nbsp; '
            f'🏆 <a href="../tournament-academy/" style="color:#e94560;text-decoration:none;font-weight:700">MTT 锦标赛学院</a>'
            '</div>')

def insert_after_heading(html, full_heading, snippet):
    idx = html.find(full_heading)
    if idx < 0:
        raise SystemExit(f"ANCHOR NOT FOUND: {full_heading[:60]}")
    at = idx + len(full_heading)
    return html[:at] + "\n" + snippet + "\n" + html[at:]

def insert_after_close(html, close_sub, snippet):
    idx = html.find(close_sub)
    if idx < 0:
        raise SystemExit(f"ANCHOR NOT FOUND: {close_sub[:60]}")
    at = idx + len(close_sub)
    return html[:at] + "\n" + snippet + "\n" + html[at:]

def insert_after_h1(html, text, snippet):
    i = html.find(text)
    if i < 0:
        raise SystemExit(f"H1 TEXT NOT FOUND: {text[:40]}")
    j = html.find('</h1>', i)
    if j < 0:
        raise SystemExit(f"NO </h1> after: {text[:40]}")
    at = j + len('</h1>')
    return html[:at] + "\n" + snippet + "\n" + html[at:]

# ---------- copy images ----------
nl_img = os.path.join(REPO, "nl10-poker-notes", "img")
mt_img = os.path.join(REPO, "tournament-academy", "img")
os.makedirs(nl_img, exist_ok=True)
os.makedirs(mt_img, exist_ok=True)

# real assets (lighter web versions)
shutil.copyfile(os.path.join(ICLOUD, "images", "翻前范围阶梯图.png"), os.path.join(nl_img, "nl10-range-ladder.png"))
shutil.copyfile(os.path.join(ICLOUD, "玩家象限图.jpeg"), os.path.join(nl_img, "player-quadrant.jpeg"))
# example SVGs
for f in ["tilt_gauge.svg","outs_equity.svg","position_winrate.svg","preflop_range_btn.svg","preflop_range_utg.svg"]:
    shutil.copyfile(os.path.join(EX, f), os.path.join(nl_img, f))
for f in ["mtt_roadmap.svg","icm_bubble_factor.svg","stack_depth_coefficient.svg","pushfold_heatmap.svg"]:
    shutil.copyfile(os.path.join(EX, f), os.path.join(mt_img, f))
print("images copied")

# ---------- NL10 edits ----------
p = os.path.join(REPO, "nl10-poker-notes", "index.html")
h = open(p, encoding="utf-8").read()
h = h.replace('<h1>扑克深度学习笔记 — NL10 6-max 线上（公开版）</h1>',
              '<h1>扑克深度学习笔记 — NL10 6-max 线上（公开版）</h1>\n' + banner("", "", ""), 1)
h = insert_after_heading(h, '<h4>(3) Tilt 四阶段</h4>',
    img("img/tilt-gauge.svg", "Tilt 四阶段风险条", "Tilt 四阶段风险条 · 配合 -3 组止损线"))
h = insert_after_heading(h, '<h4>(2) 概率论入门：Outs、胜率与赔率</h4>',
    img("img/outs-equity.svg", "Outs 到胜率曲线", "Outs → 胜率（转牌 / 河牌）· 规则 2/4 的精确版"))
h = insert_after_heading(h, '<h2>9. 军争篇：IP/OOP — 位置博弈与信息差</h2>',
    img("img/position-winrate.svg", "位置赢率示意", "位置赢率示意 (bb/100) · 越后位越高，盲位通常为负"))
h = insert_after_heading(h, '<h2>9. 翻前范围详解</h2>',
    img("img/nl10-range-ladder.png", "NL10 6-max 范围阶梯图", "NL10 6-max 翻前范围阶梯（真实导出）") +
    img("img/preflop_range_btn.svg", "BTN 开池范围", "BTN 开池范围热图（示例）") +
    img("img/preflop_range_utg.svg", "UTG 开池范围", "UTG 开池范围热图（示例）· 与 BTN 对比可见位置对宽度的 ~3 倍影响"))
h = insert_after_heading(h, '<h2>18. 进阶：玩家分类与针对性策略</h2>',
    img("img/player-quadrant.jpeg", "玩家象限图", "玩家四象限分类（真实图）"))
open(p, "w", encoding="utf-8").write(h)
print("nl10 index.html edited")

# ---------- MTT edits ----------
p = os.path.join(REPO, "tournament-academy", "index.html")
h = open(p, encoding="utf-8").read()
h = insert_after_h1(h, '🏆 锦标赛特训营', banner("", "", ""))
h = insert_after_close(h, 'MTT 十阶段作战地图</h2>',
    img("img/mtt-roadmap.svg", "MTT 十阶段作战地图", "MTT 十阶段作战地图（示例）"))
h = insert_after_close(h, '第二关：ICM 决策体系</h2>',
    img("img/icm-bubble-factor.svg", "ICM Bubble Factor 曲线", "ICM Bubble Factor 曲线（示例）· 接近泡沫急剧上升"))
h = insert_after_close(h, '第二维：码量 (Stack Depth)</h3>',
    img("img/stack-depth-coefficient.svg", "码量系数", "码量系数 (Open% 调整) · 以 40bb=1.0 为基准"))
h = insert_after_close(h, '短码 Push/Fold 速查（<15bb）</h3>',
    img("img/pushfold-heatmap.svg", "Push/Fold 范围", "Push/Fold 范围 — BTN <15bb（示例）· 用 Nash 表替换"))
open(p, "w", encoding="utf-8").write(h)
print("tournament index.html edited")
print("DONE")
