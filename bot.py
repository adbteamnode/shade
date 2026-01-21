import os
import time
import random
import json
import cloudscraper
from datetime import datetime
import pytz
from colorama import Fore, Style, init
from web3 import Web3
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address

os.system('clear' if os.name == 'posix' else 'cls')
import warnings
warnings.filterwarnings('ignore')

init(autoreset=True)

# ==========================================
# CONFIGURATION
# ==========================================
# သင်ပေးထားတဲ့ Link အပြည့်အစုံနဲ့ Code ကို ဒီမှာ ထည့်ထားပါတယ်
REF_LINK = "https://points.shadenetwork.io/ref/1law552s"
REF_CODE = "1law552s"
# ==========================================

class ShadeBot:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        ]

    def welcome(self):
        print(f"""
{Fore.CYAN + Style.BRIGHT} ██████╗██╗  ██╗ █████╗ ██████╗ ███████╗
{Fore.CYAN + Style.BRIGHT}██╔════╝██║  ██║██╔══██╗██╔══██╗██╔════╝
{Fore.CYAN + Style.BRIGHT}╚█████╗ ███████║███████║██║  ██║█████╗  
{Fore.CYAN + Style.BRIGHT} ╚═══██╗██╔══██║██╔══██║██║  ██║██╔══╝  
{Fore.CYAN + Style.BRIGHT}██████╔╝██║  ██║██║  ██║██████╔╝███████╗
{Fore.CYAN + Style.BRIGHT}╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚══════╝
{Fore.YELLOW + Style.BRIGHT}    SHADE NETWORK FULL AUTO | REFERRAL & QUESTS FIXED
        """)

    def log(self, message, level="INFO"):
        wib = pytz.timezone('Asia/Jakarta')
        time_str = datetime.now(wib).strftime('%H:%M:%S')
        colors = {"INFO": Fore.WHITE, "SUCCESS": Fore.GREEN, "ERROR": Fore.RED, "WARNING": Fore.YELLOW, "CYCLE": Fore.MAGENTA}
        print(f"[{time_str}] {colors.get(level, Fore.WHITE)}[{level}] {message}{Style.RESET_ALL}")

    def get_signature_data(self, private_key):
        try:
            w3 = Web3()
            pk = '0x' + private_key.strip().replace('0x', '')
            account = w3.eth.account.from_key(pk)
            address = to_checksum_address(account.address)
            timestamp = int(time.time() * 1000)
            message = f"Shade Points: Create account for {address.lower()} at {timestamp}"
            encoded_message = encode_defunct(text=message)
            signed_message = w3.eth.account.sign_message(encoded_message, private_key=pk)
            return address, timestamp, signed_message.signature.hex()
        except: return None, None, None

    def format_proxy(self, proxy_str):
        if not proxy_str: return None
        proxy_str = proxy_str.strip()
        if not proxy_str.startswith('http'): proxy_str = f"http://{proxy_str}"
        return {"http": proxy_str, "https": proxy_str}

    def process_account(self, pk, p_str, idx):
        ua = random.choice(self.user_agents)
        scraper = cloudscraper.create_scraper(browser={'custom_browser': ua, 'platform': 'windows', 'desktop': True})
        proxies = self.format_proxy(p_str)
        address, timestamp, signature = self.get_signature_data(pk)
        
        if not address: return
        self.log(f"Account {idx}: {address[:8]}...", "INFO")

        # Initial Headers with Referral Link as Referer
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://points.shadenetwork.io",
            "referer": REF_LINK,
            "user-agent": ua
        }

        try:
            # --- LOGIN / REGISTER ---
            payload = {
                "address": address, 
                "timestamp": timestamp, 
                "signature": signature if signature.startswith('0x') else '0x'+signature, 
                "referralCode": REF_CODE
            }
            
            scraper.get(f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}", headers=headers, proxies=proxies, timeout=20)
            auth_res = scraper.post("https://points.shadenetwork.io/api/auth/session", headers=headers, json=payload, proxies=proxies, timeout=20)
            
            if auth_res.status_code in [200, 201]:
                token = auth_res.json().get('token')
                self.log("Login Success (Referral Applied)", "SUCCESS")
                
                auth_headers = headers.copy()
                auth_headers["authorization"] = f"Bearer {token}"
                auth_headers["referer"] = "https://points.shadenetwork.io/dashboard"

                # Daily Claim
                try:
                    c_res = scraper.post("https://points.shadenetwork.io/api/claim", headers=auth_headers, json={}, proxies=proxies, timeout=20)
                    if c_res.status_code == 200:
                        self.log(f"Daily Claim: +{c_res.json().get('reward')} pts", "SUCCESS")
                    else:
                        self.log("Daily Claim: Already done", "WARNING")
                except: pass

                # --- ALL QUESTS ---
                quests = [
                    ("verify-twitter", "social_001", "Follow Twitter"),
                    ("verify-twitter", "social_002", "Like Tweet"),
                    ("verify-twitter", "social_003", "Retweet"),
                    ("verify-discord", "social_006", "Join Discord"),
                    ("verify-discord", "social_007", "Discord Msg")
                ]
                
                for endpoint, qid, name in quests:
                    try:
                        q_headers = auth_headers.copy()
                        q_headers["referer"] = "https://points.shadenetwork.io/quests"
                        q_res = scraper.post(f"https://points.shadenetwork.io/api/quests/{endpoint}", headers=q_headers, json={"questId": qid}, proxies=proxies, timeout=20)
                        if q_res.status_code == 200:
                            self.log(f"Quest: {name} Success", "SUCCESS")
                        else:
                            self.log(f"Quest: {name} Checked", "INFO")
                        time.sleep(2)
                    except: pass

                # Faucet
                try:
                    f_headers = {"authority": "wallet.shadenetwork.io", "referer": "https://wallet.shadenetwork.io/", "user-agent": ua}
                    scraper.post("https://wallet.shadenetwork.io/api/faucet", headers=f_headers, json={"address": address}, proxies=proxies, timeout=25)
                    self.log("Faucet Processed", "SUCCESS")
                except: pass

            else:
                self.log(f"Login Failed: {auth_res.status_code}", "ERROR")

        except Exception as e:
            self.log(f"Connection error: {str(e)[:50]}", "ERROR")

    def run(self):
        self.welcome()
        print(f"Target Referral: {Fore.GREEN}{REF_LINK}")
        mode = input("1. Proxy Mode | 2. No Proxy: ").strip()
        
        try:
            accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
            proxies = [line.strip() for line in open("proxy.txt") if line.strip()] if mode == '1' else []
        except:
            self.log("Files missing!", "ERROR")
            return

        while True:
            self.log("=== NEW CYCLE STARTED ===", "CYCLE")
            for i, pk in enumerate(accounts):
                p_str = proxies[i % len(proxies)] if proxies else None
                self.process_account(pk, p_str, i+1)
                
                if i < len(accounts) - 1:
                    wait = random.randint(10, 20)
                    self.log(f"Waiting {wait}s...", "INFO")
                    time.sleep(wait)
            
            self.log("All accounts done. Waiting 24h...", "CYCLE")
            time.sleep(86400)

if __name__ == "__main__":
    ShadeBot().run()
