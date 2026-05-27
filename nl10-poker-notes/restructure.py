#!/usr/bin/env python3
"""
Restructure poker-notes-public.md v4 — gap-filling insertion.
"""
import re

MD_PATH = "/Users/ymz/.cola/outputs/扑克笔记-公开版/poker-notes-public.md"

def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# ── New chapter content ──────────────────────────────────────────────

CH2 = """
---

## 2. 资金管理

> **核心原则**：扑克是技术游戏，但资金管理是生存游戏。技术决定你赢多少，资金管理决定你能不能留到赢的时候。

### 2.1 三个账户原则

NL5000 教练的核心框架——三个完全隔离的账户：

| 账户 | 用途 | 规则 |
|------|------|------|
| **日常账户** | 生活开销、房租、吃饭 | 绝对不进扑克。哪怕「就借 2 组明天还」——不行。 |
| **储蓄账户** | 3-6 个月生活费 | **永不碰。** 这不是扑克储备金，是生活最后防线。 |
| **扑克账户** | 专用扑克资金 | 赢了不提、输了不补。独立运行。 |

> 为什么隔离：人的大脑会骗自己。「先从储蓄拿 100 刀，赢回来就还」→ 三周后储蓄少了 500 刀，扑克账户清空。两个账户一起死。

### 2.2 升级降级规则

级别升降不是感觉——是数字。

| 升级条件 | 要求 |
|----------|------|
| NL10 → NL25 | 扑克账户 ≥ 50 buy-ins（$1,250）+ 近 50,000 手正盈利 |
| NL25 → NL50 | 扑克账户 ≥ 50 buy-ins（$2,500）+ 近 100,000 手正盈利 |

| 降级触发 | 动作 |
|----------|------|
| 扑克账户 < 30 buy-ins（当前级别） | 自动降一级 |
| 扑克账户 < 20 buy-ins | 降两级或暂停，强制复盘 |
| 连输 10 buy-ins（任一级别） | **停。** 不看牌。复盘手牌历史。至少 48 小时不碰桌。 |

> 降级不是失败——降级是止损。留在承受不起的级别才是失败。

### 2.3 Shot-taking 策略

想尝试更高级别？可以。但要有规则。

```
准备：3-5 buy-ins 当作「冒险预算」
规则：赢 → 留下的 buy-ins 就是新级别的启动资金
      输光这 3-5 组 → 回原级别。不追、不补、不借。
      一次 shot 期不超过 5 个 session。
```

> Shot-taking 不是升级——是侦察。你的目标不是「在 NL50 稳定盈利」，是「看看 NL50 的人怎么打」。输掉的 3-5 组是你付的学费。

### 2.4 下风期应对

| 行为 | 评价 |
|------|------|
| 追存（输 2 组后加注追） | 🔴 **最差。** 这是在赌今天不崩。 |
| 升级翻本（NL10 输了去 NL25「赢回来」） | 🔴 **自杀。** 级别越大，你的劣势越大。 |
| 加倍桌数（「4 桌输，开 8 桌追」） | 🔴 **加速自杀。** 注意力翻倍稀释，决策品质崩盘。 |
| 暂停 + 复盘 | 🟢 **唯一正确。** 输钱的时候不是你运气差——是你判断力差。 |

> 下风期的定义不是「输了多少组」，是「你开始觉得你该赢了」的那一刻。一旦这个念头出现——**你的判断力已经关了。**

### 2.5 NL10 实战要点

- **55 buy-ins = 健康。** $550 扑克账户打 NL10 = 安全。30 buy-ins 以下 = 危险信号。
- **别动储蓄。** 哪怕你觉得「就差一点就回本了」——那不是回本，是加注送。
- **赢钱了不提。** 扑克账户是工具，不是工资。复利效应在扑克不靠赢率——靠 buy-ins 厚度。
- **每 100 手记录一次账户余额。** 不只是看输赢——看 swing。20 buy-in swing 要停下来问自己：「我在打牌还是在赌？」
"""

