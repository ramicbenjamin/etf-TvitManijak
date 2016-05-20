import tweepy

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

import json

import threading
import time

import signal
import sys

#import wiringpi

auth = tweepy.OAuthHandler("RNCh6pIbLoex1mgL4GabVdjmE", "rBTcyyEYlLoW89Z7xMbK03VzMqt4XEWyLQBGDZVyHCG7wsfxgX")
auth.set_access_token("731180533212938240-sBh2t0xYdNxuByhSVPhWmra2EyobH7V", "19YCttvhwfJAzBcpab2e7kYbjxHmmhtUlDF1nso4pfnFy")

api = tweepy.API(auth)

mod = '0'
tracking = False

pin_r = 2
pin_g = 3
pin_b = 4

boje = {"crvena": pin_r, "zelena": pin_g, "plava": pin_b}

#wiringpi.wiringPiSetup()
#wiringpi.pinMode(pin_r,1) # set pins to output
#wiringpi.pinMode(pin_g,1)
#wiringpi.pinMode(pin_b,1)

class StdOutListener(StreamListener):
    def on_data(self, data):
        global tracking
        
        tvit = json.loads(data)
        
        if tracking == True:
            print("%s kaze \"%s\"" % (tvit["user"]["name"], tvit["text"]))
            komanda = tvit["text"]
            if tvit["text"].find("::") != -1:
                parsiraj_komandu(tvit["text"].replace("#etf2016us", "").strip(), tvit["user"]["screen_name"])
            
        return True

    def on_error(self, status):
        print(status)

    
def tracker():
    l = StdOutListener()
    stream = Stream(auth, l)
    stream.filter(track=['etf2016us'], async=True)

def signal_handler(signal, frame):
    while True:
        menu()

def parsiraj_komandu(komanda, komeOdgovoriti):
    if komanda[0:2] == "::":        
        try:
            prvaZagrada = komanda.index('(')
            nazivKomande = komanda[2:prvaZagrada]    
            parametri_svi = komanda[ prvaZagrada + 1 : -1 ]
            parametri = [x.strip() for x in parametri_svi.split(',')]

            if nazivKomande in funkcije:
                funkcije[nazivKomande](parametri, komeOdgovoriti)
            else:
                print("Data komanda ne postoji!")
        except ValueError:
            print("Nisu dati nikakvi parametri ili je nepostojeca komanda!")

def ledica(parametri, komeOdgovoriti):
    if len(parametri) != 2:
        print("@%s Neispravan broj parametara!" % komeOdgovoriti)
        api.update_status(status=("@%s Neispravan broj parametara!" % komeOdgovoriti))
        return
    
    koji_pin = parametri[0]
    upali = parametri[1]
    try:    
        # defaultni pin
        if(int(koji_pin) == -1):
            koji_pin = 2;

        #wiringpi.digitalWrite(int(koji_pin), int(upali))
        print("upali ledicu")
    
    except TypeError:
        print("@%s Pogresna komanda (jeste li fino unijeli parametre?" % komeOdgovoriti)
        api.update_status(status=("@%s Pogresna komanda (jeste li fino unijeli parametre?" % komeOdgovoriti))


def rgb_ledica(parametri, komeOdgovoriti):    
    if len(parametri) != 1:
        print("@%s Neispravan broj parametara!" % komeOdgovoriti)
        api.update_status(status=("@%s Neispravan broj parametara!" % komeOdgovoriti))
        return
    
    global pin_r
    global pin_g
    global pin_b
    global boje
    
    koja_boja = parametri[0].strip()
    print(koja_boja)

    try:
        if koja_boja not in boje:
            print("@%s Boja ne postoji!" % komeOdgovoriti)
            api.update_status(status=("@%s Boja ne postoji!" % komeOdgovoriti))
            return

        # prvo iskljuci sve
        for boja in boje:
            print("iskljucujem sve")            
            #wiringpi.digitalWrite(boje[boja], 0)

        # sad ukljuci koja treba
        print("ukljucujem koju treba")
        #wiringpi.digitalWrite(boje[koja_boja], 1)

        print("upali rgb ledicu")
        
    except TypeError:
        print("@%s Pogresna komanda (jeste li fino unijeli parametre?" % komeOdgovoriti)
        api.update_status(status=("@%s Pogresna komanda (jeste li fino unijeli parametre?" % komeOdgovoriti))

funkcije = {"ledica": ledica,
            "rgb_ledica": rgb_ledica
    
}
        
def menu():
    global tracking
    print("Izaberite mod: ")
    print("1 - Tvitajte nesto")
    print("2 - Pratite tvitove")
    print("3 - Izlaz")
    mod = input("Unesite izbor: ") # Treba validirati ovaj ulaz

    if mod == '1':
        tracking = False
        poruka = input("Ukucajte Tweet za slanje: ")
        api.update_status(status=poruka)
    elif mod == str('2'):
        tracking = True
        tracker()
        while True:
            time.sleep(1)
    elif mod == '3':
        sys.exit()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    while True:
        menu()
