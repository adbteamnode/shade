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

class ShadeBot:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
        )
        self.base_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "referer": "https://points.shadenetwork.io/dashboard",
            "origin": "https://points.shadenetwork.io"
        }

    def welcome(self):
        print(f"""
            {Fore.GREEN + Style.BRIGHT}      █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}     ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}     ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}     ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}     ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}     ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE (Proxy Authenticated)
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
            return address, timestamp, signed_message.signature.hex(), message
        except Exception:
            return None, None, None, None

    def format_proxy(self, proxy_str):
        """သင်ပေးထားတဲ့ http://user:pass@ip:port format ကို သေချာဖတ်ပေးမယ့် function"""
        if not proxy_str: return None
        proxy_str = proxy_str.strip()
        
        # အရှေ့မှာ http:// မပါရင် ထည့်ပေးမယ်
        if not proxy_str.startswith('http'):
            proxy_str = f"http://{proxy_str}"
            
        return {
            "http": proxy_str,
            "https": proxy_str
        }

    def do_login(self, private_key, proxies):
        try:
            address, timestamp, signature, _ = self.get_signature_data(private_key)
            if not address: return None, None
            
            self.log(f"Wallet: {address[:6]}... (Using Proxy)", "INFO")
            user_url = f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}"
            
            # Step 1: Wallet Verification
            self.scraper.get(user_url, headers=self.base_headers, proxies=proxies, timeout=30)
            
            # Step 2: Session Login
            payload = {"address": address, "timestamp": timestamp, "signature": signature if signature.startswith('0x') else '0x'+signature}
            response = self.scraper.post("https://points.shadenetwork.io/api/auth/session", headers=self.base_headers, json=payload, proxies=proxies, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "token" in data:
                    self.log("Login Success!", "SUCCESS")
                    return data['token'], address
            self.log(f"Login Failed (Status {response.status_code})", "ERROR")
        except Exception as e:
            self.log(f"Proxy Connection Error: Check your proxy format", "ERROR")
        return None, None

    def do_claim(self, token, proxies):
        try:
            headers = self.base_headers.copy()
            headers["authorization"] = f"Bearer {token}"
            res = self.scraper.post("https://points.shadenetwork.io/api/claim", headers=headers, json={}, proxies=proxies, timeout=30)
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    self.log(f"Daily Claim: +{data.get('reward')} | Total: {data.get('newPoints'):,}", "SUCCESS")
                else: self.log("Already claimed today", "WARNING")
        except: pass

    def verify_quests(self, token, proxies):
        quests = [
            {"id": "social_001", "name": "Follow Twitter"},
            {"id": "social_002", "name": "Like Tweet"},
            {"id": "social_003", "name": "Retweet"},
            {"id": "social_006", "name": "Join Discord"},
            {"id": "social_007", "name": "Send Discord Message"}
        ]
        headers = self.base_headers.copy()
        headers["authorization"] = f"Bearer {token}"
        for q in quests:
            try:
                endpoint = "verify-twitter" if "social_001" in q["id"] or "social_002" in q["id"] or "social_003" in q["id"] else "verify-discord"
                self.scraper.post(f"https://points.shadenetwork.io/api/quests/{endpoint}", headers=headers, json={"questId": q["id"]}, proxies=proxies, timeout=30)
            except: pass

    def do_faucet(self, address, proxies):
        try:
            f_headers = self.base_headers.copy()
            f_headers["authority"] = "wallet.shadenetwork.io"
            f_headers["referer"] = "https://wallet.shadenetwork.io/"
            self.scraper.post("https://wallet.shadenetwork.io/api/faucet", headers=f_headers, json={"address": address}, proxies=proxies, timeout=60)
        except: pass

    def run(self):
        self.welcome()
        mode = input("1. Proxy Mode | 2. No Proxy: ").strip()
        
        try:
            accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
            proxies_list = [line.strip() for line in open("proxy.txt") if line.strip()] if mode == '1' else []
        except Exception as e:
            self.log(f"File missing: {str(e)}", "ERROR")
            return

        while True:
            self.log("New Cycle Started", "CYCLE")
            for i, pk in enumerate(accounts):
                p = self.format_proxy(proxies_list[i % len(proxies_list)]) if proxies_list else None
                self.log(f"Account {i+1}/{len(accounts)}", "INFO")
                
                token, addr = self.do_login(pk, p)
                if token:
                    self.do_claim(token, p)
                    self.verify_quests(token, p)
                    self.do_faucet(addr, p)
                
                time.sleep(random.randint(5, 8))
            
            self.log("Cycle Completed. Waiting 24h...", "CYCLE")
            time.sleep(86400)

if __name__ == "__main__":
    ShadeBot().run()
