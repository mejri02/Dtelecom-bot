# 🚀 dTelecom Auto Bot

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained-Yes-brightgreen.svg)](https://github.com/mejri02/Dtelecom-bot)

**Automated Daily Check-in Bot for dTelecom Rewards Platform**

🎁 **Register Now:** [https://rewards.dtelecom.org/reward?referral_code=EE8887CV](https://rewards.dtelecom.org/reward?referral_code=EE8887CV)

---

## 📋 Table of Contents

- [Features](#-features)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Output Example](#-output-example)
- [Troubleshooting](#-troubleshooting)
- [Security](#-security)
- [Disclaimer](#-disclaimer)
- [Support](#-support)

---

## ✨ Features

- ✅ **Automatic Daily Check-in** 
- 🔐 **Secure Authentication** - SIP99 Solana wallet signing
- ⏰ **Smart Scheduling** - Checks reset time from API, waits until midnight UTC
- 📊 **Live Countdown Timer** - Real-time countdown to next check-in
- 🔄 **Multi-Account Support** - Run unlimited accounts simultaneously
- 🌐 **Proxy Support** - HTTP/HTTPS/SOCKS5 proxy support
- 💾 **Session Persistence** - Saves sessions to avoid re-login
- 🎨 **Beautiful Terminal UI** - Colored output with live updates
- 🔁 **Runs Forever** - Continuous operation, auto-restarts on errors

---

## 📦 Requirements

- **Python 3.8+** (3.10+ recommended)
- **Solana Wallet** with private key
- **Proxies** (optional, for multi-account setups)

---

## 🔧 Installation

### 1. Clone Repository

```bash
git clone https://github.com/mejri02/Dtelecom-bot.git
cd Dtelecom-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Or install manually:**

```bash
pip install aiohttp PyNaCl base58
```

### 3. Register Account

Before running the bot, **register your wallet** using the referral link:

🎁 **[Click here to register](https://rewards.dtelecom.org/reward?referral_code=EE8887CV)**

Connect your Solana wallet and complete registration.

---

## ⚙️ Configuration

### 1. Add Private Keys

Edit `accounts.txt` and add your Solana private keys (one per line):

```txt
5J7WTMRn4wxUWMNsmuUmVJvLdEJXqJYqvXbPJQfDdJhVmEktg8JsAg8WyALxKy7vJv5ZkqZPtmGJxyfEJf3xqxqK
a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2
```

**Supported formats:**
- Base58 (Phantom wallet export)
- Hex (64 characters)

### 2. Add Proxies (Optional)

Edit `proxy.txt` and add proxies (one per line):

```txt
http://username:password@proxy.example.com:8080
socks5://123.456.789.012:1080
https://proxy.example.com:3128
```

**Note:** If you have fewer proxies than accounts, remaining accounts will run without proxy.

---

## 🚀 Usage

### Run the Bot

```bash
python3 bot.py
```

### First Run Behavior

The bot will:
1. ✅ Authenticate each account
2. ✅ Check current task status from API
3. ✅ Perform daily check-in (if not already done)
4. ✅ Display current points
5. ⏰ Calculate time until next reset (midnight UTC)
6. 🕐 Show live countdown timer
7. 🔁 Auto check-in again after reset

### Continuous Operation

The bot runs **forever** until you stop it with `Ctrl+C`.

**Run in Background:**

#### Linux/Mac (Screen)
```bash
screen -S dtelecom
python dtelecom_bot.py
```
Press `Ctrl+A` then `D` to detach.

Reattach: `screen -r dtelecom`

#### Linux/Mac (tmux)
```bash
tmux new -s dtelecom
python dtelecom_bot.py
```
Press `Ctrl+B` then `D` to detach.

Reattach: `tmux attach -t dtelecom`

#### Using nohup
```bash
nohup python dtelecom_bot.py > bot.log 2>&1 &
```

---

## 📊 Output Example

```
    ███╗   ███╗███████╗     ██╗██████╗ ██╗ ██████╗ ██████╗ 
    ████╗ ████║██╔════╝     ██║██╔══██╗██║██╔═████╗╚════██╗
    ██╔████╔██║█████╗       ██║██████╔╝██║██║██╔██║ █████╔╝
    ██║╚██╔╝██║██╔══╝  ██   ██║██╔══██╗██║████╔╝██║██╔═══╝ 
    ██║ ╚═╝ ██║███████╗╚█████╔╝██║  ██║██║╚██████╔╝███████╗
    ╚═╝     ╚═╝╚══════╝ ╚════╝ ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝

         ═══════ dTelecom Auto Bot v2.0 ═══════
              Daily Check-In Automation

[12:00:00] ✓  Loaded 3 account(s)
[12:00:00] ✓  Loaded 2 proxy/proxies
[12:00:05] ℹ  [Account 1] Wallet: Ab3D...Xy9Z
[12:00:06] ► [Account 1] Getting CSRF token...
[12:00:07] ► [Account 1] Signing in...
[12:00:08] ✓  [Account 1] Sign-in successful!
[12:00:09] ✓  [Account 1] Session valid
[12:00:12] ► [Account 1] Attempting daily check-in...
[12:00:13] ✓  [Account 1] Daily check-in completed! (+5 points)
[12:00:16] ► [Account 1] Fetching account stats...
[12:00:18] ✓  [Account 1] Stats: 125 points | Check-in: ✓
[12:00:18] ✓  [Account 1] === Cycle Complete ===
[12:00:18] ℹ  [Account 1] Points: 125

[12:00:19] [COUNTDOWN] [Account 1] Next cycle in: 11:59:41
[12:00:20] [COUNTDOWN] [Account 1] Next cycle in: 11:59:40
[12:00:21] [COUNTDOWN] [Account 1] Next cycle in: 11:59:39
...
```

---

## 🔧 Troubleshooting

### "Invalid private key format"

**Cause:** Private key is not in correct format.

**Solution:**
- Ensure key is base58 or hex format
- Remove any spaces or line breaks
- For hex: must be exactly 64 characters

### "Session validation failed"

**Cause:** Network issue or expired session.

**Solution:**
- Check internet connection
- Delete `tokens.json` and restart bot
- Verify dTelecom website is accessible

### "Check-in already done today"

**Cause:** You already completed today's check-in.

**Solution:** This is normal. Bot will wait until next reset (midnight UTC).

### "NameError: name 'HTTPClient' is not defined"

**Cause:** Missing future annotations import.

**Solution:** Ensure first line of bot is `from __future__ import annotations`

### Bot appears frozen

**Cause:** Bot is in countdown mode.

**Solution:** The countdown timer updates every second. If you don't see updates, check your terminal supports carriage return (`\r`).

### Proxy connection errors

**Cause:** Invalid proxy or proxy is down.

**Solution:**
- Verify proxy format is correct
- Test proxy separately
- Try running without proxy first

---

## 🔒 Security

### Best Practices

1. ✅ **Never share `accounts.txt`** - Contains your private keys
2. ✅ **Keep `tokens.json` private** - Contains session data
3. ✅ **Use unique private keys** - Don't reuse across services
4. ✅ **Use proxies for multi-account** - Avoid rate limits

---

## 📁 File Structure

```
Dtelecom-bot/
├── dtelecom_bot.py       # Main bot script
├── accounts.txt          # Your private keys (create this)
├── proxy.txt             # Your proxies (optional)
├── tokens.json           # Auto-generated session cache
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── .gitignore           # Git ignore rules
```

---

## 🛠️ Advanced Configuration

Edit these values in `dtelecom_bot.py` if needed:

```python
REFERRAL_CODE = 'EE8887CV'
CHECK_IN_RESET_HOUR_UTC = 0
MIN_DELAY = 2000
MAX_DELAY = 8000
RETRY_DELAY_MINUTES = 30
```

---

## ⚠️ Disclaimer

This bot is for **educational purposes** only. 

- Use at your own risk
- Always comply with dTelecom's Terms of Service
- No guarantees of rewards or points
- Author is not responsible for account bans or issues

---

## 💝 Support

If this bot helped you, please:
- ⭐ Star this repository
- 🔗 Use referral code: [EE8887CV](https://rewards.dtelecom.org/reward?referral_code=EE8887CV)
- 🐛 Report bugs via [Issues](https://github.com/mejri02/Dtelecom-bot/issues)

---

## 📝 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Mejri02**

- GitHub: [@mejri02](https://github.com/mejri02)
- Repository: [Dtelecom-bot](https://github.com/mejri02/Dtelecom-bot)

---

## 🙏 Acknowledgments

- dTelecom team for the platform
- Python community for excellent libraries
- All contributors and users

---

<div align="center">

**Made with ❤️ by Mejri02**

**Register now:** [https://rewards.dtelecom.org/reward?referral_code=EE8887CV](https://rewards.dtelecom.org/reward?referral_code=EE8887CV)

⭐ **Star this repo if you found it helpful!** ⭐

</div>
