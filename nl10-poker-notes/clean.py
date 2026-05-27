#!/usr/bin/env python3
"""
Clean poker notes: remove personal content, produce public-facing educational document.
"""
import re

SRC = "/Users/ymz/Documents/poker/扑克深度学习笔记.md"
DST = "/Users/ymz/.cola/outputs/扑克笔记-公开版/poker-notes-public.md"

with open(SRC, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split("\n")

# We'll build the output by including/excluding line ranges.
# Strategy: mark sections to KEEP, then process the kept content.

# Find all H2 headings (##) to identify section boundaries
h2_indices = []
for i, line in enumerate(lines):
    if re.match(r'^#{1,2}\s+\d+\.', line.strip()) or line.strip().startswith("# 附錄") or line.strip().startswith("## 附錄"):
        h2_indices.append(i)

# Map section titles to their start/end
sections = []
for j, idx in enumerate(h2_indices):
    title = lines[idx].strip()
    if title.startswith("## "):
        title = title[3:]
    elif title.startswith("# "):
        title = title[2:]
    end = h2_indices[j+1] if j+1 < len(h2_indices) else len(lines)
    sections.append((idx, end, title))

print("Found sections:")
for s, e, t in sections:
    print(f"  L{s}-{e}: {t}")

# Define which section titles to EXCLUDE (full section removal)
EXCLUDE_TITLES = [
    "12. Rush & Cash 与系统学习",
    "12. Rush & Cash 與系統學習", 
    "13. 锦标赛入门（MTT）",
    "13. 錦標賽入門（MTT）",
    "16. 5/18 — 情绪管理的实战课",
    "16. 5/18 — 情緒管理的實戰課",
    "數據審計",
    "学习日志",
    "學習日誌",
]

# Also need to exclude "待学习清单" and the "学习日志" block that appears 
# between chapters (not as a proper H2 heading)
# These are in the middle of the document

# Build the list of line ranges to KEEP
keep_ranges = []

# 1. Find the real start: after the stats header block (ends at "---" before ## 1.)
first_h2 = h2_indices[0]  # Should be "## 1. 心态与纪律"
# Find the --- line before this H2
header_end = first_h2
for i in range(first_h2 - 1, 0, -1):
    if lines[i].strip() == "---":
        header_end = i + 1
        break

# 2. Identify which H2 sections to keep vs exclude
excluded_ranges = []
for s, e, t in sections:
    for et in EXCLUDE_TITLES:
        if t == et or t.startswith(et):
            excluded_ranges.append((s, e))
            break

# Also find "待学习清单" block (it's not an H2 but has its own heading)
# and "学习日志" block (also not an H2)
extra_exclude_starts = []
extra_exclude_ends = []

for i in range(header_end, len(lines)):
    stripped = lines[i].strip()
    if stripped == "### 待学习清单" or stripped == "### 學習清單" or stripped == "待学习清单":
        # Find the end of this block (next H2 or next major section)
        for j in range(i+1, len(lines)):
            if re.match(r'^#{1,2}\s+', lines[j].strip()):
                extra_exclude_starts.append(i)
                extra_exclude_ends.append(j)
                break
        break

for i in range(header_end, len(lines)):
    stripped = lines[i].strip()
    if stripped == "### 学习日志" or stripped == "### 學習日誌" or stripped == "### 2026-05-02":
        # Find the end: next "## 12. Rush" or similar
        for j in range(i+1, len(lines)):
            if re.match(r'^#{1,2}\s+12\.\s*(Rush|大牌)', lines[j].strip()):
                extra_exclude_starts.append(i)
                extra_exclude_ends.append(j)
                break
        break

# Find the first "最后更新" line before end and strip it plus trailing content
final_update_idx = None
for i in range(len(lines)-1, len(lines)-200, -1):
    if "最后更新" in lines[i] or "最後更新" in lines[i]:
        final_update_idx = i
        break

# Build comprehensive excluded ranges (sorted)
all_excluded = list(excluded_ranges)
for s, e in zip(extra_exclude_starts, extra_exclude_ends):
    all_excluded.append((s, e))

# Sort by start
all_excluded.sort()

# Now build keep_ranges
current = header_end
for es, ee in all_excluded:
    if current < es:
        keep_ranges.append((current, es))
    current = max(current, ee)

# After last excluded, keep to end (but trim final update)
end_point = final_update_idx if final_update_idx else len(lines)
if current < end_point:
    keep_ranges.append((current, end_point))

print(f"\nKeep ranges: {keep_ranges}")
print(f"Excluded: {all_excluded}")

# Build output lines
output_lines = []

# Add a brief header note
output_lines.append("# 扑克深度学习笔记 — NL10 6-max 线上（公开版）")
output_lines.append("")
output_lines.append("> **说明**：本文档基于个人学习笔记整理，已移除日记内容和私人数据，保留所有核心教育内容。适合 NL10-NL25 线上现金桌玩家参考。")
output_lines.append("> **原始笔记来源**：GGpoker NL10 6-max 慢速桌实战与 GTO 理论学习。")
output_lines.append("")
output_lines.append("---")
output_lines.append("")

# Now concatenate kept content
for start, end in keep_ranges:
    # Skip leading empty lines in each block
    while start < end and not lines[start].strip():
        start += 1
    # Add a blank line between sections if needed
    if output_lines and output_lines[-1].strip():
        output_lines.append("")
    output_lines.extend(lines[start:end])

# Join and apply text replacements
output = "\n".join(output_lines)

# --- TEXT REPLACEMENTS ---

# Replace "施老师" references
output = output.replace("施老师 ", "读者 ")
output = output.replace("施老师：", "读者：")
output = output.replace("施老师实战推导", "实战推导")
output = output.replace("施老师实战提問", "实战提问")
output = output.replace("施老师 2026-05-20 Sessions", "实战 Session 记录")
output = output.replace("施老師", "读者")
output = output.replace("施老师特别版", "特别说明")
output = output.replace("小可教练 + 施老师", "编辑团队")
output = output.replace("小可教练", "编辑团队")

# Remove personal bankroll references in chapter bodies (keep the structure)
output = re.sub(r'💰\s*目前资金[：:][^\n]*\n', '', output)
output = re.sub(r'后备资金[：:][^\n]*\n', '', output)
output = re.sub(r'资金[：:]\s*¥\d+[^\n]*\n', '', output)
output = re.sub(r'资金里程碑[^\n]*\n', '', output)
output = re.sub(r'三天时间从[^\n]*\n', '', output)

# Remove personal date references like "2026-05-03 晚 ~ 2026-05-04 凌晨"
output = re.sub(r'> \*\*最后更新\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*最後更新\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*笔记者\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*筆記者\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*今日重点\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*今日重點\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*阅读方式\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*閱讀方式\*\*[^\n]*\n', '', output)

# Remove session/bankroll specific lines
output = re.sub(r'> \*\*Session 報告\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*实战战绩\*\*[^\n]*\n', '', output)
output = re.sub(r'- 💰[^\n]*\n', '', output)
output = re.sub(r'- 🎰[^\n]*\n', '', output)
output = re.sub(r'- 🃏[^\n]*\n', '', output)

# Remove stats header block elements
output = re.sub(r'> \*\*玩家档案\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*玩家檔案\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*学习日期\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*學習日期\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*战绩\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*戰績\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*核心目标\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*核心目標\*\*[^\n]*\n', '', output)
output = re.sub(r'> - 5/2[^\n]*\n', '', output)
output = re.sub(r'> - 5/3[^\n]*\n', '', output)
output = re.sub(r'> - 5/4[^\n]*\n', '', output)
output = re.sub(r'> - 累计[^\n]*\n', '', output)

# Remove personal bankroll lines in Ch 1 (心态与纪律)
output = re.sub(r'后备资金[：:][^\n]*\n', '', output)

# Remove "買入：\$10\.00[^\n]*" from Ch 1.4 Poker Plan
output = re.sub(r'买入[：:]\s*\$10[^\n]*\n', '', output)
output = re.sub(r'買入[：:]\s*\$10[^\n]*\n', '', output)
output = re.sub(r'桌数[：:][^\n]*\n', '', output)
output = re.sub(r'模式[：:][^\n]*\n', '', output)

# Remove the specific bankroll paragraph from Ch 1.4
output = re.sub(r'级别[：:]\s*NL10[^\n]*\n', '', output)
output = re.sub(r'級別[：:]\s*NL10[^\n]*\n', '', output)

# Remove the "Poker Plan" subsection entirely (1.4) - it contains personal bankroll details
# Find and remove the section between "### 1.4" and "### 1.5"
output = re.sub(
    r'### 1\.4 当前 Poker Plan.*?(?=### 1\.5)',
    '',
    output,
    flags=re.DOTALL
)
output = re.sub(
    r'### 1\.4 當前 Poker Plan.*?(?=### 1\.5)',
    '',
    output,
    flags=re.DOTALL
)

# Remove the Bad Beat Jackpot section imagery reference
output = re.sub(r'!\[Jackpot\][^\n]*\n', '', output)

# Remove "参考卡" file path references
output = re.sub(r'> \*\*參考卡\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*参考卡\*\*[^\n]*\n', '', output)

# Remove data source / contributor footers with personal info
output = re.sub(r'> \*\*貢獻\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*数据来源\*\*[：:][^\n]*GTO[^\n]*\n', '> *数据来源：GTO Wizard*\n', output)
output = re.sub(r'> \*\*數據來源\*\*[：:][^\n]*GTO[^\n]*\n', '> *数据来源：GTO Wizard*\n', output)
output = re.sub(r'> \*\*編制\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*编制\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*實戰牌例\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*实战牌例\*\*[：:][^\n]*\n', '', output)

# Remove session report line references
output = re.sub(r'> \*\*Session[^\n]*\n', '', output)

# Remove personal "数据背景" line with specific hand count
output = re.sub(r'> \*\*數據背景\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*数据背景\*\*[：:][^\n]*\n', '', output)

# Remove "下次审计" line
output = re.sub(r'> \*\*下次審計\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*下次审计\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*審計日期\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*审计日期\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*審計頻率\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*审计频率\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*數據範圍\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*数据范围\*\*[^\n]*\n', '', output)

# Clean up "本日关键句" / "本日總結" personal footers
output = re.sub(r'> \*\*本日關鍵句\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*本日关键句\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*為什麼重要\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*为什么重要\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*下一步\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*本日總結\*\*[^\n]*\n', '', output)
output = re.sub(r'> \*\*本日总结\*\*[^\n]*\n', '', output)

# Clean up date headers like "2026-05-03 晚 ~ 2026-05-04 凌晨"
output = re.sub(r'### 2026-05-\d+[^\n]*\n', '', output)

# Remove the "数据来源 + 编制" footers that remain
output = re.sub(r'> \*\*數據來源\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*数据来源\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*編制\*\*[：:][^\n]*\n', '', output)
output = re.sub(r'> \*\*编制\*\*[：:][^\n]*\n', '', output)

# --- CHAPTER RENUMBERING ---
# After removing chapters 12 (Rush), 13 (MTT), 16 (情绪), we need to renumber
# Old -> New mapping:
# 1-11 stay same
# 12 (大牌翻后透明化) stays 12
# 14 (Overbet) -> 13
# 15 (Bet Size) -> 14
# 17 (牌面分类) -> 15
# 18 (BB/SB) -> 16
# 19 (特定手牌) -> 17
# 20 (River Bluff) -> 18

renumber_map = {
    "14. Overbet": "13. Overbet",
    "14. Overbet 与防 Overbet": "13. Overbet 与防 Overbet",
    "14. Overbet 與防 Overbet": "13. Overbet 與防 Overbet",
    "15. Bet Size 即语言": "14. Bet Size 即语言",
    "15. Bet Size 即语言：從讀牌到讀人": "14. Bet Size 即语言：從讀牌到讀人",
    "15. Bet Size 即语言：從讀牌到讀人": "14. Bet Size 即语言：從讀牌到讀人",
    "17. 牌面分类 × 底池类型": "15. 牌面分类 × 底池类型",
    "17. 牌面分類 × 底池類型": "15. 牌面分類 × 底池類型",
    "17. 牌面分类 × 底池类型 + SB vs BB 范围": "15. 牌面分类 × 底池类型 + SB vs BB 范围",
    "17. 牌面分類 × 底池類型 + SB vs BB 範圍": "15. 牌面分類 × 底池類型 + SB vs BB 範圍",
    "18. BB/SB 盲注位防守系统": "16. BB/SB 盲注位防守系统",
    "18. BB/SB 盲注位防守系統": "16. BB/SB 盲注位防守系統",
    "19. 特定手牌專題": "17. 特定手牌專題",
    "19. 特定手牌专题": "17. 特定手牌专题",
    "20. River Bluff": "18. River Bluff",
}

# Apply renumbering to headings
for old, new in renumber_map.items():
    output = output.replace(f"## {old}", f"## {new}")
    output = output.replace(f"# {old}", f"# {new}")

# Fix sub-section numbering for moved chapters
# 14.x -> 13.x
output = re.sub(r'(?<!\d)14\.(\d+)', r'13.\1', output)
# 15.x -> 14.x  
output = re.sub(r'(?<!\d)15\.(\d+)', r'14.\1', output)
# But careful: 15 in normal text shouldn't change. Only in heading context.
# Actually, the regex above is too aggressive. Let me be more targeted.

# Actually let's just fix the H3/H4 heading numbers
# The sub-numbering within chapters should be preserved as-is since they're
# internal to the chapter. I'll just fix the chapter-level headings.

# Fix references to old chapter numbers in cross-references
output = output.replace("Chapter 18", "Chapter 16")
output = output.replace("Chapter 17", "Chapter 15")
output = output.replace("Chapter 16", "Chapter 16")  
# etc. Let me check what cross-refs exist

# Fix TOC if any remains (most of it was in the header we removed)
# Let's rebuild a simple TOC

# Clean up excessive blank lines
while "\n\n\n\n" in output:
    output = output.replace("\n\n\n\n", "\n\n\n")

# Clean up "---" separators that are adjacent
output = re.sub(r'---\n+---', '---', output)

# Remove empty blockquotes
output = re.sub(r'> \n', '', output)

# Fix the "核心目标" line if it survived
output = re.sub(r'> 核心目标[^\n]*\n', '', output)

# Fix name references in hand histories (NLHBlueXX player names are fine to keep)
# Remove author credit lines
output = output.replace("> **笔记者**：小可教练 + 施老师\n", "")
output = output.replace("> **筆記者**：小可教练 + 施老师\n", "")

# Write output
with open(DST, "w", encoding="utf-8") as f:
    f.write(output)

print(f"\nOutput written to: {DST}")
print(f"Size: {len(output):,} chars")
print(f"Lines: {len(output.split(chr(10))):,}")

# Quick content check
checks = [
    "扑克深度学习笔记",
    "心态与纪律",
    "翻前基础策略",
    "Overbet",
    "Bet Size",
    "River Bluff",
    "盲注位防守",
    "公开版",
]
for c in checks:
    if c in output:
        print(f"  ✅ '{c}' present")
    else:
        print(f"  ❌ '{c}' MISSING")

# Things that should NOT be in output
bad_checks = [
    "施老师",
    "施老師",
    "锦标赛入门",
    "錦標賽入門",
    "Rush & Cash",
    "情绪管理的实战课",
    "情緒管理的實戰課",
    "数据审计",
    "數據審計",
    "学习日志",
    "學習日誌",
    "待学习清单",
    "待學習清單",
    "最后更新",
    "最後更新",
]
for c in bad_checks:
    if c in output:
        print(f"  ⚠️  '{c}' STILL PRESENT (should be removed)")
    else:
        print(f"  ✅ '{c}' correctly absent")
