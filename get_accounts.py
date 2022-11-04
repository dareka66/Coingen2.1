from time import time as timestamp
from uuid import uuid4 as uuid_gen
from contextlib import suppress
from base64 import b64encode
from json import dumps, loads
from hashlib import sha1
from hmac import new
import os

os.system("pip install json_minify requests")

from json_minify import json_minify
from requests import Session

import box


####################
emailsPath = "acc.json"
##################


signatureKey="f8e7a61ac3f725941e3ac7cae2d688be97f30b93"
deviceKey="02b258c63559d8804321c5d5065af320358d366f"
accounts = list()


class Amino:
    
    def __init__(
        self : object,
        device: str = None,
        proxy: str = None
    ) -> None :

        self.device = device or None
        self.session = Session()
        self.proxies = dict(https = proxy)
        self.uuid = str(uuid_gen())
        self.sid, self.userId = None, None


    def device_gen(
        self: object,
        device_info: bytes = bytes.fromhex("42") + os.urandom(20)
    ) -> str:

        new_device: str = (
            device_info + new(
                bytes.fromhex(deviceKey),
                device_info,
                sha1
            ).digest()
        ).hex().upper()
        return new_device


    def sig(
        self, data: (str, dict) = None
    ) -> str:

        signature: str = b64encode(
            bytes.fromhex("42") + new(
                bytes.fromhex(signatureKey),
                data.encode("utf-8"),
                sha1
            ).digest()
        ).decode("utf-8")
        return signature


    def headers(
        self: object,
        data: str = None
    ) -> dict:

        if not self.device:
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


    def request(
        self: object,
        method: str,
        url: str,
        data: dict = None,
        minify: bool = False,
        **kwargs: dict
    ) -> dict:

        assert method.upper() in ("DELETE", "GET", "POST", "PUT"), "Invalid method -> %r" % method

        url = f"https://service.narvii.com/api/v1/{url}"

        if self.sid is not None and method.upper() == "GET" :
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
            proxies = self.proxies
        ) as response:

            if response.status_code != 200:
                try: raise Exception(response.json())
                except: raise Exception(response.text)

            return response.json()


    def login(
        self: object,
        email: str,
        password: str,
        secret: str = None,
    ) -> dict:

        if not self.device:
            self.device = self.device_gen()

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



def accLoad() -> None:
    global accounts
    
    if not os.path.exists(emailsPath):
        with open(emailsPath, "w") as File:
            File.write("[]")

    with suppress(Exception):
        with open(emailsPath, "r") as File:
            content = File.read()

        accounts = loads(content)



def main() -> None:
    accLoad(); box.clear()
    while True:
        print("~", len(accounts), "\033[1;32maccounts saved\033[0m!\n")

        email = input(">> Email?: ")
        password = input(">> Password?: ")

        try:
            amino = Amino()
            amino.login(
                email = email,
                password = password
            )

            accounts.append({
                "email": str(email),
                "password": str(password),
                "device": str(amino.device),
                "uuid": str(amino.uuid),
                "sid": str(amino.sid),
            })

        except Exception as Error:
            args = Error.args[0]
            with suppress(Exception):
                args = loads(str(Error.args[0]))

            print("\n~ \033[1;31mERROR\033[0m -> %r" % (args if isinstance(args, str) else args.get("api:message")))
            continue

        data = dumps(accounts, indent = 4)
        with open(emailsPath, "w") as File:
            File.write(data)


if __name__ == "__main__":
    main()