CH7 = """
---

## 7. 转牌决策体系

> **核心问题**：翻牌谁都会打——c-bet 是义务。转牌才是分水岭。转牌决定一手的走向：价值收三条街、停枪控池、还是弃牌止损。

### 7.1 Turn Barrel（开第二枪）条件

翻牌 c-bet 被跟，转牌继续打——不是每次都该打。

| 条件 | 为什么 |
|------|--------|
| **牌面 blank**（转牌没改变结构） | 你的翻牌优势还在。低牌白板 = 对手 float 的弱牌没提升。 |
| **你有 equity 或 blocker** | 纯空气 barrel 是自杀。至少有一个 overcard、一张高牌 blocker、或一个 gutshot。 |
| **对手类型合适** | 对手 fold-to-turn-cbet > 50% → barrel 赚钱。对手跟注站 → 别 barrel——他有中对就跟到底。 |
| **你的翻牌范围允许** | 你不能只在有牌时 bet——turn 范围必须两极化：顶端（value）+ 底端（bluff）。中间牌 check 控池。 |

> 核心理念：转牌 bet 不是在「继续翻牌的故事」——是在 **重构你的范围**。翻牌 1/3 pot = 全范围。转牌重注 = 极化的宣言：「我有牌，或者我在装。」

### 7.2 Turn Probe（翻牌全 check → 转牌 bet）

翻牌双方 check，转牌你先打。这种 bet 叫 probe bet。

| 适合 probe | 不适合 probe |
|------------|--------------|
| 转牌是 blank（低牌），你没中但范围有你 | 转牌是高牌（A/K/Q），对手的范围比你更可能 hit |
| 你在位置（IP），对手 check 两次 → capped | 对手是跟注站——probe 是送钱 |
| 你有 equity（overcard/gutshot），被 call 还能赢 | 纯空气 + 对手不弃 = 烧钱 |

**选牌**：你有 A-high blocker → probe。你有小对子 → probe 也很适合（被跟了还有可能 showdown）。KQ on A-high 面 → **别 probe**——A 在对手范围密度太高。

### 7.3 Turn Float（跟翻牌后在转牌偷）

翻牌你 call 对手 c-bet（float），转牌对手 check → 你 bet。

| 适合 float | 不适合 float |
|------------|-------------|
| 你有位置 | OOP float = 死 |
| 对手 c-bet 频率高但 turn barrel 低 | 对手是老手——他的 turn check 可能是 trap |
| 转牌 blank → 你的翻牌 call 看起来像有货 | 转牌 scare card → 对手 check 可能不是示弱 |

**典型场景**：BTN open → BB call。Flop K72r → BTN c-bet 1/3 → BB float with A5s（A-high + backdoor）。Turn blank → BTN check → BB bet 2/3 pot → BTN fold。BTN 翻牌 c-bet = 义务，turn check = 他没 K。

### 7.4 延迟 C-bet（翻牌 check → 转牌 bet）

翻前你 PFR，翻牌你 check，转牌你 bet。

**什么时候用**：翻牌是连接面（JT8 两同花）→ 你 check 控池。转牌 blank → 你 bet。对手的翻牌 check 表示他没强牌（有强牌会 bet 保护）。你的转牌 bet 有额外 fold equity——因为「翻牌 check = 放弃」的思维惯性让对手觉得你不可能有牌。

| 面适合延迟 c-bet | 面不适合 |
|-----------------|---------|
| 连接/湿面，翻牌 check 合理 | 干燥面，翻牌 check 不正常 |
| 转牌 blank | 转牌完成了明显的 draw |

### 7.5 Turn Sizing 逻辑

转牌的 sizing 逻辑和翻牌完全不同。

| Sizing | 什么时候用 | 含义 |
|--------|----------|------|
| **1/3 pot** | 干燥面，你有 thin value（如顶对弱踢脚） | 「我还有牌，但不大」 |
| **2/3 pot** | 标准 turn barrel | 「我的范围极化——你来跟」 |
| **3/4~满 pot** | 你有 monsters（set+），对手有 draw | 「这张票很贵」 |
| **Overbet** | 你有坚果，对手 capped，牌面安全 | 「你中等牌？交出来。」 |

> **翻牌 sizing 看面。转牌 sizing 看范围。** 翻牌是讲范围优势，转牌是讲极化程度。范围越极化 → sizing 可以越大。

### 7.6 Turn 面对 Donk 的应对

转牌对手突然 donk bet。NL10 这是极强的信号。

| 场景 | 行动 |
|------|------|
| 翻牌 check-call → 转牌 donk | **他有东西。** 大概率是翻牌慢打的强牌（set/两对），转牌怕你 check back 错失价值。 |
| 你的牌 = 顶对以下 | **弃。** NL10 转牌 donk 的 bluff 频率 < 5%。 |
| 你的牌 = 超对/TPTK | 看对手。紧弱 → 信有货，弃。松凶 → call 一枪看河牌。 |
| 你的牌 = set+ | Raise。他 donk 说明他有货——你不怕他有货，怕他不跟。 |

> **NL10 铁律**：转牌 donk = 价值 95%。不 bluff-catch。

### 7.7 关于「开池 Miss 后的第二条街防守」

详见第 21 章「特定手牌专题」中 **开池 Miss 后的第二条街防守** 一节。该节专门拆解 AK/AQ/AJ/KQ 在翻牌完全 miss 后，转牌面对反打的决策框架——牌面 × 阻挡 × 对手类型三维交叉。本章覆盖的是广义的转牌进攻体系（barrel/probe/float/延迟 c-bet），那节解决的是防守端的具体决策表。两个方向构成完整的转牌决策闭环。

### 7.8 NL10 实战要点

- **转牌是 NL10 的分水岭。** 多数 NL10 玩家翻牌还行——c-bet 义务大家都会。转牌就不一样了：自动开第二枪的太多、该停不停、该打不打的也太多。
- **Turn check-back 在 NL10 是很强的信号。** 对手翻牌 c-bet 被跟 → 转牌 check → 大概率他 miss。转牌你可以 bet 偷。
- **别在跟注站身上 barrel。** 跟注站的翻牌 call 意味着他有任何东西——中对、底对、A-high 都跟。转牌别试图 bluff 他。
- **低牌面的 turn barrel 是 NL10 的金矿。** 翻牌 237r → c-bet → call。转牌 4 → barrel 2/3 pot。对手的 float 范围全弃。
- **转牌 donk = 尊重它。** NL10 的 turn donk 不存在 bluff。别试图「识破」它。
"""

