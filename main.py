import enkacard
import enkacard.encbanner
import enkanetwork
import asyncio
from flask import Flask, jsonify, request
import requests
from io import BytesIO
from enkanetwork import EnkaNetworkAPI

enka_update = EnkaNetworkAPI()

async def update_genshin():
    async with enka_update:
        await enka_update.update_assets()

app = Flask(__name__)

async def card(id, designtype):
    async with enkacard.encbanner.ENC(uid = str(id)) as encard:
        return await encard.creat(template = (2 if str(designtype) == "2" else 1))
    
@app.route("/<int:id>")
def characters(id):
    try:
        characters = []
        result = asyncio.run(card(id, request.args.get('design')))
        for dt in result.card:
            byte_io = BytesIO()
            dt.card.save(byte_io, "PNG")
            byte_io.seek(0)
            characters.append({
                "name":   dt.name,
                "url" :   upload_image(byte_io)
            })
            # print(upload_image(byte_io))
        return jsonify({'response': characters}) 
    except enkanetwork.exception.VaildateUIDError:
        return jsonify({'error': 'Invalid UID. Please check your UID.'}), 400 
    except enkacard.enc_error.ENCardError:
        return jsonify({'error': 'Enable display of the showcase in the game or add characters there.'}), 400 
    # for card in result.card:
        # print(card.card.save(card.name + ".png"))
    # print(result.card)
        # return e

@app.route("/")
def hello_world():
    return 'AMERICA YA HALLO!!'

def upload_image(data):
    url = "https://telegra.ph/upload"
    files = {'file': ('file', data.read(), "image/png")}
    response = requests.post(url, files=files)
    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code}")
    
    body = response.json()
    try:
        if 'src' in body[0]:
            return "https://telegra.ph" + body[0]['src']
        else:
            return Exception(f"telegraph: {body['error']}")
    except Exception:
            return Exception(f"telegraph: {body['error']}")
asyncio.run(update_genshin())
    
if __name__ == "__main__":
    app.run(debug=True)