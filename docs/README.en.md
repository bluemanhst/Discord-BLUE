# Discord BLUE 🚀

🌐 **Read in other languages:**
- [🇻🇳 Tiếng Việt](README.md)

> ⚠️ **USAGE & TERMS COMPLIANCE NOTICE (please read before use)**
> * This project is released for **educational, technical-research and automation-testing purposes**.
> * Only use it on **accounts you own** and on servers/channels where you have **explicit permission**.
> * Automating user accounts (self-botting) and bulk messaging may **violate the Discord Terms of Service**; you bear all risk (account termination, legal action…).
> * **Never** use this tool for spam, fraud, unsolicited advertising, harassment, or to infringe on the rights of others.

---

**Discord BLUE** (by *bluemanhst*) is an intuitive multi-threaded Discord auto-messaging tool with a full graphical user interface (GUI). It is equipped with comprehensive human-like simulation mechanisms to minimize the risk of spam detection or account bans (Anti-Ban / Anti-Spam).

---

## 📥 DOWNLOAD APPLICATION (EXE BUILD)

You can download the pre-compiled `.exe` file directly without needing to install Python:

🔗 **[DOWNLOAD LATEST DISCORD BLUE RELEASE](https://github.com/bluemanhst/Discord-BLUE/releases)**

*(Download `Discord BLUE.exe` from the Assets section of the latest release).*

---

## ✨ KEY FEATURES

### 👥 1. Multi-Account & Multi-Threading
* Run unlimited Discord accounts concurrently.
* Each account runs in an **independent Thread**, randomly distributing messages across target channels.
* Instant stop mechanism: The **STOP ALL** button terminates all threads immediately with zero delay.

### 🛡️ 2. Anti-Detection Mechanisms
* **Auto Typing Simulation**: Simulates the *"Typing..."* indicator before sending messages to mimic real human behavior.
* **Random Cooldown**: Customizable random delay between sends (e.g. 60s - 90s).
* **Auto Break**: Automatically takes long periodic breaks after a certain number of messages (e.g., break for 10–30 mins after every 15–25 messages).
* **Auto Stop on Ban**: Detects channel bans, kicks, or mutes (HTTP status codes `403`, `404`) and stops only the affected account while others continue uninterrupted.
* **Smart Templates & Spintax**:
  * Supports Spintax format: `{Hello|Hi|Hey there}`.
  * Message variants: Random emojis, random spaces, randomized casing, and common abbreviations.

### 🗑️ 3. Auto Delete Messages
* Automatically deletes messages after sending with a customizable delay (in milliseconds).
* Ideal for leveling/XP bot grinding without cluttering channels with message history.

### ⏰ 4. Schedule Run Times
* Configure active operating hours (e.g., only run between `09:00` and `17:00`). Outside of this window, accounts pause automatically.

### 🔍 5. Token Validator
* Built-in Discord token checker via Discord API:
  * Check token status (valid / expired / locked).
  * Inspect Avatar, Username, User ID, Email, Phone, 2FA (MFA) status, and token type.

### 📊 6. Realtime Dashboard
* Track: Runtime, Total Messages Sent, Deleted Messages, Errors, Active Accounts, Speed (messages/min), and Success Rate (%).
* Detailed tables broken down by account and by channel.
* **Export** all stats directly to a `.json` file.

### 🎨 7. UI Customization & System Settings
* **3 Preset Themes**: *Dragon Ball* (Default), *Discord*, and *Dark Professional*.
* **Multi-Language Support**: English and Vietnamese (Tiếng Việt).
* **System Tray**: Minimize the app to the Windows taskbar notification tray when closing.
* **Startup with Windows**: Option to automatically start the tool when Windows boots up.
* **Sound Notifications**: Audio cues on successful sends, errors, or tool stop events.
* **Config Management**: Automatically saves `config.json`, with **Export/Import** buttons for easy backup and migration.

---

## 📖 USER GUIDE

### Step 1: Initial Setup
1. Launch **Discord BLUE**.
2. On the **MAIN** tab:
   * **Discord Tokens List**: Paste your tokens (one token per line).
   * *(Optional)* Click **"✅ CHECK TOKEN"** to verify accounts.
   * **Target Channel ID**: Enter the channel IDs to post to (one ID per line). The tool will distribute messages randomly.
   * **Cooldown Min / Cooldown Max**: Set random delay between sends in seconds (recommended: 60 - 90s).
   * **Message List**: Enter your messages (one per line). Spintax `{opt1|opt2}` is supported.

### Step 2: Configure Safety Features
1. Switch to the **FEATURES** tab:
   * Enable **Auto Typing** to display typing indicator before sending.
   * Enable **Auto Break** to take periodic resting breaks.
   * Enable **Smart Templates** to randomize message content against spam filters.
   * Enable **Auto Delete** if you want messages removed after sending.
   * Enable **Schedule** if you want the tool active only during specific hours.

### Step 3: Run
1. Return to the **MAIN** tab and click **"START DISCORD BLUE"**.
2. Monitor real-time logs in the activity log window below.
3. Switch to the **DASHBOARD** tab and click **"REFRESH"** to see live performance statistics.
4. Click **"STOP ALL"** at any time to instantly stop all accounts.

---

## 🛠️ INSTALLATION & RUNNING FROM SOURCE

### Requirements
* Python 3.8+ on Windows.

### Install Dependencies
```bash
pip install requests Pillow pystray
```

### Run Application
```bash
python main.pyw
```

---

## 📦 BUILD EXE

The project includes an automated build script:

1. Run:
   ```cmd
   build.bat
   ```
2. The compiled executable `Discord BLUE.exe` will be located in the `dist/` directory.

---

## 📌 IMPORTANT NOTES

* **`config.json`**: Stores your tokens locally. This file is generated next to the executable (or in the project root). Never share this file.
* **Theme & Language Changes**: After changing the theme or language in Settings, restart the application to apply changes throughout the entire interface.
* **System Tray**: Requires `pystray`. When enabled, clicking `X` hides the window to the tray; double-click the tray icon to restore or right-click to exit.

---

---

## ⚖️ LICENSE & COPYRIGHT

This project is licensed under the [MIT License](../LICENSE). You are free to use, modify, and distribute this software in accordance with the license conditions.

---

## ⚠️ DISCLAIMER

* **Not Affiliated with Discord Inc.**: This project is an independent software and is **NOT** affiliated with, authorized, maintained, sponsored, or endorsed by Discord Inc. or any of its affiliates. The Discord logo and trademarks are the property of Discord Inc.
* **Intended Purpose**: This application is developed strictly for **educational, security research, and interface testing purposes**.
* **User Responsibility**: Using automated tools on user accounts (self-botting) violates the [Discord Terms of Service](https://discord.com/terms). Users are solely responsible for compliance with Discord rules and any potential actions taken against their accounts. The author assumes no liability for any misuse, account suspensions, or damages resulting from the use of this software.

---

## 🌐 BLUE LABS ECOSYSTEM

**Discord BLUE** is part of the **BLUE LABS** ecosystem — a suite of automation tools developed by *bluemanhst*:

| Project | Description | Language |
|---------|-------------|----------|
| [**Discord BLUE**](https://github.com/bluemanhst/Discord-BLUE) | Discord automation tool (this repo) | Python |
| [**Roblox BLUE**](https://github.com/bluemanhst/Roblox-BLUE) | Roblox assistance tool (Multi-Instance, AFK, ...) | C++ |

---

## 👨‍💻 AUTHOR & CONTACT

* **Author**: bluemanhst
* **Discord**: [bluemanhst](https://discord.com/users/481280614956400690)
* **Facebook**: [bluemanhst](https://www.facebook.com/bluemanhstv4seo)

<div align="center">
  <sub>Made with ❤️ by <a href="https://github.com/bluemanhst">bluemanhst</a> · BLUE LABS Ecosystem</sub>
</div>