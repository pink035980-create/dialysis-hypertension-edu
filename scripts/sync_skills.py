import os

project_init_content = '''---
name: project-init
description: 專案初始化技能（三層級自動偵測）。當使用者說「初始化專案」、「專案初始化」、「幫這個專案做初始化」、「開新專案」、「建立專案藍圖」、「幫我 init 專案」等要為當前資料夾建立專案基礎建設的請求時，請一定要使用此技能。本技能會依這台電腦的工具鏈自動建到最高可用層級：L1 本地（AGENTS.md + handoff.md）→ L2 GitHub（git init + 私有 repo）→ L3 Obsidian（專案詳細筆記與 ADR）。
---

# 專案初始化技能（三層級自動偵測）

## 設計理念

一套技能、三個層級。**這台電腦裝了什麼工具，就自動建到哪個層級**——不用問使用者「你要第幾層級」。

三層資訊的定位與讀取頻率不同：

| 層級 | 平台 | 建立的東西 | 讀取時機 |
|------|------|-----------|---------|
| L1 本地 | 專案資料夾（建議放 GDrive 或本機純實體目錄） | `AGENTS.md`（專案藍圖）＋`handoff.md`（交接檔） | **每個 session 都讀** |
| L2 GitHub | 私有 repo (`pink035980-create`) | git 版本控制＋雲端備份 | 指定才讀 |
| L3 Obsidian | 第二大腦 vault (`~/second-brain/`) | `專案工作流程.md`（詳細筆記與 ADR） | 開工檢閱 ADR、收工追加 |

> 為什麼藍圖叫 `AGENTS.md` 而不是 `CLAUDE.md`？因為 AGENTS.md 是跨 Agent 開放標準——Claude Code、Codex/ChatGPT、Gemini CLI/AntiGravity 2、OpenCode 都讀得懂。專案層的檔案刻意用開放格式，任何 Agent 接手都能無縫工作。

## 層級偵測（初始化看「這台電腦」有什麼）

依序檢查，決定本次能建到第幾層級：

1. **L1**：無條件可建
2. **L2**：跑 `gh auth status`，成功（已登入 GitHub CLI）→ 可建
3. **L3**：本機有 `~/second-brain` 快捷目錄或 Obsidian MCP 可用 → 可建

檢查完先告訴使用者：「這台電腦可初始化至第 N 層級」，再開始執行。

## 初始化 SOP（依序執行）

### L1：本地藍圖（永遠執行）

1. **掃描資料夾現況**：列出既有檔案，若已有 `AGENTS.md` 或 `handoff.md` → 停下來問使用者是否要覆蓋
2. **詢問使用者**：專案名稱、一句話目標、關鍵時程（沒有就留白，不要硬編）
3. **建立 `AGENTS.md`**：用範本為底，填入實際內容；「資料夾結構」區塊由掃描結果自動生成
4. **建立 `handoff.md`**：用範本為底，「目前做到哪」填「專案初始化完成」，更新者填 Agent 名＋電腦名（PowerShell 用 `$env:COMPUTERNAME` 取得）
5. 若路徑含「雲端硬碟」或「My Drive」→ 提醒使用者確認 Google 雲端硬碟桌面版的同步圖示已打勾（檔案要真的躺在雲端，換電腦才拿得到）

### L2：GitHub（gh 已登入才做，否則跳過並註明）

6. **git 初始化**：
   ```bash
   git init
   git config user.email "pink035980@gmail.com"
   git config user.name "pink035980-create"
   git config windows.appendAtomically false   # GDrive 上跑 git 的必要設定，避免寫入錯誤
   ```
7. **建立 `.gitignore`**（GDrive / 本地專用）：
   ```
   desktop.ini
   *.tmp
   ~$*
   .env
   *.key
   credentials.*
   ```
8. **初始 commit**：`git add .` → `git commit -m "初始化專案：<專案名稱>"`
9. **建立私有 repo**：問使用者偏好的英文 repo 名，確認後：
   ```bash
   gh repo create pink035980-create/<repo-name> --private --source=. --push
   ```
10. **回填 `AGENTS.md`** 同步層級表的 GitHub 欄（repo 網址）

### L3：Obsidian 第二大腦（可透過本機捷徑或 MCP 執行）

11. 優先檢查本機第二大腦快捷目錄 `%USERPROFILE%\second-brain`（或 `~/second-brain`），若存在則直接建立與專案**同名**的資料夾；若無快捷目錄但有 Obsidian MCP（`mcp__obsidian__*`）可用，則透過 MCP 建立。兩者皆無時跳過並註明。
12. 建立 `<資料夾名>/專案工作流程.md`，內容包含：專案背景與詳細脈絡、架構與決策紀錄 (ADR)、素材與相關筆記連結、🕳️ 踩坑筆記、🗓️ 最近更動紀錄表格（第一行寫今天的初始化）。
13. **回填 `AGENTS.md`** 同步層級表的 Obsidian 欄（`~/second-brain/<資料夾名>/專案工作流程.md`）。

### 回報

給使用者一個層級 checklist：

```
🏗️ 本專案初始化至第 N 層級
✅ L1 本地：AGENTS.md ＋ handoff.md
✅ L2 GitHub：pink035980-create/<repo>（私有）
✅ L3 Obsidian：~/second-brain/<專案>/專案工作流程.md
```

## 不該做的事

- ❌ 未經確認就覆蓋既有的 `AGENTS.md`／`handoff.md`
- ❌ 電腦沒 gh／Obsidian 時報錯中斷（正確行為：跳過該層級、在回報中註明原因）
- ❌ 把 `.env`、API key 之類敏感檔 commit 進 git
- ❌ 建 public repo（預設一律 private，使用者明說才轉公開）

## 注意事項

- 所有訊息與檔案內容使用**繁體中文**
- 之後的日常循環交給搭檔技能：開工（startup）讀、收工（shutdown）寫
'''

