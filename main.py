from uuid import uuid4 as uuid_gen
from time import time as timestamp
from base64 import b64encode
from json import loads, dumps
from threading import Thread
from random import randint
from hashlib import sha1
from hmac import new
import os, time


os.system("pip install -r requirements.txt")

from json_minify import json_minify
from requests import Session
from flask import Flask

import box


Parameters = {
    "community-link":
        "http://aminoapps.com/c/Howtopurr",

    "proxy": None
}

###################$
emailsPath = "acc.json"
###################


signatureKey="f8e7a61ac3f725941e3ac7cae2d688be97f30b93"
deviceKey="02b258c63559d8804321c5d5065af320358d366f"


GRAY = lambda *text, type = 1: f"\033[{type};30m" + " ".join(str(obj) for obj in text) + "\033[0m"
RED = lambda *text, type = 1: f"\033[{type};31m" + " ".join(str(obj) for obj in text) + "\033[0m"
GREEN = lambda *text, type = 1: f"\033[{type};32m" + " ".join(str(obj) for obj in text) + "\033[0m"
YELLOW = lambda *text, type = 1: f"\033[{type};33m" + " ".join(str(obj) for obj in text) + "\033[0m"
BLUE = lambda *text, type = 1: f"\033[{type};34m" + " ".join(str(obj) for obj in text) + "\033[0m"
MAGNETA = lambda *text, type = 1: f"\033[{type};35m" + " ".join(str(obj) for obj in text) + "\033[0m"
CYAN = lambda *text, type = 1: f"\033[{type};36m" + " ".join(str(obj) for obj in text) + "\033[0m"


#-----------------FLASK-APP-----------------
app = Flask(__name__)
@app.route('/')
def home():
    return "~~8;> ~~8;>"
#----------------------------------------------------


class Amino :

    def __init__(
        self : object,
        device : str = None,
        proxy : str = None,
        uuid : str = None,
        timeout : int = 15
    ) -> None :

        self.proxies = dict(https = proxy)
        self.device = device or None
        self.session = Session()
        self.uuid = uuid or str(uuid_gen())
        self.timeout = timeout
        self.userId, self.sid = None, None



    def device_gen(
        self : object,
        device_info : bytes = bytes.fromhex("42") + os.urandom(20)
    ) -> str :

        new_device: str = (
            device_info + new(
                bytes.fromhex(deviceKey),
                device_info,
                sha1
            ).digest()
        ).hex().upper()
        return new_device



    def headers(
        self : object,
        data : str = None
    ) -> dict :

        if not self.device :
            self.device = self.device_gen()

        headers = {
            "NDCDEVICEID": self.device,
            "SMDEVICEID": self.uuid,
            "Accept-Language": "en-EN",
            "Content-Type":
                "application/json; charset=utf-8",
            "User-Agent":
                'Dalvik/2.1.0 (Linux; U; Android 7.1; LG-UK495 Build/MRA58K; com.narvii.amino.master/3.3.33180)', 
            "Host": "service.narvii.com",
            "Accept-Encoding": "gzip",
            "Connection": "keep-alive"
        }

        if data is not None:
            headers["Content-Length"] = str(len(data))
            headers["NDC-MSG-SIG"] = self.sig(data)

        if self.sid is not None:
            headers["NDCAUTH"] = "sid=%s" % self.sid

        return headers



    def sig(
        self : object,
        data : str = None
    ) -> str :

        signature: str = b64encode(
            bytes.fromhex("42") + new(
                bytes.fromhex(signatureKey),
                data.encode("utf-8"),
                sha1
            ).digest()
        ).decode("utf-8")
        return signature



    def request(
        self : object,
        method : str,
        url : str,
        data : dict = None,
        minify : bool = False,
        **kwargs : dict
    ) -> dict :

        assert method.upper() in ("DELETE", "GET", "POST", "PUT"), "Invalid method -> %r" % method

        url = f"https://service.narvii.com/api/v1/{url}"

        if self.sid is not None:
            url += f"?sid={self.sid}"

        if isinstance(data, dict):
            data["timestamp"] = int(timestamp() * 1000)
            data = dumps(data)

            if minify is True:
                data = json_minify(data)

        with self.session.request(
            method = method.upper(),
            url = url,
            headers = self.headers(data = data),
            data = data,
            proxies = self.proxies,
            timeout = self.timeout
        ) as response:

            try: return response.json()
            except: raise Exception(response.text)



    def get_from_code(
        self : object,
        code : str
    ) -> dict :

        return self.request(
            method = "GET",
            url = f"g/s/link-resolution?q={code}"
        )


    def login(
        self : object,
        email : str,
        password : str,
        secret : str = None,
    ) -> dict :

        data = {
            "email": email,
            "v": 2,
            "secret": f"0 {password}" if not secret else secret,
            "deviceID": self.device,
            "clientType": 100,
            "action": "normal",
        }

        resp = self.request(
            method = "POST",
            url = "g/s/auth/login",
            data = data
        )

        self.sid = resp.get("sid", None)
        self.userId = resp.get("account", {}).get("uid", None)

        return resp.copy()



    def join_community(
        self : object,
        comId : int,
        invitationId : str
    ) -> dict :

        data = {}

        if invitationId:
            data["invitationId"] = invitationId

        resp = self.request(
            method = "POST",
            url = f"x{comId}/s/community/join",
            data = data
        )

        return resp.copy()



    def lottery(
        self : object,
        comId : int,
        tz : (int, str)
    ) -> dict :

        data = {
            "timezone": tz,
        }

        resp = self.request(
            method = "POST",
            url = f"x{comId}/s/check-in/lottery",
            data = data
        )

        return resp.copy()



    def send_active_obj(
        self : object,
        comId : int,
        tz : int,
        timers : list
    ) -> dict :

        data = {
            "userActiveTimeChunkList": timers,
            "optInAdsFlags": 2147483647,
            "timezone": tz
        }

        resp = self.request(
            method = "POST",
            url = f"x{comId}/s/community/stats/user-active-time",
            data = data,
            minify = True
        )

        return resp.copy()