CH8 = """
---

## 8. 价值下注

> **核心问题**：River Bluff（第 9 章）讲的是怎么诈唬。但 NL10 最大的利润来源不是 bluff——是 **价值下注**。Bluff 赚的是 fold equity，价值下注赚的是他整组。

### 8.1 价值下注三层 Sizing 金字塔

| 层级 | Sizing | 对手的牌力 | 例子 |
|------|--------|----------|------|
| **Thin Value（薄价值）** | 1/3-1/2 pot | 中等牌——比你差但可能会跟一枪 | A83r 上 AK vs 对手的 A2-A7 |
| **Moderate Value（中等价值）** | 2/3-3/4 pot | 二线强牌——他想跟但感到压力 | 两对 vs 对手的顶对 |
| **Fat Value（肥价值）** | Pot-Overbet | 强牌——他愿意付整组 | Set/顺子 vs 对手的超对/两对 |

> 翻牌 → moderate/fat value。转牌 → thin/moderate（看面）。河牌 → thin value 为主（强牌已经建完池了）。

### 8.2 榨取性 Value Sizing

不是每手牌都该 GTO sizing。根据对手类型调：

| 对手类型 | Value Sizing 调整 | 理由 |
|---------|-----------------|------|
| **跟注站 (Call Station)** | **+30-50% sizing** | 他对 sizing 不敏感。$0.30 和 $0.50 他跟的频率一样。打大。 |
| **NIT (紧弱)** | **标准或稍小** | 他有牌才跟。打大只会吓跑他。小注收他的弃牌权。 |
| **LAG (松凶)** | **正常**，偶尔 check-raise | 他会自己 bet。设套比追打更赚。 |
| **Reg (TAG)** | **混合**（GTO 标准） | 对他不能单一 sizing——会被读。 |

**跟注站的金矿**：你中 TPTK，他中对。GTO 说 bet 2/3 pot。对跟注站 bet **满 pot**。他的中对不会因为你的 sizing 改变决定——但他的损失翻倍了。

### 8.3 Value Bet vs Check-Back 决策树

河牌你 IP，对手 check。Bet 还是 check？

```
「比我差的会不会跟？」

会 → bet。
  他差到什么程度？
  → 弱牌（中对/底对）→ thin value 1/3 pot
  → 中等牌（TP weaker kicker）→ moderate value 1/2-2/3 pot
  → 强牌但比你差 → fat value 3/4-满 pot

不会 → check back。
  → bet 不是为了「赢底池」，是为了被比你差的牌跟。
  → 「我 bet 他可能弃」→ 那 check。check 也能赢底池。
  → 「我 bet 他可能 raise」→ 看人。NIT raise = 你死。LAG raise = 可能 bluff。
```

> 最常见的漏：拿着 TPTK 在 scare card river bet 薄价值，被 raise，不知道该怎么办。**解法**：scare card river → 你的 TPTK 降级为 bluff-catcher。Check back。别 bet。

### 8.4 多人底池的 Value Sizing

| 人数 | Value Sizing | 逻辑 |
|------|-------------|------|
| Heads-up | GTO 标准：1/3-满 pot 视情况 | 单挑，你的 thin value 能收 |
| 3-way | **+20-30% sizing** | 需要给第一个人弃牌的理由，第二个人才能单独决策。 |
| 4-way+ | **大注为主（2/3+）** | 多人 = 更有可能有人中了一点东西。别打小注。 |

### 8.5 NL10 实战要点

- **价值下注是 NL10 最大的利润来源。** Bluff 在 NL10 不稳定——对手 call 太多。但 value bet 是稳的——对手 **跟太多** 才是你赚钱的地方。
- **鱼付到满。** 跟注站/娱乐玩家 vs 你的 set → bet bet bet，河牌 overbet。他们的 AA/顶对/两对跟到死。
- **NIT 身上别贪。** NIT 的 fold button 很灵敏。你的 nuts vs NIT → bet 正常 size（2/3 pot），别 overbet。你宁可少赢 10bb 也别把他吓跑。
- **河牌 thin value 是 NL10 的高级技能。** 多数 NL10 reg 要么 check back 太多（漏 value），要么 bet-fold 做不好（被 raise 不知道弃）。练好 thin value bet-fold 是你从 breakeven 到 3bb/100 的关键。
- **Donk bet 面前的价值保护**：对手 donk → 你有强牌就 raise，别慢打。NL10 donk = 他有货→他能跟 raise。
"""

