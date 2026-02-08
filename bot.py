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

# Screen Clear
os.system('clear' if os.name == 'posix' else 'cls')
import warnings
warnings.filterwarnings('ignore')

init(autoreset=True)

class CaptchaSolver:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.page_url = "https://wallet.shadenetwork.io"
        self.site_key = "0x4AAAAAACN1moBrJQ-mAzdh"
    
    def read_api_key(self):
        try:
            with open("2captcha.txt", "r") as f:
                return f.read().strip()
        except FileNotFoundError:
            return None
    
    def solve_2captcha(self):
        api_key = self.read_api_key()
        if not api_key:
            self.bot.log("2captcha.txt missing!", "ERROR")
            return None
        
        url_create = "https://api.2captcha.com/createTask"
        payload = {
            "clientKey": api_key,
            "task": { "type": "TurnstileTaskProxyless", "websiteURL": self.page_url, "websiteKey": self.site_key }
        }
        
        try:
            self.bot.log("Solving Captcha via 2Captcha...", "INFO")
            response = requests.post(url_create, json=payload, timeout=30)
            result = response.json()
            if result.get("errorId") != 0:
                self.bot.log(f"2Captcha Error: {result.get('errorDescription')}", "ERROR")
                return None
            
            task_id = result.get("taskId")
            url_result = "https://api.2captcha.com/getTaskResult"
            
            for _ in range(60):
                time.sleep(5)
                check = requests.post(url_result, json={"clientKey": api_key, "taskId": task_id})
                res = check.json()
                if res.get("status") == "ready":
                    return res.get("solution", {}).get("token")
            return None
        except Exception as e:
            self.bot.log(f"Captcha Error: {str(e)}", "ERROR")
            return None

