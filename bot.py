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
        # Browser browser fingerprint ကို ပိုပြီး browser အစစ်နဲ့တူအောင် သတ်မှတ်ထားပါတယ်
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
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE (Cloudflare Bypass Fixed)
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
            # return ၄ ခု ပေးဖို့ ပြန်ပြင်ထားပါတယ်
            return address, timestamp, signed_message.signature.hex(), message
        except Exception as e:
            self.log(f"Sign data error: {str(e)}", "ERROR")
            return None, None, None, None

    def do_login(self, private_key, proxies):
        try:
            address, timestamp, signature, message = self.get_signature_data(private_key)
            if not address: return None, None
            
            if not signature.startswith('0x'): signature = '0x' + signature
            
            # Step 1: User Verification (Browser behaviour အတိုင်း)
            self.log(f"Verifying wallet: {address[:6]}...", "INFO")
            user_url = f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}"
            self.scraper.get(user_url, headers=self.base_headers, proxies=proxies, timeout=30)
            
            # Step 2: Session POST
            payload = {"address": address, "timestamp": timestamp, "signature": signature}
            response = self.scraper.post(
                "https://points.shadenetwork.io/api/auth/session",
                headers=self.base_headers,
                json=payload,
                proxies=proxies,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                if "token" in data:
                    self.log("Login Success!", "SUCCESS")
                    return data['token'], address
                else:
                    self.log(f"Token not found in response", "ERROR")
            else:
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
                    self.log(f"Claim Success: +{data.get('reward')} | New Total: {data.get('newPoints'):,}", "SUCCESS")
                else:
                    self.log("Already claimed today", "WARNING")
            else:
                self.log(f"Claim failed: Status {res.status_code}", "WARNING")
        except Exception as e:
            self.log(f"Claim error: {str(e)}", "ERROR")

    def run(self):
        self.welcome()
        print(f"{Fore.CYAN}1. Proxy Mode | 2. No Proxy{Style.RESET_ALL}")
        mode = input("Choice: ").strip()
        
        try:
            accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
            proxies = [line.strip() for line in open("proxy.txt") if line.strip()] if mode == '1' else []
        except Exception as e:
            self.log(f"File error: {str(e)}", "ERROR")
            return

        while True:
            self.log("Cycle Started", "CYCLE")
            for i, pk in enumerate(accounts):
                p = {"http": f"http://{proxies[i%len(proxies)]}", "https": f"http://{proxies[i%len(proxies)]}"} if proxies else None
                
                self.log(f"Account {i+1}/{len(accounts)}", "INFO")
                token, addr = self.do_login(pk, p)
                
                if token:
                    self.do_claim(token, p)
                    # faucet နဲ့ verification တွေပါ ထပ်ထည့်ချင်ရင် ဒီအောက်မှာ ထည့်နိုင်ပါတယ်
                
                time.sleep(random.randint(3, 7))
            
            self.log("Cycle Finished. Waiting for next window...", "CYCLE")
            # 24 နာရီ စောင့်မယ်
            time.sleep(86400)

if __name__ == "__main__":
    ShadeBot().run()
