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
# ပြင်ဆင်ရန် အပိုင်း
# ==========================================
REFERRAL_CODE = "1law552s" 
# ==========================================

class ShadeBot:
    def __init__(self):
        # Device မတူအောင် Browser Fingerprint အမျိုးမျိုး သတ်မှတ်ခြင်း
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0"
        ]

    def welcome(self):
        print(f"""
            {Fore.GREEN + Style.BRIGHT}      █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}     ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}     ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}     ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}     ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}     ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Ultimate Multi-Account Bot (Protection Enabled)
        """)

    def log(self, message, level="INFO"):
        wib = pytz.timezone('Asia/Jakarta')
        time_str = datetime.now(wib).strftime('%H:%M:%S')
        colors = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "ERROR": Fore.RED, "WARNING": Fore.YELLOW, "CYCLE": Fore.MAGENTA}
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

    def do_work(self, pk, p_str, idx):
        ua = random.choice(self.user_agents)
        scraper = cloudscraper.create_scraper(browser={'custom_browser': ua, 'platform': 'windows', 'desktop': True})
        proxies = self.format_proxy(p_str)
        
        address, timestamp, signature = self.get_signature_data(pk)
        if not address: return
        
        self.log(f"Account {idx}: {address[:6]}...{address[-4:]}", "INFO")
        
        headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "origin": "https://points.shadenetwork.io",
            "referer": "https://points.shadenetwork.io/dashboard",
            "user-agent": ua
        }

        try:
            # Login / Registration logic
            payload = {
                "address": address, 
                "timestamp": timestamp, 
                "signature": signature if signature.startswith('0x') else '0x'+signature,
                "referralCode": REFERRAL_CODE
            }
            
            # Step 1: User Verification
            scraper.get(f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}", headers=headers, proxies=proxies, timeout=30)
            
            # Step 2: Session
            log_res = scraper.post("https://points.shadenetwork.io/api/auth/session", headers=headers, json=payload, proxies=proxies, timeout=30)
            
            if log_res.status_code in [200, 201]:
                token = log_res.json().get('token')
                headers["authorization"] = f"Bearer {token}"
                self.log("Login Success", "SUCCESS")
                
                # Daily Claim
                claim_res = scraper.post("https://points.shadenetwork.io/api/claim", headers=headers, json={}, proxies=proxies, timeout=30)
                if claim_res.status_code == 200:
                    self.log(f"Claimed: +{claim_res.json().get('reward')} pts", "SUCCESS")
                else: self.log("Already claimed today", "WARNING")

                # Quests (Twitter & Discord)
                quests = [
                    ("verify-twitter", "social_001", "Follow Twitter"),
                    ("verify-twitter", "social_002", "Like Tweet"),
                    ("verify-twitter", "social_003", "Retweet"),
                    ("verify-discord", "social_006", "Join Discord"),
                    ("verify-discord", "social_007", "Discord Msg")
                ]
                
                for endpoint, qid, name in quests:
                    q_headers = headers.copy()
                    q_headers["referer"] = "https://points.shadenetwork.io/quests"
                    q_res = scraper.post(f"https://points.shadenetwork.io/api/quests/{endpoint}", headers=q_headers, json={"questId": qid}, proxies=proxies, timeout=30)
                    if q_res.status_code == 200:
                        self.log(f"Quest: {name} Verified", "SUCCESS")
                    time.sleep(2)

                # Faucet
                f_headers = {"authority": "wallet.shadenetwork.io", "referer": "https://wallet.shadenetwork.io/", "user-agent": ua}
                scraper.post("https://wallet.shadenetwork.io/api/faucet", headers=f_headers, json={"address": address}, proxies=proxies, timeout=30)
                self.log("Faucet Processed", "SUCCESS")

            else:
                self.log(f"Login Failed: {log_res.status_code}", "ERROR")

        except Exception as e:
            self.log(f"Connection Error: {str(e)[:50]}...", "ERROR")

    def run(self):
        self.welcome()
        print(f"Referral Code: {Fore.CYAN}{REFERRAL_CODE}")
        mode = input("1. Proxy Mode | 2. No Proxy: ").strip()
        
        try:
            accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
            proxies = [line.strip() for line in open("proxy.txt") if line.strip()] if mode == '1' else []
        except:
            self.log("Files (accounts.txt/proxy.txt) missing!", "ERROR")
            return

        while True:
            self.log("--- New Cycle Started ---", "CYCLE")
            for i, pk in enumerate(accounts):
                p_str = proxies[i % len(proxies)] if proxies else None
                self.do_work(pk, p_str, i+1)
                
                if i < len(accounts) - 1:
                    wait = random.randint(10, 20)
                    self.log(f"Waiting {wait}s for safety...", "INFO")
                    time.sleep(wait)
            
            self.log("Cycle Done. Waiting 24h...", "CYCLE")
            time.sleep(86400)

if __name__ == "__main__":
    ShadeBot().run()
