import os
import time
import requests
from flask import Flask

# --- CLES (viennent de Render, ne touche pas) ---
PAGE_ID = os.environ.get("PAGE_ID")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
API_FOOTBALL_KEY = os.environ.get("API_FOOTBALL_KEY")

# --- Petit serveur pour garder Render réveillé ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Foot entre nous en ligne 🔥"

# --- Fonctions Facebook ---
def poster_sur_facebook(message):
    url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    data = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    r = requests.post(url, data=data)
    print("Post Facebook:", r.status_code, r.text)
    return r.json()

# --- Fonction API-Football ---
def get_matchs_live():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {
        "x-apisports-key": API_FOOTBALL_KEY
    }
    r = requests.get(url, headers=headers)
    return r.json().get("response", [])

def format_match(m):
    equipe_dom = m['teams']['home']['name']
    equipe_ext = m['teams']['away']['name']
    score_dom = m['goals']['home']
    score_ext = m['goals']['away']
    minute = m['fixture']['status']['elapsed']
    ligue = m['league']['name']
    return f"⚽ LIVE - {ligue}\n\n{equipe_dom} {score_dom} - {score_ext} {equipe_ext}\n🕐 {minute}'\n\n#FootEntreNous"

# --- Boucle principale ---
def boucle_bot():
    deja_poste = set()
    while True:
        try:
            print("Vérification des matchs live...")
            matchs = get_matchs_live()
            for m in matchs:
                id_match = m['fixture']['id']
                # On ne poste que les ligues qu'on veut
                ligue_id = m['league']['id']
                # 2=Champions League, 3=Europa, 39=Premier League, 140=La Liga, 135=Serie A, 78=Bundesliga, 61=Ligue 1, 1=Coupe du monde
                if ligue_id in [2, 3, 39, 140, 135, 78, 61, 1]:
                    cle = f"{id_match}-{m['goals']['home']}-{m['goals']['away']}"
                    if cle not in deja_poste:
                        msg = format_match(m)
                        poster_sur_facebook(msg)
                        deja_poste.add(cle)
            time.sleep(120)  # Vérifie toutes les 2 minutes
        except Exception as e:
            print("Erreur:", e)
            time.sleep(60)

if __name__ == "__main__":
    import threading
    t = threading.Thread(target=boucle_bot)
    t.start()
    app.run(host="0.0.0.0", port=10000)