class ShadeBot:
    def __init__(self):
        self.base_headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
        }
        self.captcha_solver = CaptchaSolver(self)

    def welcome(self):
        print(f"""
            {Fore.GREEN + Style.BRIGHT}      █████╗ ██████╗ ██████╗     ███╗   ██╗ ██████╗ ██████╗ ███████╗
            {Fore.GREEN + Style.BRIGHT}     ██╔══██╗██╔══██╗██╔══██╗    ████╗  ██║██╔═══██╗██╔══██╗██╔════╝
            {Fore.GREEN + Style.BRIGHT}     ███████║██║  ██║██████╔╝    ██╔██╗ ██║██║   ██║██║  ██║█████╗  
            {Fore.GREEN + Style.BRIGHT}     ██╔══██║██║  ██║██╔══██╗    ██║╚██╗██║██║   ██║██║  ██║██╔══╝  
            {Fore.GREEN + Style.BRIGHT}     ██║  ██║██████╔╝██████╔╝    ██║ ╚████║╚██████╔╝██████╔╝███████╗
            {Fore.GREEN + Style.BRIGHT}     ╚═╝  ╚═╝╚═════╝ ╚═════╝     ╚═╝  ╚═══╝ ╚═════╝ ╚═════╝ ╚══════╝
            {Fore.YELLOW + Style.BRIGHT}      Ultimate Multi-Account Bot (Faucet & Quests Enabled)
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

    def do_faucet(self, address, proxies):
        self.log("Starting Faucet Claim...", "INFO")
        c_token = self.captcha_solver.solve_2captcha()
        if not c_token:
            self.log("Captcha Solve Failed. Faucet Skipped.", "WARNING")
            return

        faucet_headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://wallet.shadenetwork.io",
            "referer": "https://wallet.shadenetwork.io/",
            "user-agent": self.base_headers["user-agent"]
        }
        
        f_url = "https://wallet.shadenetwork.io/api/drip"
        payload = {"address": address, "turnstileToken": c_token}
        
        try:
            time.sleep(2)
            res = requests.post(f_url, json=payload, headers=faucet_headers, proxies=proxies, timeout=60)
            if res.status_code == 200:
                data = res.json()
                self.log(f"Faucet SUCCESS: {data.get('amount', 'Unknown')} SHD Received", "SUCCESS")
            else:
                self.log(f"Faucet Status: {res.status_code}", "WARNING")
        except Exception as e:
            self.log(f"Faucet Error: {str(e)}", "ERROR")

    def process_account(self, pk, p_str, idx):
        proxies = None
        if p_str:
            if not p_str.startswith('http'): p_str = f"http://{p_str}"
            proxies = {"http": p_str, "https": p_str}

        address, timestamp, signature = self.get_signature_data(pk)
        if not address: return

        self.log(f"Account {idx}: {address[:8]}...", "INFO")
        
        try:
            payload = {"address": address, "timestamp": timestamp, "signature": signature if signature.startswith('0x') else '0x'+signature}
            login_headers = self.base_headers.copy()
            login_headers["origin"] = "https://points.shadenetwork.io"
            login_headers["referer"] = "https://points.shadenetwork.io/"
            
            res = requests.post("https://points.shadenetwork.io/api/auth/session", headers=login_headers, json=payload, proxies=proxies, timeout=30)
            
            if res.status_code in [200, 201]:
                token = res.json().get('token')
                self.log("Login Success", "SUCCESS")
                auth_headers = login_headers.copy()
                auth_headers["authorization"] = f"Bearer {token}"

                # Daily Claim
                requests.post("https://points.shadenetwork.io/api/claim", headers=auth_headers, json={}, proxies=proxies)
                self.log("Daily Claim Processed", "SUCCESS")

                # Faucet
                self.do_faucet(address, proxies)

                # Quests
                quests = [
                    ("verify-twitter", "social_001", "Follow Twitter"),
                    ("verify-twitter", "social_002", "Like Tweet"),
                    ("verify-twitter", "social_003", "Retweet"),
                    ("verify-discord", "social_006", "Join Discord"),
                    ("verify-discord", "social_007", "Discord Message")
                ]

                for endpoint, qid, name in quests:
                    try:
                        self.log(f"Starting {name}...", "INFO")
                        v_res = requests.post(
                            f"https://points.shadenetwork.io/api/quests/{endpoint}", 
                            headers=auth_headers, 
                            json={"questId": qid}, 
                            proxies=proxies
                        )
                        
                        if v_res.status_code == 200:
                            v_data = v_res.json()
                            if v_data.get("verified") and v_data.get("proof"):
                                proof = v_data.get("proof")
                                self.log(f"Verification Proof received for {name}", "SUCCESS")
                                
                                time.sleep(random.randint(2, 4))
                                c_res = requests.post(
                                    "https://points.shadenetwork.io/api/quests/complete",
                                    headers=auth_headers,
                                    json={"questId": qid, "verificationProof": proof},
                                    proxies=proxies
                                )
                                if c_res.status_code == 200:
                                    self.log(f"Quest {name} fully completed!", "SUCCESS")
                            else:
                                self.log(f"{name} already done or not eligible.", "WARNING")
                        
                        time.sleep(random.randint(3, 5))
                    except Exception as e:
                        self.log(f"Error doing {name}", "ERROR")

            else: self.log(f"Login Failed: {res.status_code}", "ERROR")
        except Exception as e: 
            self.log(f"Connection Error: {str(e)}", "ERROR")

    def run(self):
        self.welcome()
        try:
            pks = open("accounts.txt", "r").read().splitlines()
        except FileNotFoundError:
            self.log("accounts.txt missing!", "ERROR")
            return

        proxies = []
        try: proxies = open("proxy.txt", "r").read().splitlines()
        except: pass

        while True:
            for idx, pk in enumerate(pks, 1):
                p_str = proxies[idx % len(proxies)] if proxies else None
                self.process_account(pk, p_str, idx)
                print("-" * 65)
                time.sleep(3)
            
            self.log("Cycle Finished. Waiting 24 Hours.", "CYCLE")
            time.sleep(86400)

if __name__ == "__main__":
    bot = ShadeBot()
    bot.run()
