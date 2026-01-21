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
            "origin": "https://points.shadenetwork.io",
            "sec-ch-ua": '"Chromium";v="138", "Not(A:Brand";v="8", "Herond";v="138"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }

    def welcome(self):
        print(f"""
            {Fore.GREEN + Style.BRIGHT}      █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}     ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}     ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}     ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}     ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}     ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE (Task Logic Fixed)
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
        if not proxy_str: return None
        proxy_str = proxy_str.strip()
        if not proxy_str.startswith('http'): proxy_str = f"http://{proxy_str}"
        return {"http": proxy_str, "https": proxy_str}

    def do_login(self, private_key, proxies):
        try:
            address, timestamp, signature, _ = self.get_signature_data(private_key)
            if not address: return None, None
            
            headers = self.base_headers.copy()
            headers["referer"] = "https://points.shadenetwork.io/dashboard"
            
            # Step 1: Wallet Verification
            user_url = f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}"
            self.scraper.get(user_url, headers=headers, proxies=proxies, timeout=30)
            
            # Step 2: Session Login
            payload = {"address": address, "timestamp": timestamp, "signature": signature if signature.startswith('0x') else '0x'+signature}
            response = self.scraper.post("https://points.shadenetwork.io/api/auth/session", headers=headers, json=payload, proxies=proxies, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "token" in data:
                    self.log(f"Login Success: {address[:6]}...", "SUCCESS")
                    return data['token'], address
            self.log(f"Login Failed: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Login Error: {str(e)}", "ERROR")
        return None, None

    def do_claim(self, token, proxies):
        try:
            headers = self.base_headers.copy()
            headers["authorization"] = f"Bearer {token}"
            headers["referer"] = "https://points.shadenetwork.io/dashboard"
            res = self.scraper.post("https://points.shadenetwork.io/api/claim", headers=headers, json={}, proxies=proxies, timeout=30)
            if res.status_code == 200:
                data = res.json()
                self.log(f"Daily Claim: +{data.get('reward')} | Total: {data.get('newPoints'):,}", "SUCCESS")
            else:
                self.log("Daily Claim: Already claimed or not available", "WARNING")
        except: pass

    def verify_quests(self, token, proxies):
        """Task တွေကို အရင်ကုဒ်ဟောင်းထဲကအတိုင်း တစ်ခုချင်းစီ သေချာလုပ်ပေးမယ့်အပိုင်း"""
        headers = self.base_headers.copy()
        headers["authorization"] = f"Bearer {token}"
        headers["referer"] = "https://points.shadenetwork.io/quests"
        
        # Twitter Quests
        tw_quests = [
            {"id": "social_001", "name": "Follow Twitter"},
            {"id": "social_002", "name": "Like Tweet"},
            {"id": "social_003", "name": "Retweet"}
        ]
        # Discord Quests
        dc_quests = [
            {"id": "social_006", "name": "Join Discord"},
            {"id": "social_007", "name": "Send Discord Message"}
        ]

        # Process Twitter
        for q in tw_quests:
            try:
                self.log(f"Processing {q['name']}...", "INFO")
                res = self.scraper.post("https://points.shadenetwork.io/api/quests/verify-twitter", headers=headers, json={"questId": q["id"]}, proxies=proxies, timeout=30)
                if res.status_code == 200 and res.json().get("verified"):
                    self.log(f"Success: {q['name']}", "SUCCESS")
                time.sleep(2)
            except: pass

        # Process Discord
        for q in dc_quests:
            try:
                self.log(f"Processing {q['name']}...", "INFO")
                res = self.scraper.post("https://points.shadenetwork.io/api/quests/verify-discord", headers=headers, json={"questId": q["id"]}, proxies=proxies, timeout=30)
                if res.status_code == 200 and res.json().get("verified"):
                    self.log(f"Success: {q['name']}", "SUCCESS")
                time.sleep(2)
            except: pass

    def do_faucet(self, address, proxies):
        try:
            self.log("Processing Faucet...", "INFO")
            f_headers = self.base_headers.copy()
            f_headers.pop("origin", None)
            f_headers["authority"] = "wallet.shadenetwork.io"
            f_headers["referer"] = "https://wallet.shadenetwork.io/"
            res = self.scraper.post("https://wallet.shadenetwork.io/api/faucet", headers=f_headers, json={"address": address}, proxies=proxies, timeout=60)
            if res.status_code == 200 and res.json().get("success"):
                self.log(f"Faucet Success: {res.json().get('amount')} SHD", "SUCCESS")
            else:
                self.log("Faucet: Already claimed or limit reached", "WARNING")
        except: pass

    def run(self):
        self.welcome()
        mode = input("1. Proxy Mode | 2. No Proxy: ").strip()
        
        try:
            accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
            proxies_list = [line.strip() for line in open("proxy.txt") if line.strip()] if mode == '1' else []
        except:
            self.log("Required files missing!", "ERROR")
            return

        while True:
            self.log("--- New Cycle Started ---", "CYCLE")
            for i, pk in enumerate(accounts):
                p = self.format_proxy(proxies_list[i % len(proxies_list)]) if proxies_list else None
                self.log(f"Account {i+1}/{len(accounts)}", "INFO")
                
                token, addr = self.do_login(pk, p)
                if token:
                    # အရင်ကုဒ်ဟောင်းမှာပါတဲ့ အစဉ်လိုက်အတိုင်း လုပ်ဆောင်ခြင်း
                    self.do_claim(token, p)      # Daily Points
                    self.verify_quests(token, p)  # Twitter & Discord Quests
                    self.do_faucet(addr, p)      # Faucet
                
                time.sleep(random.randint(5, 10))
            
            self.log("Cycle Completed. Waiting for 24h...", "CYCLE")
            time.sleep(86400)

if __name__ == "__main__":
    ShadeBot().run()