CH10 = """
---

## 10. 多人底池策略

> **核心问题**：NL10 最大的结构性偏差——多人底池频率极高。鱼不弃，reg 要隔离但不够频繁。你要么学会打多人底池，要么在 NL10 被拖死。

### 10.1 翻前策略：3-way/4-way 调整

| 场景 | 调整 |
|------|------|
| **Limper 在场** | ISO raise 3-4bb + 1bb per limper。别用 2.5bb——那是在邀请更多 call。 |
| **前面有 caller，你在后位** | Squeeze 频率翻倍。多人底池 OOP = 地狱。Squeeze or fold——别 cold-call。 |
| **你是 PFR，后面有三个人 cold-call** | 范围缩紧。UTG/HJ 只用 premium 开。别用投机牌——多人底池 OOP + 多人 = 必亏。 |
| **盲注位防守多人** | BB 面对多 caller → 只防守有坚果潜力的牌（同花 Ax、小对子 set mine、大对子）。KJo/QTo = instant fold。 |

> 翻前纪律在多人底池里比单挑重要十倍。一手错误的 cold-call 在 4-way pot 能漏你半组。

### 10.2 翻后调整

| 原则 | 说明 |
|------|------|
| **C-bet 频率大幅降低** | 单挑 c-bet 70%+。3-way c-bet 降到 40%。4-way 降到 25%。 |
| **C-bet sizing 增大** | 1/3 pot 在多人底池是自杀——第一个人跟了，后面的人有更好的赔率。最小 2/3 pot。 |
| **Check 的频率远超单挑** | 你 miss 了？check。不是示弱——是数学。四个人 = 大约 60%+ 的概率有人击中了翻牌。 |
| **Draw 的玩法完全变化** | 单挑 draw = 半诈唬。多人 draw = 看赔率，别乱推。你的 fold equity 在 3-way/4-way 接近零。 |

### 10.3 牌力需求变化

| 单挑 | 3-way | 4-way |
|------|-------|-------|
| TPTK = 强牌，三条街价值 | TPTK = 中等牌——有人可能有 set | TPTK = **谨慎**——大概率落后至少一个人 |
| 超对 = 接近坚果 | 超对 = 强牌但不稳 | 超对 = 怕 set + 怕两队 |
| 两对 = 怪兽 | 两对 = 强 value，但要小心顺子 | 两对 = 仍然强但被 cooler 概率高 |
| 中对 = 可 bluff-catch | 中对 = **fold to any aggression** | 中对 = 秒弃 |

> **核心公式**：牌力缩水 = 1 / √(人数)。4-way pot → 你的 TPTK 价值大约只剩单挑的 50%。

### 10.4 Draw 的赔率陷阱

在多人底池，draw 的隐含赔率看起来好（人多 = 有人会付你的中牌）——但反向隐含赔率暴增。

| 陷阱 | 说明 |
|------|------|
| **花 draw 被高花碾压** | 3-way pot，你的 7♠6♠ 翻中同花 draw。另一个 caller 可能拿着 A♠X♠——你中了就是送死。 |
| **顺子 draw 被更高的顺子碾压** | JT8 面，你拿 Q9 两头顺。K9 也在等——你中了 K9 也中了。 |
| **Set-over-set** | 3-way pot 翻牌你中 set ~12%。另一个人也中 set ~12%。同时发生 ~1.4%——但发生时你清空。 |

> 多人底池的 draw 玩法：**优先选坚果方向的 draw。** 非坚果 draw → fold。不是 -EV 的问题——是你不知道中牌后是不是领先。

### 10.5 NL10 实战要点

- **NL10 多人底池极常见。** 鱼不弃 = 你 open 2.5bb → 3 个人跟。这不会变——这就是 NL10 的生态。
- **ISO 要大。** 2.5bb 开池不够——鱼会跟任何 2.5bb。有 limper → 4-5bb ISO。有多个 limper → 5-7bb。
- **翻后别自动 c-bet。** 单挑 c-bet = 习惯。多人 c-bet = 错误。miss 就 check——这是数学。
- **TPTK 在 3-way = 控池为主。** 别三枪打光。一枪翻牌、转牌 check、河牌看对手行动。
- **Nuts 不要慢打。** 多人 = 更有可能有人在追。你的 set/顺子 → bet 或 check-raise。NL10 的多人底池是 draw 重灾区。
"""