startup_content = '''---
name: startup
description: 開工接續助手（三層級自動偵測）。當使用者說「開工」、「開始工作」、「我來了」、「上次做到哪」、「我們繼續」、「接下來呢」、「接續工作」、「來吧」等任何要接續上次工作的請求時，請一定要使用此技能。本技能會讀取 agents.md 專案藍圖與 handoff.md 交接檔、檢查 git 狀態（含遠端 fetch）、檢閱 Obsidian 第二大腦歷次決策 (ADR)、辨識上次是否在另一台電腦收工、建議下一步該做什麼。
---

# 開工接續助手（三層級）

新對話開始時，幫使用者快速進入「上次做到哪」的脈絡，避免從零開始解釋。

## 核心原則

1. **開工是「讀」、收工是「寫」**——本技能只讀、只報告，不改任何檔案
2. **不主動 `git pull`**（避免覆蓋本地未 commit 變動，只提醒「要不要 pull」）
3. **30 分鐘內 fetch 過就跳過**（避免單台多對話冗餘）
4. **主動檢閱 Obsidian 第二大腦**——檢閱 `~/second-brain/<專案名稱>/專案工作流程.md` 中的 ADR 與踩坑紀錄，避免重複決策
5. 跟收工（shutdown）技能是**對偶關係**：收工存進去、開工讀出來

## 層級偵測（開工看「這個專案」建到哪層）

- **L1**：專案有 `AGENTS.md`／`handoff.md` → 讀
- **L2**：專案有 `.git` → 做 git 檢查
- **L3**：專案在 Obsidian 第二大腦（`~/second-brain/<專案名稱>/專案工作流程.md`）有筆記檔或登記於 `AGENTS.md` → 檢閱歷次決策與踩坑

## 開工 SOP（依序執行）

### L1：讀藍圖與交接檔（永遠執行）

1. **讀 `AGENTS.md`**：專案目標、路線圖進度、工作約定（摘要，不全文倒出）
2. **讀 `handoff.md`**：上次做到哪、目前狀態、下一步、注意事項
3. **檢查「最後更新」欄**：
   - 若**更新者的電腦名 ≠ 這台電腦**（PowerShell 比對 `$env:COMPUTERNAME`）→ 特別標示「⚠️ 上次在另一台電腦（名稱）收工」，並確認同步已完成（看 handoff.md 檔案時間戳是否吻合；若本地檔案明顯過舊，提醒等同步完再開工）
   - 若 handoff.md 的更新時間比 agents.md 舊很多 → 提醒「上次可能沒有正式收工」

**Fallback（舊專案相容）**：若專案沒有 `AGENTS.md`／`handoff.md`：
- 改讀 `~/second-brain/<專案名稱>/專案工作流程.md` 的「上次做到哪」段
- 讀完提議：「這個專案還沒有 agents.md＋handoff.md，要不要用『初始化專案』補建？」（提議即可，不主動建）

### L2：git 檢查（專案有 `.git` 才做）

4. **本地狀態**：`git status --short`
   - clean → 「本地工作區乾淨」
   - 有未 commit 變動 → 列出，提醒「上次有未完成的修改，要繼續還是放棄？」
5. **遠端狀態**（30 分鐘判斷）：
   - 遠端有新 commit 時，提醒「遠端有新 commit，要 `git pull` 嗎？」**不主動 pull**
6. **交叉比對防呆**：若 handoff.md 寫「Git push：✅」但遠端沒有對應的新 commit → 警告「上次收工可能沒推成功，建議先確認再動工」

### L3：Obsidian 第二大腦（主動檢閱 ADR 與防踩坑約定）

7. 若本機 `~/second-brain/<專案名稱>/專案工作流程.md` 存在（或已在 `AGENTS.md` 登記）：
   - 主動檢視該筆記的「架構與臨床決策紀錄 (ADR)」與「🕳️ 踩坑筆記」，將既有架構脈絡與防踩坑約定納入當前 Session，不重複向使用者提問已決策的事項。
   - 在開工報告中標註「🧠 Obsidian：`~/second-brain/<專案名稱>/專案工作流程.md`（已檢閱歷次 ADR 與踩坑筆記）」。

### 報告 + 建議下一步

給使用者**結構化摘要**（保持精煉）：

```
📂 專案：<資料夾名>（第 N 層級）
📘 上次做到哪：<handoff 摘要 1-2 句>（<時間>，<更新者> @ <電腦名>）
🔧 本地 git：<clean｜有 N 個未 commit 變動｜—（L1 專案）>
🌐 遠端：<最新｜落後 N commits，建議 git pull｜—>
🧠 Obsidian：<筆記路徑，已掌握歷次 ADR 與避坑規範｜—>
➡️ 建議下一步：
   1. <handoff「下一步」第 1 項>
   2. <可選：第 2 項>

要從哪個方向開始？
```

最後**等使用者選方向**，不要自己擅自繼續。

## 不該做的事

- ❌ 主動 `git pull`（會撞本地未 commit 變動）
- ❌ 修改 `AGENTS.md`／`handoff.md`／Obsidian 筆記（那是收工的事）
- ❌ 沒有交接檔時硬建一個（先問使用者）
- ❌ 把藍圖與交接檔內容**全文倒出來**（要摘要、保持精簡）

## 與收工（shutdown）的對偶關係

| 面向 | 收工 | 開工 |
|------|------|------|
| 主要動作 | 摘要今天做什麼 | 摘要上次做什麼 |
| agents.md / handoff.md | **寫入** | **讀出** |
| Git 動作 | add + commit + push | status + fetch（不 pull） |
| Obsidian | 寫詳細紀錄與 ADR | 檢閱 ADR 與踩坑脈絡 |
| 對外副作用 | 推 GitHub、改檔案 | **無**（只讀、只報告） |

## 注意事項

- 所有訊息使用**繁體中文**
'''

