import enkacard
# from enkacard import enkatools
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
        await enka_update.update_assets(lang = ["EN"])

# async def update_enka():
#     tools = enkatools.Tools()
#     result = await tools.update_assets(path = None)
#     return result

app = Flask(__name__)

async def card(id, designtype):
    async with enkacard.encbanner.ENC(uid = str(id)) as encard:
        return await encard.creat(template = (2 if str(designtype) == "2" else 1))
    
@app.route("/<int:id>")
def characters(id):
    try:
        characters = []
        result = asyncio.run(card(id, request.args.get('design')))
        print(result)
        # for dt in result.card:
        #     byte_io = BytesIO()
        #     dt.card.save(byte_io, "PNG")
        #     byte_io.seek(0)
        #     characters.append({
        #         "name":   dt.name,
        #         "url" :   upload_image(byte_io)
        #     })
        for dt in result.card:
         with BytesIO() as byte_io:  # Automatically closes the BytesIO object after the block
             dt.card.save(byte_io, "PNG")
             byte_io.seek(0)
             image_url = upload_image(byte_io)
             
         characters.append({
             "name": dt.name,
             "url": image_url
         })
            # print(upload_image(byte_io))
        return jsonify({'response': characters}) 
    except enkanetwork.exception.VaildateUIDError:
        # return jsonify({'error': 'Invalid UID. Please check your UID.'}), 400 

        return jsonify({'error': 'Invalid UID. Please check your UID.'})

    except enkacard.enc_error.ENCardError:
        # return jsonify({'error': 'Enable display of the showcase in the game or add characters there.'}), 400 
        return jsonify({'error': 'Enable display of the showcase in the game or add characters there.'})
    except Exception as e:

        return jsonify({'error': 'UNKNOWN ERR' + e.__str__()})
    # for card in result.card:
        # print(card.card.save(card.name + ".png"))
    # print(result.card)
        # return e

@app.route("/")
def hello_world():
    return 'AMERICA YA HALLO!!'

@app.route("/update_char")
def upload():
    asyncio.run(update_genshin())
    return 'Update smth ig!!'

# def upload_image(data):
#     url = "https://telegra.ph/upload"
#     files = {'file': ('file', data.read(), "image/png")}
#     response = requests.post(url, files=files)
#     if response.status_code != 200:
#         raise Exception(f"HTTP Error: {response.status_code}")
    
#     body = response.json()
#     try:
#         if 'src' in body[0]:
#             return "https://telegra.ph" + body[0]['src']
#         else:
#             return Exception(f"telegraph: {body['error']}")
#     except Exception:
#             return Exception(f"telegraph: {body['error']}")
def upload_image(data):
    url = "https://telegra.ph/upload"
    files = {'file': ('file', data, "image/png")}  # Pass the file object directly
    response = requests.post(url, files=files)
    
    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code}")
    
    try:
        body = response.json()
        if isinstance(body, list) and 'src' in body[0]:
            return "https://telegra.ph" + body[0]['src']
        else:
            raise Exception(f"Telegraph error: {body.get('error', 'Unknown error')}")
    except (ValueError, KeyError, IndexError) as e:
        raise Exception(f"Failed to parse response: {str(e)}")
    
if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)