import os
import time
import random
import requests
import json
from datetime import datetime
import pytz
from colorama import Fore, Style, init
from web3 import Web3
from eth_account.messages import encode_defunct
from eth_utils import to_checksum_address

os.system('clear' if os.name == 'posix' else 'cls')
import warnings
warnings.filterwarnings('ignore')
import sys
if not sys.warnoptions:
    os.environ["PYTHONWARNINGS"] = "ignore"

init(autoreset=True)

class ShadeBot:
    def __init__(self):
        # Header တွေကို Screenshot ထဲကအတိုင်း ပိုတူအောင် ပြင်ထားပါတယ်
        self.base_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "sec-ch-ua": '"Chromium";v="138", "Not(A:Brand";v="8", "Herond";v="138"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
        }

    def welcome(self):
        print(
            f"""
            {Fore.GREEN + Style.BRIGHT}      █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}     ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}     ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}     ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}     ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}     ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Modified by ADB NODE
            """
        )

    def get_headers(self, subdomain="points", auth_token=None):
        headers = self.base_headers.copy()
        headers["authority"] = f"{subdomain}.shadenetwork.io"
        headers["origin"] = f"https://{subdomain}.shadenetwork.io"
        headers["referer"] = f"https://{subdomain}.shadenetwork.io/dashboard"
        
        if auth_token and subdomain == "points":
            headers["authorization"] = f"Bearer {auth_token}"
            
        return headers

    def get_wib_time(self):
        wib = pytz.timezone('Asia/Jakarta')
        return datetime.now(wib).strftime('%H:%M:%S')
    
    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()
        colors = {"INFO": Fore.CYAN, "SUCCESS": Fore.GREEN, "ERROR": Fore.RED, "WARNING": Fore.YELLOW, "CYCLE": Fore.MAGENTA}
        color = colors.get(level, Fore.WHITE)
        print(f"[{time_str}] {color}[{level}] {message}{Style.RESET_ALL}")
    
    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            hours, rem = divmod(i, 3600)
            mins, secs = divmod(rem, 60)
            print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{mins:02d}:{secs:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError: return []

    def get_signature_data(self, private_key):
        w3 = Web3()
        pk = '0x' + private_key.strip().replace('0x', '')
        account = w3.eth.account.from_key(pk)
        address = to_checksum_address(account.address)
        timestamp = int(time.time() * 1000)
        # Screenshot ထဲက Message format အတိုင်း ပြင်ထားပါတယ်
        message = f"Shade Points: Create account for {address.lower()} at {timestamp}"
        encoded_message = encode_defunct(text=message)
        signed_message = w3.eth.account.sign_message(encoded_message, private_key=pk)
        return address, timestamp, signed_message.signature.hex(), message

    def do_login(self, private_key, proxies):
        try:
            address, timestamp, signature, message = self.get_signature_data(private_key)
            if not signature.startswith('0x'): signature = '0x' + signature
            
            # Step 1: User Check (Screenshot ထဲက GET user request)
            self.log(f"Checking wallet: {address[:6]}...{address[-4:]}", "INFO")
            user_url = f"https://points.shadenetwork.io/api/auth/user?wallet={address.lower()}"
            requests.get(user_url, headers=self.get_headers("points"), proxies=proxies, timeout=30)
            
            # Step 2: Session POST (Screenshot ထဲက session request)
            payload = {"address": address, "timestamp": timestamp, "signature": signature}
            response = requests.post(
                "https://points.shadenetwork.io/api/auth/session",
                headers=self.get_headers("points"),
                json=payload,
                proxies=proxies,
                timeout=30
            )
            
            try:
                data = response.json()
                if "token" in data:
                    self.log("Login Successful!", "SUCCESS")
                    return data['token'], address
                else:
                    self.log(f"Login Failed: {data.get('message', 'No token found')}", "ERROR")
            except ValueError:
                self.log(f"Server Error (Not JSON). Status: {response.status_code}", "ERROR")
                # Cloudflare က block ရင် response text ကို စစ်ဖို့:
                # print(response.text[:200]) 
                
        except Exception as e:
            self.log(f"Login Exception: {str(e)}", "ERROR")
        return None, None

    def do_claim(self, token, proxies):
        try:
            self.log("Claiming Daily Points...", "INFO")
            res = requests.post("https://points.shadenetwork.io/api/claim", headers=self.get_headers("points", token), json={}, proxies=proxies, timeout=30)
            if res.status_code == 200:
                data = res.json()
                self.log(f"Success! Reward: +{data.get('reward')} | Total: {data.get('newPoints', 0):,}", "SUCCESS")
            else: self.log("Already claimed or error.", "WARNING")
        except: pass

    def do_faucet(self, address, proxies):
        try:
            self.log("Claiming Faucet...", "INFO")
            res = requests.post("https://wallet.shadenetwork.io/api/faucet", headers=self.get_headers("wallet"), json={"address": address}, proxies=proxies, timeout=60)
            if res.status_code == 200 and res.json().get("success"):
                self.log(f"Faucet Success: {res.json().get('amount')} SHD", "SUCCESS")
            else: self.log("Faucet unavailable.", "WARNING")
        except: pass

    def run(self):
        self.welcome()
        print(f"{Fore.CYAN}1. Proxy Mode | 2. No Proxy{Style.RESET_ALL}")
        mode = input("Choice: ").strip()
        use_proxy = (mode == '1')
        
        accounts = self.load_file("accounts.txt")
        proxies = self.load_file("proxy.txt")
        
        if not accounts: return self.log("No accounts found!", "ERROR")

        cycle = 1
        while True:
            self.log(f"Cycle #{cycle} Started", "CYCLE")
            for i, pk in enumerate(accounts):
                current_proxy = {"http": f"http://{proxies[i%len(proxies)]}", "https": f"http://{proxies[i%len(proxies)]}"} if use_proxy and proxies else None
                
                self.log(f"Account {i+1}/{len(accounts)}", "INFO")
                token, address = self.do_login(pk, current_proxy)
                
                if token:
                    self.do_claim(token, current_proxy)
                    self.do_faucet(address, current_proxy)
                
                time.sleep(2)
            
            self.log(f"Cycle #{cycle} Complete", "CYCLE")
            cycle += 1
            self.countdown(86400)

if __name__ == "__main__":
    bot = ShadeBot()
    bot.run()
