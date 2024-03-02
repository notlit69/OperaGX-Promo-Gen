import requests
import random
import json

import time
import capsolver
import ctypes

from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style,init
from datetime import datetime
from threading import Lock
from traceback import print_exc
from random import choice
from faker import Faker

lock = Lock()
fkr = Faker()
genned = 0
capsolver.api_key = json.load(open("config.json"))['capsolver_key']

def update_title():
    ctypes.windll.kernel32.SetConsoleTitleW(f"Opera GX Promo Gen By Notlit | Generated : {genned}") 

class Logger:
    @staticmethod
    def Sprint(tag: str, content: str, color):
        ts = f"{Fore.RESET}{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{Fore.RESET}"
        with lock:
            print(Style.BRIGHT + ts + color + f" [{tag}] " + Fore.RESET + content + Fore.RESET)
    @staticmethod
    def Ask(tag: str, content: str, color):
        ts = f"{Fore.RESET}{Fore.LIGHTBLACK_EX}{datetime.now().strftime('%H:%M:%S')}{Fore.RESET}"
        return input(Style.BRIGHT + ts + color + f" [{tag}] " + Fore.RESET + content + Fore.RESET)

class Opera:
    def __init__(self,proxy) -> None:
        self.session = requests.session()
        self.session.proxies = proxy 
        self.email = fkr.first_name() + f"{str(random.randint(100000,200000))}@" + \
                        choice(['gmail.com','outlook.com','yahoo.com','hotmail.com'])
        self.user = self.email.split("@")[0]
        self.session.headers={
    'authority': 'auth.opera.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Brave";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'sec-gpc': '1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}
    def request(self,*args,**kwargs):
        while True:
            try:
                return self.session.request(*args,**kwargs)
            except:
                # print_exc()
                continue
    def get_soln(self):
        try:
            soln = capsolver.solve({
            "type": "ReCaptchaV2TaskProxyLess",
            "websiteURL": "https://auth.opera.com/account/authenticate/email",
            "websiteKey": "6LdYcFgaAAAAAEH3UnuL-_eZOsZc-32lGOyrqfA4",
          })['gRecaptchaResponse']
            return soln
        except Exception as e:
            Logger.Sprint("ERROR",f"Captcha Error: {str(e)}",Fore.RED)
            return None
        
    def regAndAuth(self):
        self.request("GET","https://auth.opera.com/account/authenticate",allow_redirects=True)
        start = time.time()
        soln = self.get_soln() 
        if not soln:
            return

        Logger.Sprint("CAPTCHA","Successfully Solved in {}s".format("%.2f" % (time.time()-start)),Fore.LIGHTCYAN_EX)
        
        self.session.headers['x-language-locale'] = 'en'
        self.session.headers['referer'] = 'https://auth.opera.com/account/authenticate/signup'

        signUp = self.request("POST",
                              "https://auth.opera.com/account/v4/api/signup",
                              json={
    'email': self.email,
    'password': self.user,
    'password_repeated': self.user,
    'marketing_consent': False,
    'captcha' : soln,
    'services': ['gmx']})
        if "429" in signUp.text:
            Logger.Sprint("ERROR","Ratelimited On Signup!")
            return False
        if not signUp.status_code in [200,201,204]:
            Logger.Sprint("ERROR",f"Signup Error: {signUp.text}",Fore.LIGHTRED_EX)
            return False
        
        self.session.headers['x-csrftoken'] = self.session.cookies.get_dict()['__Host-csrftoken']

        profile = self.request("PATCH",
                               "https://auth.opera.com/api/v1/profile",
                               json={"username":self.user})
        if not profile.status_code in [200,201,204]:
            Logger.Sprint("ERROR",f"Profile Set Error: {profile.json()}",Fore.LIGHTRED_EX)
            return False
        
        self.request("GET",
                     "https://api.gx.me/session/login?site=gxme&target=%2F",allow_redirects=True)
        
        self.request("GET",
                           "https://auth.opera.com/account/login-redirect?service=gmx",
                            allow_redirects=True)
        return True
        
    def gen(self):
        global genned

        for x in range(3):
            if not self.regAndAuth():
                continue
            break
        else:
            return 
        
        Logger.Sprint("AUTH",f"Fetched Auth on {self.email}",Fore.LIGHTMAGENTA_EX)

        profileToken = self.request("GET",
                                    "https://api.gx.me/profile/token")

        auth = profileToken.json()['data']
        headers = {
    'authority': 'discord.opr.gg',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': auth,
    'origin': 'https://www.opera.com',
    'referer': 'https://www.opera.com/',
    'sec-ch-ua': '"Not A(Brand";v="99", "Opera GX";v="107", "Chromium";v="121"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
}

        promoReq = self.request("POST",
                                'https://discord.opr.gg/v2/direct-fulfillment', headers=headers)

        if not "token" in promoReq.text:
            Logger.Sprint("ERROR",f"Failed To Fetch Promo! Text: {promoReq.text} Code: {promoReq.status_code}",Fore.LIGHTRED_EX)

        promo = "https://discord.com/billing/partner-promotions/1180231712274387115/{}".format(promoReq.json()['token'])

        Logger.Sprint("PROMO",promo,Fore.LIGHTGREEN_EX)
        with lock:
            with open("promos.txt",'a') as io:
                io.write(f"{promo}\n")
                io.flush()
            genned += 1
            update_title()

def _task():
    proxies = {"https":"http://"+choice(open("proxies.txt",'r').read().splitlines())} if open("proxies.txt",'r').read().splitlines() else None
    while True:
        try:
            Opera(proxies).gen()
        except:
            print_exc()
            continue

if __name__ == "__main__":
    init()
    update_title()
    trds = int(Logger.Ask("INPUT","Enter Amount Of Threads: ",Fore.BLUE))
    with ThreadPoolExecutor(max_workers=trds+1) as exc:
        for x in range(trds):
            exc.submit(_task)

        
