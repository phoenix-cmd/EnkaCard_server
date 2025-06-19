from fastapi import FastAPI
from fastapi.responses import JSONResponse
from enkacard import encbanner
from enkacard.enc_error import ENCardError
import enkanetwork
import concurrent.futures
from io import BytesIO
import requests
import uvicorn
import os

app = FastAPI()


# 🔧 Generate single character card
async def generate_card(uid, design):
    async with encbanner.ENC(uid=str(uid)) as encard:
        return await encard.creat(template=(2 if str(design) == "2" else 1))


# 🌐 GET /<uid>/<char_id> — image generator
@app.get("/{uid}/{char_id}")
async def get_card_by_char(uid: int, char_id: int, design: str = "1"):
    try:
        result = await generate_card(uid, design)

        for dt in result.card:
            if dt.character_id == char_id:
                image = process_image(dt)
                return JSONResponse(content={"card": [image]})

        return JSONResponse(content={"error": "Character not found in profile."}, status_code=404)

    except enkanetwork.exception.VaildateUIDError:
        return JSONResponse(content={"error": "Invalid UID."}, status_code=400)

    except ENCardError:
        return JSONResponse(content={"error": "Showcase not enabled or character not available."}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": f"Server error: {str(e)}"}, status_code=500)


# 🖼️ Upload image
def upload_image(data):
    url = "https://fighter-programmer-uploader.hf.space/upload"
    files = {"file": ("file", data, "image/png")}
    response = requests.post(url, files=files)

    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code}")

    try:
        body = response.json()
        if body["url"]:
            return body["url"]
        raise Exception("Missing URL in response.")
    except Exception as e:
        raise Exception(f"Failed to parse response: {str(e)}")


# 🎨 Process one image
def process_image(dt):
    with BytesIO() as byte_io:
        dt.card.save(byte_io, "PNG")
        byte_io.seek(0)
        image_url = upload_image(byte_io)
        return {
            "name": dt.name,
            "url": image_url
        }


# ✅ Health check
@app.get("/")
def root():
    return {"message": "EnkaCard API is up 🚀"}


# 🏁 Launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
