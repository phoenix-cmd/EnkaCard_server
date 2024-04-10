from enkacard import encbanner
import enkanetwork
import asyncio
from flask import Flask, jsonify
import requests
from io import BytesIO

app = Flask(__name__)

async def card(id):
    async with encbanner.ENC(uid = str(id)) as encard:
        return await encard.creat()
    
@app.route("/<int:id>")
def characters(id):
    try:
        characters = []
        result = asyncio.run(card(id))
        for dt in result.card:
            byte_io = BytesIO()
            dt.card.save(byte_io, "PNG")
            byte_io.seek(0)
            characters.append({
                "name":   dt.name,
                "url" :   upload_image(byte_io)
            })
            # print(upload_image(byte_io))
        return jsonify(characters) 
    except enkanetwork.exception.VaildateUIDError:
        return jsonify({'error': 'Invalid UID. Please check your UID.'}), 400 
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
            return f"telegraph: {body['error']}"
    except Exception:
            return f"telegraph: {body['error']}"
    
# if __name__ == "__main__":
#     app.run()