CH12 = """
---

## 12. 牌桌选择

> **核心认知**：「坐对桌比翻前范围精确 1% 重要得多。」你在 1bb/100 的边缘桌上把一个 leak 修成 GTO 完美——多赚 0.3bb/100。你换到有两条鱼的桌——直接多赚 5bb/100。**牌桌选择是 NL10 最大的 leverage。**

### 12.1 快速扫桌方法

开 lobby，按 **VPIP 排序**。30 秒判断一张桌：

| 信号 | 鱼桌 ✅ | 差桌 ❌ |
|------|---------|---------|
| VPIP 平均值 | > 30% | < 22% |
| 有玩家 VPIP > 40% | 至少 1 个 → 🐟 | 0 个 |
| PFR / VPIP gap | 有人 gap > 15%（limp-call 型） | 所有人 gap < 4% |
| 平均底池大小 | 明显偏大 | 正常或偏小 |
| Players/flop | > 35% | < 25% |

**实战口诀**：看到有人 VPIP 50%+ → 马上坐下。看到全桌 VPIP 22/18 → 换。

### 12.2 座位选择

| 位置 | 评分 | 理由 |
|------|------|------|
| 鱼在右（你有位置） | ⭐⭐⭐⭐⭐ **理想** | 他在前面行动，你每次都能在他之后决定。他 limp → 你 ISO。他 bet → 你 IP 可以 float/raise。 |
| 鱼在左 | ⭐⭐ | 他在你之后行动。你 open → 他 call → 你 OOP 猜谜。他有位置优势。 |
| 鱼正对面 | ⭐⭐⭐ | 翻前调整范围——你在前位收紧，后位放宽。 |

> **Waitlist 策略**：等鱼右边的座位。不在鱼左边的位坐下——哪怕桌上有鱼，OOP 打鱼也不好赚。

### 12.3 坏桌信号

| 信号 | 为什么坏 |
|------|---------|
| **3+ 短码（< 50bb）** | 短码策略赌性重，波动大。有效筹码不够深 = thin value 收不到、bluff 没 fold equity。 |
| **全桌 VPIP < 20%** | 没鱼。大家都是 reg/bot。你的 edge 只有小数点的 EV——不如换桌。 |
| **Waiting list 全是 reg** | reg 扎堆等一张桌——要么鱼刚走，要么鱼不在。 |
| **翻前 3-bet 频率异常高** | 说明桌上有 LAG/maniac。你可以利用他——但波动更大。自己判断。 |

### 12.4 换桌节奏

```
开 4 桌 → 每 30 分钟扫一次 lobby（在 45/15 的 15 分钟休息里做）
          → 有鱼的新桌？→ 停掉最差的那桌，换过去。
          → 某桌的鱼走了？→ 马上 sit out。别留恋。
```

> 不要忠诚于一张桌。忠诚于你的 win rate。鱼走了 = 你的 edge 消失了 = 换。

### 12.5 选站逻辑（平台与抽水）

来自 NL5000 教练视频的低级别核心理念：

| 因素 | 对 NL10 玩家的影响 |
|------|-----------------|
| **抽水结构** | NL10 的抽水吃掉你大部分盈利。不同平台抽水差异巨大。GG 抽水偏高但有 leaderboard 和返水。PartyPoker 抽水低但池子小。 |
| **玩家池大小** | 池子大 = 鱼多 = 更多软桌可选。池子小 = 你只能打 reg 内战。 |
| **返水/Rakeback** | 如果你 win rate ~3bb/100，rake 可能吃掉 8-10bb/100。Rakeback 是你真实盈利的重要部分。 |

**NL10 实用建议**：选低抽水平台 > 选高返水平台 > 选「看起来很酷」的平台。GG Poker 的抽水虽然高，但 NL10 鱼密度是最高的——综合性价比仍然最优。

> 视频金句：「低级别看抽水结构，高级别看对手。NL500 往上，抽水已经不是问题——你的 win rate 远大于 rake。但 NL10——你的真实盈利大头可能被抽水偷掉。」

### 12.6 NL10 实战要点

- **坐对桌比 GTO 精确重要 10 倍。** 你在 22/18 的全 reg 桌上打 GTO 完美 = 微利。你在有两条鱼的桌上犯两个 GTO 错 = 仍然大赚。
- **VPIP 40%+ = 坐下。** 不需要分析更多。VPIP 40% 的玩家在 NL10 就是送钱的。
- **鱼走了你也走。** 桌上有鱼 → 打。鱼走了 → 换下一张。你不是来挑战 reg 的——你是来收鱼的。
- **短码多 = 换。** 3 个以上短码 = 有效筹码不够 = 你的技术优势被浅筹码强行抹平。
- **Waitlist 可以当情报。** 如果等待列表清一色 reg 标签 = 那张桌的鱼刚走。跳过。
"""

