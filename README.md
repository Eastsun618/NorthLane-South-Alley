# 北弄 × 南巷 · 行业热点「每周自动更新」部署包

这套方案让工作台的「行业热点」**每周一自动刷新**，全程免费、无需服务器。

## 原理（一句话）
> GitHub 上的一个定时任务（Actions）每周一自动生成新的热点数据 `trends.json` → 提交为 **Pull Request（草稿）** → 你点一下「合并」→ 网页打开时自动读到最新数据。

之所以做成"**PR 草稿 + 人工合并**"，是因为 AI 生成的趋势数据**必须核对来源**后再上线，避免错数据进汇报。

---

## 目录结构
```
你的仓库/
├─ .github/workflows/update-trends.yml   # 每周定时任务
├─ scripts/gen_trends.py                 # 生成脚本（调大模型）
├─ trends.json                           # 热点数据（网页读它）
└─ 北弄南巷_生活工作台.html                 # 工作台（放同一仓库，一起用 Pages）
```

---

## 一、建仓库 + 上传文件（5 分钟）
1. github.com → 右上角 **＋ → New repository** → 名字随意（如 `bnl-nl-desk`）→ 选 **Public** → 创建。
2. 进入仓库 → **Add file → Upload files**，按**原目录结构**上传：
   - `北弄南巷_生活工作台.html`
   - `trends.json`
   - `scripts/gen_trends.py`
   - `.github/workflows/update-trends.yml`

## 二、开启网页访问（GitHub Pages）
仓库 → **Settings → Pages** → Source 选 **Deploy from a branch** → Branch 选 **main / (root)** → Save。
约 1 分钟后得到网址：`https://你的用户名.github.io/bnl-nl-desk/`
工作台网址即：`https://你的用户名.github.io/bnl-nl-desk/北弄南巷_生活工作台.html`

> ✅ 用这个 **https 网址**打开，**扫码识别**也能用了（摄像头需 https 环境）。

## 三、让网页读到最新热点（关键 1 行）
用文本编辑器打开工作台 HTML，找到：
```js
const TRENDS_URL = 'https://cdn.jsdelivr.net/gh/Eastsun618/bnl-nl-desk@main/trends.json';
```
改成（推荐 jsDelivr，跨域最稳）：
```js
const TRENDS_URL = 'https://cdn.jsdelivr.net/gh/Eastsun618/bnl-nl-desk@main/trends.json';
```
保存后重新上传覆盖。**以后每满 7 天，网页自动去拉一次最新热点**（拉不到就继续用本地内置数据，不会白屏）。

## 四、配置大模型 Key（让它能自动生成内容）
仓库 → **Settings → Secrets and variables → Actions**：
- **Secrets** 新增：`LLM_API_KEY` = 你的大模型 API Key
- **Variables** 可选新增：
  - `LLM_BASE_URL` = `https://api.openai.com/v1`（或其他兼容 OpenAI 的地址）
  - `LLM_MODEL` = `gpt-4o-mini`（或其他模型名）

> 若**不配置** Key：定时任务不会乱写数据，而是**每周自动开一条 Issue 提醒你"该更新热点了"** —— 安全兜底。

## 五、测试一次
仓库 → **Actions → 每周更新行业热点 → Run workflow**（手动触发）。
- 配了 Key → 出现一条 **Pull Request「行业热点周更草稿」** → 核对来源 → **Merge** → 网页下次打开即更新；
- 未配 Key → 出现一条 **Issue 提醒**。

---

## 每周你要做什么（30 秒）
1. 收到 GitHub 通知 → 打开 **Pull Request**；
2. 扫一眼来源对不对 → 点 **Merge**；
3. 完成 ✅（网页自动读到新版）

---

## 常见问题
- **拉不到最新数据？** 检查 `TRENDS_URL` 是否写对、仓库是否 Public、jsDelivr 有 ~12h 缓存（周更无影响）。
- **不想用大模型？** Key 留空即可，改为"每周 Issue 提醒 + 手动导入 JSON"。
- **数据准确性？** AI 只做**草稿**，合并前务必核对；脚本已要求模型"不确定的数字标注（待核实）、不编造精确数据"。
- **改更新频率？** 编辑 `.github/workflows/update-trends.yml` 里的 `cron`（默认每周一 09:00 北京时间）。
