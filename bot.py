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
        # Cloudflare ကိုကျော်ရန် Browser Fingerprint သတ်မှတ်ခြင်း
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        self.base_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "referer": "https://points.shadenetwork.io/dashboard",
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
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE (Full Version)
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
        except Exception as e:
            self.log(f"Sign error: {str(e)}", "ERROR")
            return None, None, None, None

    def do_login(self, private_key, proxies):
        try:
            address, timestamp, signature, _ = self.get_signature_data(private_key)
            if not address: return None, None
            
            self.log(f"Verifying wallet: {address[:6]}...{address[-4:]}", "INFO")
            user_url = f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}"
            self.scraper.get(user_url, headers=self.base_headers, proxies=proxies, timeout=30)
            
            payload = {"address": address, "timestamp": timestamp, "signature": signature if signature.startswith('0x') else '0x'+signature}
            response = self.scraper.post("https://points.shadenetwork.io/api/auth/session", headers=self.base_headers, json=payload, proxies=proxies, timeout=30)
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "token" in data:
                    self.log("Login Success!", "SUCCESS")
                    return data['token'], address
            self.log(f"Login failed: Status {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"Login logic error: {str(e)}", "ERROR")
        return None, None

    def do_claim(self, token, proxies):
        try:
            headers = self.base_headers.copy()
            headers["authorization"] = f"Bearer {token}"
            res = self.scraper.post("https://points.shadenetwork.io/api/claim", headers=headers, json={}, proxies=proxies, timeout=30)
            if res.status_code == 200:
                data = res.json()
                if data.get("success"):
                    self.log(f"Daily Claim: +{data.get('reward')} | New Total: {data.get('newPoints'):,}", "SUCCESS")
                else: self.log("Already claimed today", "WARNING")
        except: pass

    def verify_quests(self, token, proxies):
        # Twitter and Discord Quests
        quests = [
            {"id": "social_001", "name": "Follow Twitter"},
            {"id": "social_002", "name": "Like Tweet"},
            {"id": "social_003", "name": "Retweet"},
            {"id": "social_006", "name": "Join Discord"},
            {"id": "social_007", "name": "Send Discord Message"}
        ]
        headers = self.base_headers.copy()
        headers["authorization"] = f"Bearer {token}"
        headers["referer"] = "https://points.shadenetwork.io/quests"
        
        for q in quests:
            try:
                endpoint = "verify-twitter" if "social_001" in q["id"] or "social_002" in q["id"] or "social_003" in q["id"] else "verify-discord"
                self.log(f"Verifying Quest: {q['name']}...", "INFO")
                res = self.scraper.post(f"https://points.shadenetwork.io/api/quests/{endpoint}", headers=headers, json={"questId": q["id"]}, proxies=proxies, timeout=30)
                if res.status_code == 200 and res.json().get("verified"):
                    self.log(f"Quest {q['name']} Verified!", "SUCCESS")
                time.sleep(random.randint(2, 4))
            except: pass

    def do_faucet(self, address, proxies):
        try:
            self.log("Requesting Faucet...", "INFO")
            f_headers = self.base_headers.copy()
            f_headers["authority"] = "wallet.shadenetwork.io"
            f_headers["referer"] = "https://wallet.shadenetwork.io/"
            res = self.scraper.post("https://wallet.shadenetwork.io/api/faucet", headers=f_headers, json={"address": address}, proxies=proxies, timeout=60)
            if res.status_code == 200 and res.json().get("success"):
                self.log(f"Faucet Success: {res.json().get('amount')} SHD", "SUCCESS")
            else: self.log("Faucet already claimed/unavailable", "WARNING")
        except: pass

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            h, m, s = i//3600, (i%3600)//60, i%60
            print(f"\r[COUNTDOWN] Next cycle in: {h:02d}:{m:02d}:{s:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

    def run(self):
        self.welcome()
        print(f"{Fore.CYAN}1. Proxy Mode | 2. No Proxy{Style.RESET_ALL}")
        mode = input("Choice: ").strip()
        
        accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
        proxies = [line.strip() for line in open("proxy.txt") if line.strip()] if mode == '1' else []

        while True:
            self.log("New Cycle Started", "CYCLE")
            for i, pk in enumerate(accounts):
                p = {"http": f"http://{proxies[i%len(proxies)]}", "https": f"http://{proxies[i%len(proxies)]}"} if proxies else None
                self.log(f"Processing Account {i+1}/{len(accounts)}", "INFO")
                
                token, addr = self.do_login(pk, p)
                if token:
                    self.do_claim(token, p)
                    self.verify_quests(token, p)
                    self.do_faucet(addr, p)
                
                if i < len(accounts) - 1:
                    time.sleep(random.randint(5, 10))
            
            self.log("Cycle Completed.", "CYCLE")
            self.countdown(86400) # 24 hours

if __name__ == "__main__":
    ShadeBot().run()
