import base64
from openai import OpenAI
import json
import sqlite3
import os
import sys
from PIL import Image

# Tähän kohtaan syötetään oma API-avain
client = OpenAI(
    api_key="SYÖTÄ API-AVAIN"
)

# Haetaan nykyinen kirjasto
current_dir = os.getcwd()

# Etsitään kuvatiedosto nykyisestä kansiosta
image_extensions = (".jpg")
image_files = [f for f in os.listdir(current_dir) if f.lower().endswith(image_extensions)]

# Tallennetaan kuvatiedoston nimi muuttujaan tai lopetetaan ohjelma, jos 0 tai >1 kuvaa
if len(image_files) == 1:
    image_filename = image_files[0]
else:
    print("Ei löytynyt yksittäistä kuvatiedostoa tai niitä on useampi.")
    sys.exit()

def resize_image(input_path, output_path, scale_factor):
    
    # Avataan kuva
    image = Image.open(input_path)
    
    # Alkuperäiset mitat
    original_width, original_height = image.size
    
    # Lasketaan uusi koko
    new_width = int(original_width * scale_factor)
    new_height = int(original_height * scale_factor)
    
    # Muutetaan resoluutio
    image_resized = image.resize((new_width, new_height), Image.LANCZOS)

    # Käännetään kuva oikeaan asentoon
    image_rotated = image_resized.transpose(Image.ROTATE_270)

    # Tallennetaan uusi kuva
    image_rotated.save(output_path)
    print(f"Kuvan uusi koko: {new_width} x {new_height}, tallennettu: {output_path}")

# Ajetaan funktio
resize_image(image_filename, "results.jpg", 0.50)

# Kuvan encodaus base64-muotoon
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Kuvan polku
image_path = "results.jpg"

# Base64 string
base64_image = encode_image(image_path)

# Ladataan luotu JSON-schema
def load_json_schema(schema_file: str) -> dict:
    with open(schema_file, 'r') as file:
        return json.load(file)

workout_schema = load_json_schema("workout_log.json")

# API-kutsu OpenAI:n mallille
response = client.chat.completions.create(
    model="gpt-4o-mini",
    response_format={"type": "json_object"},
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Tässä kuvassa on käsinkirjoitettu treeni. "
                            "Sivun ylälaidassa on päivämäärä. "
                            "Ensimmäisessä sarakkeessa on liike, toisessa toistot ja kolmannessa painot. "
                            "Tee JSON tiedosto, johon kopioit jokaisen rivin kuvasta."
                            "Käytä seuraavaa JSON Schemaa: "+json.dumps(workout_schema)
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                }
            ]
        }
    ],
)

# Luodaan muuttuja, johon vastauksen sisältö siirretään
json_data = json.loads(response.choices[0].message.content)
print(json_data)

# Avataan tietokantayhteys
conn = sqlite3.connect("workouts.db")
cursor = conn.cursor()

# Siirretään treeni tietokantaan
for workout in json_data['workouts']:
    cursor.execute(
        "INSERT INTO workouts (date, exercise, reps, weight) VALUES (?, ?, ?, ?)",
        (json_data['date'], workout['exercise'], workout['reps'], workout['weight'])
    )

conn.commit()  # Tallennetaan muutokset
conn.close()   # Suljetaan yhteys

# Poistetaan kuvatiedostot, jotka seuraavaa muotoa
image_extensions = (".jpg", ".jpeg")

# Käydään läpi kaikki tiedostot nykyisessä kansiossa
for filename in os.listdir():
    if filename.lower().endswith(image_extensions):  # Tarkistetaan, onko tiedosto kuva
        os.remove(filename)  # Poistetaan tiedosto
        print(f"Poistettu: {filename}")

print("Treenitiedot viety tietokantaan!")