NEW_CHAPTERS = {2: CH2, 7: CH7, 8: CH8, 10: CH10, 12: CH12}

HEADING_RENAMES = [
    ("## 2. 翻前基础策略", "## 3. 翻前基础策略"),
    ("## 3. 翻前范围详解", "## 4. 翻前范围详解"),
    ("## 4. 翻后牌面分类与打法", "## 5. 翻后牌面分类与打法"),
    ("## 5. 核心概念深度解析", "## 6. 核心概念深度解析"),
    ("## 6. NL10 线上实战调整", "## 11. NL10 线上实战调整"),
    ("## 7. 关键手牌回顾", "## 附录A：关键手牌回顾"),
    ("## 8. 关键数字速查表", "## 附录B：关键数字速查表"),
    ("## 9. 进阶：玩家分类与针对性策略", "## 13. 进阶：玩家分类与针对性策略"),
    ("## 10. 公共牌阻挡效应（Board Blockers）", "## 14. 公共牌阻挡效应（Board Blockers）"),
    ("## 11. 手牌选择与隐含赔率", "## 15. 手牌选择与隐含赔率"),
    ("## 12. 大牌翻后透明化与翻前纪律", "## 16. 大牌翻后透明化与翻前纪律"),
    ("## 13. Overbet 与防 Overbet", "## 17. Overbet 与防 Overbet"),
    ("## 14. Bet Size 即语言：從讀牌到讀人", "## 18. Bet Size 即语言：從讀牌到讀人"),
    ("## 15. 牌面分類 × 底池類型 + SB vs BB 範圍", "## 19. 牌面分類 × 底池類型 + SB vs BB 範圍"),
    ("## 16. BB/SB 盲注位防守系統", "## 20. BB/SB 盲注位防守系統"),
    ("## 17. 特定手牌專題 — 邊緣牌的攻防", "## 21. 特定手牌專題 — 邊緣牌的攻防"),
    ("## 18. River Bluff — 什麼時候轉詐唬", "## 9. River Bluff — 什麼時候轉詐唬"),
]