shutdown_content = '''---
name: shutdown
description: 收工同步助手（三層級自動偵測）。當使用者說「收工」、「結束了」、「下班」、「準備換電腦」、「同步」、「先到這裡」、「換電腦繼續做」等任何要結束工作並保存進度的請求時，請一定要使用此技能。本技能會更新 agents.md 進度與 handoff.md 交接檔、git commit + push、把詳細紀錄與 ADR 寫進 Obsidian 第二大腦、同步更新本機三大 Agent 與 chezmoi dotfiles，確保下次（或在另一台電腦、或換一個 Agent）打開能無縫接續。
---

# 收工同步助手（三層級）

對話結束前，把這次的工作保存到專案建到的每一層：

| 層級 | 收工動作 | 給誰看 |
|------|---------|--------|
| L1 本地 | 更新 `AGENTS.md` 進度＋改寫 `handoff.md` | 下一個 session 的任何 Agent、任何電腦 |
| L2 GitHub | commit + push | 版本歷史＋雲端備份 |
| L3 Obsidian | 詳細紀錄與 ADR 寫進 `專案工作流程.md` | 未來需要完整脈絡的自己與接手 Agent |
| L4 全域同步 | chezmoi dotfiles 備份三大 Agent 技能 | 跨電腦、跨 Agent 技能完全一致 |

## 核心原則

1. **開工是「讀」、收工是「寫」**——handoff.md 是收工的必寫項，這是跨電腦／跨 Agent 交接的生命線
2. **不在 vacuum 中執行**——先從對話脈絡盤點今天做了什麼
3. **只動需要動的**——沒實質進度（只是問問題、沒改檔案）就不跑同步
4. **有疑問先問人**——commit 前先給訊息草稿等點頭；不確定要不要 add 的檔案先問
5. **精簡與詳細分家**——handoff.md 只放交接必需資訊，完整脈絡（決策原因 ADR、踩坑細節）寫 Obsidian，兩邊不重複

## 層級偵測（收工看「這個專案」建到哪層）

- **L1**：專案有 `AGENTS.md`／`handoff.md` → 更新（沒有就提議先跑「初始化專案」）
- **L2**：專案有 `.git` → commit + push
- **L3**：本機有 `~/second-brain/<專案名稱>/專案工作流程.md` 或 MCP 可用 → 追加詳細紀錄與 ADR
- **L4**：有技能、全域規則檔變動 → 執行 chezmoi 納管與推送

## 收工 SOP（依序執行）

### L1：更新藍圖與交接檔（永遠執行）

1. **盤點本次成果**：從對話歷史摘要——完成了哪些檔案、做了什麼決定、踩了什麼坑
2. **更新 `AGENTS.md`**：
   - 路線圖 checklist：勾掉完成項、新增發現的待辦
   - 「資料夾結構」有新增檔案就補
3. **改寫 `handoff.md`**（整份重寫，不是往下堆）：
   - ⏯️ 目前做到哪：本次最後完成的動作
   - 🚦 目前狀態：可運行？哪些做一半？
   - ➡️ 下一步：具體、可執行的 1-3 項
   - ⚠️ 注意事項：新踩的坑、暫時 workaround
   - 🕐 最後更新：時間＋更新者（Agent 名 @ `$env:COMPUTERNAME`）＋ Git push 狀態（先寫「待推」，L2 完成後回填）

### L2：git 同步（專案有 `.git` 才做）

4. `git status --short` 看變動 → 擬**繁體中文** commit 訊息（標題：動詞＋對象；正文 3-5 條 bullet 描述變動＋為什麼）→ **給使用者過目，點頭再 commit**
5. commit → `git push`
6. **回填 handoff.md 的 Git push 欄**：成功 → `✅ 已推`；失敗 → `❌ 未推（原因）`，並在回報中標紅提醒（沒推成功，另一台電腦就拿不到 GitHub 備份）
7. 不要 add：`.claude/`、`.codex/`、`.env`、API key、untracked 的不明新檔（先問）

### L3：Obsidian 第二大腦詳細紀錄（永遠寫入第二大腦）

8. 更新 `~/second-brain/<專案名稱>/專案工作流程.md`（或透過 Obsidian MCP）：
   - 「🗓️ 最近更動紀錄」表格：追加一行（日期＋維護者＋變更摘要＋成果狀態）
   - 「🕳️ 踩坑筆記」：有新踩到的坑或重要防禦技巧（如 Pillow 文字溢出、FFmpeg 避讓、雲端鎖定）立即追加
   - 「架構決策紀錄 (ADR)」：本次做了什麼重要架構或設計取捨、為什麼
9. 表格超過 30 行 → 提醒使用者歸檔到 `歷史日誌.md`

### L4：全域 Agent 技能同步與 chezmoi 納管（每次收工必做）

10. **跨 Agent 三口令技能同步**：
    - 每次收工時，一併同步更新本機所有 Agent（Claude Code、ChatGPT/Codex、AntiGravity 2）以及 Obsidian 第二大腦中的專案三口令（初始化專案、開工、收工）技能與手冊，確保四大平台技能定義與規格完全一致。
11. **無縫交接 handoff.md**：
    - 確保 `handoff.md` 清楚詳盡列出「接手 Agent 下一步要做什麼」、目前狀態與踩坑注意事項，讓後續接手的其他 Agent 能立即精準接續。
12. **chezmoi 自動更新與同步**：
    - 將改動的技能檔或規則檔同步至 `~/.local/share/chezmoi`
    - 執行 git 提交與推送：`git -C ~/.local/share/chezmoi commit && push` 至 GitHub 私有 dotfiles 倉庫。

### 回報（層級 checklist）

```
✅ L1 本地：AGENTS.md 進度已更新、handoff.md 已改寫（更新者：<Agent> @ <電腦名>）
✅ L2 GitHub：<repo> 已 commit + push（<commit 標題>）
✅ L3 Obsidian：~/second-brain/<專案>/專案工作流程.md 已補紀錄與 ADR
✅ L4 全域同步：四大 Agent 三口令與 chezmoi dotfiles 已同步至 GitHub
```

## 不該做的事

- ❌ 對「沒實質進度」的對話也跑同步
- ❌ 沒更新 handoff.md 就收工（那是下次開工的唯一線索）
- ❌ commit message 寫「更新」、「修改」這種沒資訊的字
- ❌ 自動 add untracked 的新檔或敏感檔（要使用者確認）
- ❌ 把該寫進 Obsidian 的長篇細節塞進 handoff.md（交接檔要保持一頁內讀完）

## 與開工（startup）的對偶關係

| 面向 | 收工 | 開工 |
|------|------|------|
| agents.md / handoff.md | **寫入** | **讀出** |
| Git 動作 | add + commit + push | status + fetch（不 pull） |
| Obsidian | 寫詳細紀錄與 ADR | 檢閱 ADR 與踩坑脈絡 |
| 對外副作用 | 推 GitHub、改檔案 | 無 |
'''

