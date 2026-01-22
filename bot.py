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

class ShadeBot:
    def __init__(self):
        self.base_headers = {
            "accept": "*/*",
            "content-type": "application/json",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "origin": "https://points.shadenetwork.io",
            "referer": "https://points.shadenetwork.io/quests"
        }

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

    def process_account(self, pk, p_str, idx):
        proxies = None
        if p_str:
            if not p_str.startswith('http'): p_str = f"http://{p_str}"
            proxies = {"http": p_str, "https": p_str}

        address, timestamp, signature = self.get_signature_data(pk)
        if not address: return

        self.log(f"Account {idx}: {address[:8]}...", "INFO")
        
        try:
            # Login
            payload = {"address": address, "timestamp": timestamp, "signature": signature if signature.startswith('0x') else '0x'+signature}
            res = requests.post("https://points.shadenetwork.io/api/auth/session", headers=self.base_headers, json=payload, proxies=proxies, timeout=30)
            
            if res.status_code in [200, 201]:
                token = res.json().get('token')
                self.log("Login Success", "SUCCESS")
                auth_headers = self.base_headers.copy()
                auth_headers["authorization"] = f"Bearer {token}"

                # Daily Claim
                requests.post("https://points.shadenetwork.io/api/claim", headers=auth_headers, json={}, proxies=proxies)
                self.log("Daily Claim Processed", "SUCCESS")

                # Quests (Twitter & Discord) - Two-Step Verification Logic
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
                        # Step 1: Verification to get Proof
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
                                
                                # Step 2: Complete Quest using the Proof
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
                                    self.log(f"Could not complete {name}", "WARNING")
                            else:
                                self.log(f"{name} is already done or not eligible.", "WARNING")
                        
                        time.sleep(random.randint(3, 5))
                    except Exception as e:
                        self.log(f"Error doing {name}", "ERROR")

            else: self.log(f"Login Failed: {res.status_code}", "ERROR")
        except Exception as e: 
            self.log(f"Connection Error: {str(e)}", "ERROR")

    def run(self):
        self.welcome()
        mode = input("1. Proxy Mode | 2. No Proxy: ").strip()
        
        if not os.path.exists("accounts.txt"):
            print("accounts.txt not found!")
            return
            
        accounts = [line.strip() for line in open("accounts.txt") if line.strip()]
        proxies = [line.strip() for line in open("proxy.txt") if line.strip()] if mode == '1' and os.path.exists("proxy.txt") else []

        while True:
            for i, pk in enumerate(accounts):
                p_str = proxies[i % len(proxies)] if proxies else None
                self.process_account(pk, p_str, i+1)
                if i < len(accounts) - 1:
                    time.sleep(random.randint(5, 10))
            
            self.log("Cycle Done. Waiting 24h...", "CYCLE")
            time.sleep(86400)

if __name__ == "__main__":
    ShadeBot().run()
