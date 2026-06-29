import os
import json
import urllib.request
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
HAFIZA_DOSYASI = "hafiza.json"

def hafiza_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def hafiza_kaydet(mesajlar):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(mesajlar, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mesaj", methods=["POST"])
def mesaj():
    data = request.json
    kullanici_mesaji = data.get("mesaj", "")

    gecmis = hafiza_yukle()
    gecmis.append({"role": "user", "parts": [{"text": kullanici_mesaji}]})

    sistem_mesaji = {
        "role": "user",
        "parts": [{"text": "Kisa ve net cevap ver. Gereksiz uzun yazma."}]
    }
    gemini_gecmis = [sistem_mesaji] + gecmis[-4:]

    payload = json.dumps({
        "contents": gemini_gecmis,
        "generationConfig": {
            "maxOutputTokens": 150,
            "temperature": 0.7
        }
    }).encode("utf-8")

    api_key = os.environ.get("GEMINI_API_KEY")
    model = "gemini-2.0-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    req = urllib.request.Request(url, data=payload, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            bot_cevabi = result["candidates"][0]["content"]["parts"][0]["text"]

            gecmis.append({"role": "model", "parts": [{"text": bot_cevabi}]})
            hafiza_kaydet(gecmis)

            return jsonify({"cevap": bot_cevabi})
    except Exception as e:
        hata = str(e)
        if "429" in hata:
            return jsonify({"cevap": "API limiti doldu veya cok hizli mesaj attik. Biraz bekleyip tekrar dene."})
        return jsonify({"cevap": f"Hata: {hata}"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)