home = os.path.expanduser('~')

targets = [
    # 1. Claude Code
    (os.path.join(home, '.claude', 'skills', 'project-init', 'SKILL.md'), project_init_content),
    (os.path.join(home, '.claude', 'skills', 'startup', 'SKILL.md'), startup_content),
    (os.path.join(home, '.claude', 'skills', 'shutdown', 'SKILL.md'), shutdown_content),
    
    # 2. ChatGPT / Codex
    (os.path.join(home, '.codex', 'skills', 'project-init', 'SKILL.md'), project_init_content),
    (os.path.join(home, '.codex', 'skills', 'startup', 'SKILL.md'), startup_content),
    (os.path.join(home, '.codex', 'skills', 'shutdown', 'SKILL.md'), shutdown_content),
    
    # 3. AntiGravity 2 / Gemini
    (os.path.join(home, '.gemini', 'config', 'plugins', 'project-init-plugin', 'skills', 'SKILL.md'), project_init_content),
    (os.path.join(home, '.gemini', 'config', 'plugins', 'startup-plugin', 'skills', 'SKILL.md'), startup_content),
    (os.path.join(home, '.gemini', 'config', 'plugins', 'shutdown-plugin', 'skills', 'SKILL.md'), shutdown_content),
    
    # 4. chezmoi repo
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_claude', 'skills', 'project-init', 'SKILL.md'), project_init_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_claude', 'skills', 'startup', 'SKILL.md'), startup_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_claude', 'skills', 'shutdown', 'SKILL.md'), shutdown_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_codex', 'skills', 'project-init', 'SKILL.md'), project_init_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_codex', 'skills', 'startup', 'SKILL.md'), startup_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_codex', 'skills', 'shutdown', 'SKILL.md'), shutdown_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_gemini', 'config', 'plugins', 'project-init-plugin', 'skills', 'SKILL.md'), project_init_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_gemini', 'config', 'plugins', 'startup-plugin', 'skills', 'SKILL.md'), startup_content),
    (os.path.join(home, '.local', 'share', 'chezmoi', 'dot_gemini', 'config', 'plugins', 'shutdown-plugin', 'skills', 'SKILL.md'), shutdown_content),
]

for path, content in targets:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Successfully wrote: {path}')
