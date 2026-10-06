# Discord BLUE 🚀

🌐 **其他语言版本 / Read in other languages:**
- [🇻🇳 Tiếng Việt](README.md)
- [🇬🇧 English](README.en.md)

> ⚠️ **使用与条款合规提示（使用前请阅读）**
> * 本项目仅用于**学习、技术研究与自动化测试**。
> * 仅可用于**你自己的账号**，以及你**已获明确授权**的服务器/频道。
> * 自动化用户账号（self-bot）与批量发送消息可能**违反 Discord 服务条款**，一切风险由使用者自行承担（账号封禁、法律责任等）。
> * **严禁**用于垃圾信息、诈骗、骚扰或侵犯他人权益。

---

**Discord BLUE**（由 *bluemanhst* 开发）是一款直观的多线程Discord自动消息发送工具，具备完整的图形用户界面（GUI），并配备了完善的人性化模拟机制，以最大程度地降低被Discord检测或封号的风险（防封/防垃圾邮件）。

---

## 📥 下载应用（EXE 构建版）

您可以直接下载编译好的 `.exe` 文件使用，无需安装 Python：

🔗 **[在此下载最新版本 DISCORD BLUE](https://github.com/bluemanhst/Discord-BLUE/releases)**

*（在最新版本的 Assets 部分下载 `Discord BLUE.exe` 文件）。*

---

## ✨ 核心功能

### 👥 1. 多账户与多线程 (Multi-Account)
* 同时并发运行无限制数量的 Discord 账户。
* 每个账户在**独立线程**中运行，自动将消息随机分配到目标频道列表中。
* 紧急停止机制：**全部停止**按钮可立即终止所有线程，零延迟。

### 🛡️ 2. 防检测机制 (Anti-Detection)
* **自动打字模拟 (Auto Typing)**：发送消息前模拟显示“正在输入...”状态，表现得像真实用户。
* **随机冷却时间 (Cooldown)**：自定义每次发送之间的随机等待时间（例如：60秒至90秒）。
* **自动长休 (Auto Break)**：在发送一定数量的消息后（例如：15-25条），自动长时间休息（例如：10-30分钟）。
* **被封禁自动停止 (Auto Stop on Ban)**：自动识别账户是否被踢出或禁言（HTTP 状态码 `403`, `404`），仅停止受影响账户，其他账户继续运行。
* **智能模板与 Spintax**：
  * 支持 Spintax 语法：`{你好|Hello|Hi 大家好}`。
  * 消息随机变体：随机插入表情符号、随机空格、大小写切换及常用缩写。

### 🗑️ 3. 自动删除消息 (Auto Delete)
* 发送消息后，经过自定义延迟（以毫秒为单位）后自动删除消息。
* 非常适合升级/挂机机器人经验（XP/Level），而不在频道中留下刷屏痕迹。

### ⏰ 4. 定时运行 (Schedule)
* 配置每日定时运行时间段（例如：仅在 `09:00` 至 `17:00` 之间运行）。在此时间段之外，工具自动处于等待状态。

### 🔍 5. 令牌验证工具 (Token Validator)
* 内置 Discord Token 在线验证工具：
  * 检查 Token 是否有效、过期或被锁定。
  * 查看头像、用户名、User ID、邮箱、手机号、两步验证（2FA）及 Token 类型。

### 📊 6. 实时仪表板 (Realtime Dashboard)
* 监控：运行时间、发送总数、删除总数、错误数、在线账户数、发送速度（条/分钟）和成功率（%）。
* 按账户和按频道的详细统计表。
* 支持一键将所有统计数据导出为 `.json` 文件。

### 🎨 7. 界面定制与系统设置
* **3款精美预设主题**：*七龙珠 Dragon Ball*（默认）、*Discord*、*专业暗黑 Dark Professional*。
* **多语言支持**：完整支持简体中文、英文和越南语。
* **系统托盘 (System Tray)**：关闭窗口时最小化到系统右下角托盘（需 `pystray`）。
* **开机自启**：支持随 Windows 系统自动启动。
* **声音提醒**：发送成功、发生错误或工具停止时的音效提示。
* **配置管理**：自动保存 `config.json`，支持导出/导入配置文件。

---

## 📖 用户使用指南

### 第 1 步：初始配置
1. 打开 **Discord BLUE** 应用程序。
2. 在 **主页 (TRANG CHÍNH)** 标签页中：
   * **Discord 令牌列表**：粘贴您的 Token（每行一个账户）。
   * *（可选）* 点击 **"✅ 检查令牌"** 按钮验证有效性。
   * **目标频道 ID**：输入要发送消息的频道 ID（每行一个）。工具将自动随机分配。
   * **冷却时间 (Cooldown Min / Max)**：设置每次发送的随机等待时间（以秒为单位，建议：60 - 90秒）。
   * **消息列表**：输入要发送的内容（每行一条），支持 `{选项1|选项2}` 语法。

### 第 2 步：开启安全功能
1. 切换到 **功能设置 (TÍNH NĂNG)** 标签页：
   * 勾选 **自动打字 (Auto Typing)**。
   * 勾选 **自动长休 (Auto Break)** 以定期休息。
   * 勾选 **智能模板 (Smart Templates)** 以随机变化消息内容防封。
   * 勾选 **自动删除 (Auto Delete)** 如果需要发完即删。
   * 勾选 **定时运行 (Schedule)** 如果只需在特定时段运行。

### 第 3 步：开始运行
1. 返回 **主页**，点击 **"启动 DISCORD BLUE"** 按钮。
2. 在下方的 **活动日志** 窗口实时查看发送状态。
3. 切换到 **仪表板 (DASHBOARD)** 查看详细数据。
4. 随时点击 **"全部停止"** 即可立刻停止运行。

---

## 🛠️ 从源码安装与运行（开发者指南）

### 环境要求
* Windows 系统，Python 3.8 或更高版本。

### 安装依赖
```bash
pip install requests Pillow pystray
```

### 运行程序
```bash
python main.pyw
```

---

## 📦 打包为 EXE 文件

项目已集成自动检查与打包脚本：

1. 运行：
   ```cmd
   build.bat
   ```
2. 打包完成后，`Discord BLUE.exe` 文件将生成在 `dist/` 目录下。

---

## 📌 重要提示

* **`config.json` 文件**：包含您的私密 Token，此文件会自动保存在与 `.exe` 相同的目录下（或源码根目录下）。切勿将此文件分享给他人。
* **主题与语言切换**：切换主题或语言后，请关闭并重新打开工具以使界面完全生效。

---

---

## ⚖️ 开源许可 (LICENSE)

本项目采用 [MIT License](../LICENSE) 开源许可证。您可以根据该许可证的条款自由使用、修改和分发本软件。

---

## ⚠️ 免责声明 (DISCLAIMER)

* **非官方软件**：本项目为独立开源项目，**不隶属于** Discord Inc.，亦未获得 Discord Inc. 及其关联公司的授权、赞助或认可。Discord 徽标和商标均属于 Discord Inc. 的财产。
* **开发目的**：本软件仅用于**学习、安全研究与自动化界面测试目的（Educational & Testing Purposes）**。
* **用户责任**：在个人用户账户上使用自动化工具（Self-botting）可能违反 [Discord 服务条款 (Discord Terms of Service)](https://discord.com/terms)。用户须自行承担使用本软件的一切行为与账户安全风险。对于因使用本软件造成的任何账号受限、封禁、数据损失或争议，作者概不承担任何责任。

---

## 🌐 BLUE LABS 生态系统

**Discord BLUE** 是 **BLUE LABS** 生态系统的一部分 — 由 *bluemanhst* 开发的一套自动化工具集：

| 项目 | 描述 | 语言 |
|------|------|------|
| [**Discord BLUE**](https://github.com/bluemanhst/Discord-BLUE) | Discord 自动化工具（本仓库） | Python |
| [**Roblox BLUE**](https://github.com/bluemanhst/Roblox-BLUE) | Roblox 辅助工具（多开、AFK 等） | C++ |

---

## 👨‍💻 作者与联系方式

* **作者**: bluemanhst
* **Discord**: [bluemanhst](https://discord.com/users/481280614956400690)
* **Facebook**: [bluemanhst](https://www.facebook.com/bluemanhst)

<div align="center">
  <sub>Made with ❤️ by <a href="https://github.com/bluemanhst">bluemanhst</a> · BLUE LABS Ecosystem</sub>
</div>