# Map old chapter number → new chapter number for sub-section renumbering
SECTION_CHAPTER_MAP = {
    2: 3, 3: 4, 4: 5, 5: 6, 6: 11,
    9: 13, 10: 14, 11: 15, 12: 16,
    13: 17, 14: 18, 17: 19, 18: 20,
    19: 21, 20: 9,
}

def extract_chapter_num(heading_line):
    m = re.match(r'^## (\d+)\.', heading_line)
    return int(m.group(1)) if m else 999

def main():
    content = read_file(MD_PATH)
    original_len = len(content)
    print(f"Original: {original_len:,} chars")
    
    # ── Step 1: Renumber headings ──
    for old, new in HEADING_RENAMES:
        content = content.replace(old, new)
    
    # ── Step 2: Renumber sub-sections (single pass, no cascading) ──
    def renumber_subsections(content):
        """Renumber ###/#### OLD.N → ###/#### NEW.N using SECTION_CHAPTER_MAP."""
        def replace_match(m):
            old_ch = int(m.group(2))
            section_rest = m.group(3)
            new_ch = SECTION_CHAPTER_MAP.get(old_ch, old_ch)
            return f"{m.group(1)} {new_ch}{section_rest}"
        # Match ### N.xxx and #### N.xxx
        return re.sub(r'^(#{2,4}) (\d+)(\.\d+.*)', replace_match, content, flags=re.MULTILINE)
    content = renumber_subsections(content)
    
    # ── Step 3: Parse into sections ──
    lines = content.split("\n")
    
    # Find H1 end
    h1_end = 0
    for i, line in enumerate(lines):
        if line.startswith("# ") and not line.startswith("## "):
            h1_end = i + 1
            break
    
    pre_header = lines[:h1_end]
    
    # Extract all ##-headed sections (numbered chapters + appendices)
    # A section is: heading_line + content until next ## heading
    all_sections = []  # (heading, start_idx, end_idx)
    current_heading = None
    current_start = h1_end
    
    for i in range(h1_end, len(lines)):
        line = lines[i].rstrip()
        if re.match(r'^## ', line):
            if current_heading is not None:
                all_sections.append((current_heading, current_start, i))
            current_heading = line
            current_start = i
    
    if current_heading is not None:
        all_sections.append((current_heading, current_start, len(lines)))
    
    # Separate numbered chapters (## N.) from appendices
    numbered = []
    appendices = []
    
    for heading, start, end in all_sections:
        if re.match(r'^## \d+\.', heading):
            numbered.append((heading, start, end))
        else:
            appendices.append((heading, start, end))
    
    # Sort numbered chapters
    numbered.sort(key=lambda x: extract_chapter_num(x[0]))
    
    # ── Step 3.5: Fix stale cross-references in original content ──
    content = content.replace(
        "> **核心問題**：17.8 講了什麼時候 value bet。現在講另一半——你 miss 了，什麼時候該轉 bluff？",
        "> **核心問題**：第 8 章「价值下注」講了什麼時候 value bet。現在講另一半——你 miss 了，什麼時候該轉 bluff？"
    )
    
    # ── Step 4: Build output with gap-filling ──
    output_lines = list(pre_header)
    
    for idx, (heading, start, end) in enumerate(numbered):
        ch_num = extract_chapter_num(heading)
        
        # Output current chapter
        output_lines.extend(lines[start:end])
        
        # Determine next existing chapter number
        if idx + 1 < len(numbered):
            next_existing = extract_chapter_num(numbered[idx + 1][0])
        else:
            next_existing = 999  # no more chapters
        
        # Fill gaps: for each N between ch_num+1 and next_existing-1
        for gap_num in range(ch_num + 1, next_existing):
            if gap_num in NEW_CHAPTERS:
                output_lines.append("")
                output_lines.append(NEW_CHAPTERS[gap_num].strip())
                output_lines.append("")
                print(f"  ✅ Inserted new Ch{gap_num} after Ch{ch_num}")
    
    # Add appendices
    for heading, start, end in appendices:
        output_lines.append("")
        output_lines.extend(lines[start:end])
    
    # ── Step 5: Write ──
    result = "\n".join(output_lines)
    
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(result)
    
    print(f"\nFinal: {len(result):,} chars (was {original_len:,})")
    
    # Verify
    chapter_headings = re.findall(r'^## (\d+\. .+)$', result, re.MULTILINE)
    print(f"Numbered chapters: {len(chapter_headings)}")
    for h in chapter_headings:
        print(f"  {h}")
    
    appendix_headings = re.findall(r'^(## 附录.+)$', result, re.MULTILINE)
    print(f"Appendices: {len(appendix_headings)}")

if __name__ == "__main__":
    main()
