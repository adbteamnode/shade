import os
import time
import random
import json
import cloudscraper # requests အစား ဒါကို သုံးပါမယ်
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
        # Cloudflare ကို ကျော်ဖို့ scraper ဆောက်ပါမယ်
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            }
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
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE (Cloudflare Bypass)
        """)

    def log(self, message, level="INFO"):
        wib = pytz.timezone('Asia/Jakarta')
        time_str = datetime.now(wib).strftime('%H:%M:%S')
        colors = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "ERROR": Fore.RED, "WARNING": Fore.YELLOW, "CYCLE": Fore.MAGENTA}
        print(f"[{time_str}] {colors.get(level, Fore.WHITE)}[{level}] {message}{Style.RESET_ALL}")

    def get_signature_data(self, private_key):
        w3 = Web3()
        pk = '0x' + private_key.strip().replace('0x', '')
        account = w3.eth.account.from_key(pk)
        address = to_checksum_address(account.address)
        timestamp = int(time.time() * 1000)
        message = f"Shade Points: Create account for {address.lower()} at {timestamp}"
        encoded_message = encode_defunct(text=message)
        signed_message = w3.eth.account.sign_message(encoded_message, private_key=pk)
        return address, timestamp, signed_message.signature.hex()

    def do_login(self, private_key, proxies):
        try:
            address, timestamp, signature, _ = self.get_signature_data(private_key)
            if not signature.startswith('0x'): signature = '0x' + signature
            
            # Step 1: Wallet Check
            self.log(f"Verifying wallet: {address[:6]}...", "INFO")
            user_url = f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}"
            self.scraper.get(user_url, headers=self.base_headers, proxies=proxies, timeout=30)
            
            # Step 2: Session Login
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
            
            self.log(f"Login failed (Status {response.status_code})", "ERROR")
        except Exception as e:
            self.log(f"Login error: {str(e)}", "ERROR")
        return None, None

    def do_claim(self, token, proxies):
        try:
            headers = self.base_headers.copy()
            headers["authorization"] = f"Bearer {token}"
            res = self.scraper.post("https://points.shadenetwork.io/api/claim", headers=headers, json={}, proxies=proxies, timeout=30)
            if res.status_code == 200:
                data = res.json()
                self.log(f"Claimed: +{data.get('reward')} | Total: {data.get('newPoints'):,}", "SUCCESS")
        except: pass

    def run(self):
        self.welcome()
        mode = input("1. Proxy | 2. No Proxy: ").strip()
        accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
        proxies = [line.strip() for line in open("proxy.txt")] if mode == '1' else []

        while True:
            self.log("Cycle Started", "CYCLE")
            for i, pk in enumerate(accounts):
                p = {"http": f"http://{proxies[i%len(proxies)]}", "https": f"http://{proxies[i%len(proxies)]}"} if proxies else None
                token, addr = self.do_login(pk, p)
                if token:
                    self.do_claim(token, p)
                time.sleep(3)
            
            self.log("Cycle Finished. Waiting 24h...", "CYCLE")
            time.sleep(86400)

if __name__ == "__main__":
    ShadeBot().run()
