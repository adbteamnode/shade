# Shade Network Auto Bot

Automated bot for Shade Network that handles daily claims, quest completion, activities check, and faucet claims.

## Register

Register here: [https://points.shadenetwork.io/ref/1law552s](https://points.shadenetwork.io/ref/1law552s)

## Features

- ✅ Auto Login with private key
- ✅ Auto Daily Claim
- ✅ Auto Complete Quests (Twitter, Discord, Telegram)
- ✅ Auto Check Activities
- ✅ Auto Faucet Claim
- ✅ Proxy Support
- ✅ Multi-account Support
- ✅ Automatic 24-hour cycle

## Requirements

- Python 3.8 or higher
- pip (Python package manager)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/adbteamnode/shade.git && cd shade
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create `accounts.txt` file and add your private keys (one per line):
```
0xYOUR_PRIVATE_KEY_1
0xYOUR_PRIVATE_KEY_2
0xYOUR_PRIVATE_KEY_3
```

2. (Optional) Create `proxy.txt` file for proxy support:
```
ip:port:username:password
ip:port:username:password
```

Or in standard format:
```
http://username:password@ip:port
http://username:password@ip:port
```

## Usage

Run the bot:
```bash
python bot.py
```

Select mode:
- **Option 1**: Run with proxy (requires proxy.txt)
- **Option 2**: Run without proxy

The bot will:
1. Login to all accounts
2. Claim daily rewards
3. Complete available quests
4. Check activities
5. Claim faucet
6. Wait 24 hours and repeat

## File Structure

```
Shade-Auto-Bot/
├── bot.py              # Main bot script
├── accounts.txt        # Your private keys (create this)
├── proxy.txt          # Your proxies (optional)
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Security Warning

⚠️ **IMPORTANT**: 
- Never share your `accounts.txt` file
- Keep your private keys secure
- Use at your own risk
- This bot is for educational purposes

## Troubleshooting

**Login Failed**
- Check if your private key is correct
- Verify internet connection
- Try without proxy first

**Proxy Issues**
- Ensure proxy format is correct
- Test proxy connectivity
- Use mode 2 (without proxy) if issues persist

**Quest Not Completing**
- Some quests require manual verification
- Blockchain quests are skipped automatically
- Wait for next cycle

## Disclaimer

This bot is for educational purposes only. Use at your own risk. The developer is not responsible for any losses or damages.