class Generator(object) :

    joined = False
    logged = 0

    login_sleep = 0.2
    join_community_sleep = 0.2
    lottery_sleep = 1
    send_active_obj_sleep = 2

    def get_community(
        self : object,
        amino : object = None
    ) -> None :

        fromcode = amino.get_from_code(
            code = Parameters.get("community-link")
        )

        extensions = fromcode.get("linkInfoV2", {}).get("extensions", {})

        self.comId = extensions["community"].get("ndcId", None)
        self.invitationId = extensions.get("invitationId", None)



    def login_task(
        self : object,
        amino : object,
        email : str,
        password : str
    ) -> None :

        time.sleep(self.login_sleep)
        resp = amino.login(
            email = email,
            password = password
        )

        print("[" + BLUE("login") + f"][{email}]: {resp['api:message']}.")



    def join_community_task(
        self : object,
        amino : object,
        email : str
    ) -> None:

        time.sleep(self.join_community_sleep)
        resp = amino.join_community(
            comId = self.comId,
            invitationId = self.invitationId
        )
        
        print("[" + CYAN("join-community") + f"][{email}]: {resp['api:message']}.")



    def lottery_task(
        self : object,
        amino : object,
        email : str
    ) -> None :

        time.sleep(self.lottery_sleep)
        resp = amino.lottery(
            comId = self.comId,
            tz = box.tzFilter(hour = 23)
        )

        print("[" + GREEN("lottery") + f"][{email}]: {resp['api:message']}")



    def send_active_obj_task(
        self : object,
        amino : object,
        email : str
    ) -> None :

        time.sleep(self.send_active_obj_sleep)
        resp = amino.send_active_obj(
            comId = self.comId,
            tz = box.tzFilter(hour = 23),
            timers = list({
                "start": int(timestamp()),
                "end": int(timestamp() + 300)
            } for _ in range(50)),
        )

        print("[" + MAGNETA("main-proccess") + f"][{email}]: {resp['api:message']}.")



    def run(
        self : object
    ) -> None :
 
        self.get_community(Amino(
            proxy = Parameters.get("proxy")
        ))
 
        time.sleep(1)

        with open(emailsPath, "r") as File:
            accounts = loads(File.read())

        apps = [
            Amino(
                device = x["device"],
                uuid = x.get("uuid", None),
                proxy = Parameters.get("proxy")
            ) for x in accounts
        ]

        while True:
            try:
                # login task
                if (timestamp() - self.logged) >= 60 * 60 * 23 :
                    print()
                    [self.login_task(
                        amino = amino,
                        email = x["email"],
                        password = x["password"],
                    ) for amino, x in zip(
                        apps, accounts
                    )]; print()

                # join community task
                if self.joined is False:
                    [self.join_community_task(
                        amino = amino,
                        email = x["email"],
                    ) for amino, x in zip(
                        apps, accounts
                    )]; print()


                # lottery task
                if (timestamp() - self.logged) >= 60 * 60 * 23 :
                    [self.lottery_task(
                        amino = amino,
                        email = x["email"],
                    ) for amino, x in zip(
                        apps, accounts
                    )]; self.logged = int(timestamp()); print()



                # 24 task of send active object
                for _ in range(24):
                    [self.send_active_obj_task(
                        amino = amino,
                        email = x["email"],
                    ) for amino, x in zip(
                        apps, accounts
                    )]; print()

                    time.sleep(3)
                    print()

            except Exception as Error:
                print(f"[" + RED(["email"]) + "]][" + RED("error") + f"]]: {str([Error]).strip('[]')}")



def main() -> None:
    if not Parameters.get("community-link", "")[::-1][:Parameters.get("community-link", "")[::-1].index("/")][::-1]:
        print("Community not detected in %r" % 'Parameters["community-link"]')
        exit()

    Thread(
        target = app.run,
        kwargs = dict(
            host = "0.0.0.0",
            port = randint(2000, 9000)
        )
    ).start()

    generator = Generator()
    generator.run()


if __name__ == "__main__":
    box.clear(); main()
