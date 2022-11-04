'''Put the blog link of a public community'''
blogLink = "http://aminoapps.com/p/6kkfqo"

import json, os, time
from os import path
try: import pyfiglet, aminofix
except: os.system("pip install --upgrade pyfiglet amino.fix")
finally: import pyfiglet, aminofix
from aminofix.lib.util.exceptions import AccessDenied
from pyfiglet import figlet_format
os.system('cls' if os.name=='nt' else 'clear')


####################
emailFile = "acc.json"
####################


def main():
	print(f"\n\33[48;5;5m\33[38;5;234m ❮ {len(dictlist)} ACCOUNTS LOADED ❯ \33[0m\33[48;5;235m\33[38;5;5m \33[0m")
	for acc in dictlist:
		email=acc["email"]
		password=acc["password"]
		device=acc["device"]
		client=aminofix.Client(deviceId=device)
		time.sleep(0.5)
		try:
			client.login(email,password)
			print("\n°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°°")
			print("logged in" ,email)
			info=client.get_from_code(blogLink)
			comId=info.comId
			blogId=info.objectId
			time.sleep(0.5)
			client.join_community(comId)
			subClient = aminofix.SubClient(comId,profile=client.profile, deviceId=device)
			coin=client.get_wallet_info().totalCoins
			print(f'Coins: {coin}')
			time.sleep(2)
			timer = 0
			while True:
				if coin != 0 and timer <= 10:
					 if coin >=500:
						 subClient.send_coins(500, blogId)
						 print('>> Sent 500 successfully.')
						 coin -= 500
					 elif coin < 500 and coin != 0:
						 subClient.send_coins(coin, blogId)
						 print(f'>> Sent {coin} successfully.')
						 coin -= coin
				else: break
		except AccessDenied: print('>> Wait 2 hours to transfer the coins')
		except Exception as e: print(e)

if __name__ == "__main__":
    file = path.dirname(path.abspath(__file__))
    acc = path.join(file, emailFile)
    dictlist=[]
    with open(acc) as f:
        dictlist = json.load(f)
    print(figlet_format("Transfer By Blog", font="big", width=60))
    main()
    exit(f"\n\n\33[48;5;5m\33[38;5;234m ❮ Transferred all coins from {len(dictlist)} ACCOUNTS ❯ \33[0m\33[48;5;235m\33[38;5;5m \33[0m")
