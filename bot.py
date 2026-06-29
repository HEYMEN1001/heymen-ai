import os
import json
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

sistem_talimati = """
Sen samimi, esprili ve yardımsever bir Türkçe sohbet botusun.
Konuşma tarzın arkadaş canlısı, bazen şakacı ama her zaman saygılı.
Kısa ve net cevaplar ver, gereksiz uzatma.
Kullanıcı senden teknik/kodlama yardımı isterse, ciddi ve detaylı bir mühendis gibi cevap ver.
Kullanıcı senden duygusal destek isterse, sıcak ve anlayışlı ol, asla yargılamadan dinle.
"""

HAFIZA_DOSYASI = "hafiza.json"

def hafizayi_yukle():
    if os.path.exists(HAFIZA_DOSYASI):
        with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def hafizayi_kaydet(gecmis):
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(gecmis, f, ensure_ascii=False, indent=2)

# Programı açar açmaz eski hafızayı yükle
gecmis = hafizayi_yukle()

if gecmis:
    print(f"(Eski sohbetten {len(gecmis)} mesaj hatırlanıyor)\n")

print("Botla sohbet başladı! Çıkmak için 'q' yaz.\n")

while True:
    kullanici_mesaji = input("Sen: ")

    if kullanici_mesaji.lower() == "q":
        print("Görüşürüz!")
        break

    gecmis.append({"role": "user", "parts": [{"text": kullanici_mesaji}]})

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=gecmis,
        config={
            "system_instruction": sistem_talimati
        }
    )

    bot_cevabi = response.text
    print(f"Bot: {bot_cevabi}\n")

    gecmis.append({"role": "model", "parts": [{"text": bot_cevabi}]})

    # Her mesajdan sonra hafızayı diske kaydet
    hafizayi_kaydet(gecmis)