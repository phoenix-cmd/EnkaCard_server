from enkacard import encbanner
import asyncio
import os
import concurrent.futures

# from enkanetwork import EnkaNetworkAPI
from fastapi import FastAPI
from io import BytesIO
import enkanetwork
from fastapi.responses import (
    JSONResponse,
)  
import enkacard
import uvicorn
import requests

# client = EnkaNetworkAPI()

# import asyncio

# async def card():
#     print("cret")
#     async with encbanner.ENC(uid = "811455610") as encard:
#         print("creting")
#         return await encard.creat()

# result = asyncio.run(card()) 

# print(result)

# data_dir = "/tmp/data"
# if not os.path.exists(data_dir):
#     os.makedirs(data_dir)
# data_dir = "/tmp/langs"
# if not os.path.exists(data_dir):
#     os.makedirs(data_dir)

# async def main():
#     async with client:
#         await client.update_assets(lang = ["EN", "CHT"], path="/tmp")

# asyncio.run(main())

app = FastAPI()
# app = FastAPI(lifespan=lifespan)
async def card(id, designtype):
    async with encbanner.ENC(uid = str(id)) as encard:
        return await encard.creat(template = (2 if str(designtype) == "2" else 1))
    
@app.get("/{id}")  # Correct route definition without prefix
async def characters(id: int, design: str = "1"):  # Use async and await
    try:
        # characters = []
        result = await card(id, design)  # Use await instead of asyncio.run()
        print(result)
        characters = process_images(result)
        print(characters)

        # Return valid JSON response using FastAPI's JSONResponse
        return JSONResponse(content={'response': characters})

    except enkanetwork.exception.VaildateUIDError:
        return JSONResponse(content={'error': 'Invalid UID. Please check your UID.'}, status_code=400)

    except enkacard.enc_error.ENCardError:
        return JSONResponse(content={'error': 'Enable display of the showcase in the game or add characters there.'}, status_code=400)

    except Exception as e:
        return JSONResponse(content={'error': 'UNKNOWN ERR: ' + str(e)}, status_code=500)

@app.get("/")
def hello_world():
    return 'AMERICA YA HALLO!!'

# @app.route("/update_char")
# def upload():
    # data_dir = "/tmp/data"

    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)

    # data_dir = "/tmp/langs"

    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)
    # asyncio.run(update_genshin())
#     return 'Update smth ig!!'



def upload_image(data):
    print(data)
    url = "https://fighter-programmer-uploader.hf.space/upload"
    files = {'file': ('file', data, "image/png")}  
    response = requests.post(url, files=files)
    
    if response.status_code != 200:
        raise Exception(f"HTTP Error: {response.status_code}")
    
    try:
        body = response.json()
        if body["url"]:
            return body["url"]
        else:
            raise Exception(f"Telegraph error: {body.get('error', 'Unknown error')}")
    except (ValueError, KeyError, IndexError) as e:
        raise Exception(f"Failed to parse response: {str(e)}")
def process_image(dt):
    with BytesIO() as byte_io:
        dt.card.save(byte_io, "PNG")
        byte_io.seek(0)
        image_url = upload_image(byte_io)
        
        return {
            "name": dt.name,
            "url": image_url
        }

def process_images(result):
    characters = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Execute image uploads in parallel
        futures = [executor.submit(process_image, dt) for dt in result.card]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                characters.append(future.result())
            except Exception as e:
                print(f"Error processing image: {e}")
    
    return characters
if __name__ == "__main__":
    # data_dir = "/tmp/data"

    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)

    # data_dir = "/tmp/langs"

    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir)
    # asyncio.run(update_genshin())
    uvicorn.run("main:app", host="0.0.0.0", port=7860, workers=8, timeout_keep_alive=60000)