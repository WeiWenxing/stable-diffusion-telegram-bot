from pyrogram import Client, filters
from pyrogram.types import *
import os
import json
import requests
import io
import random
from PIL import Image, PngImagePlugin
import base64
from io import BytesIO

import webuiapi

from dotenv import load_dotenv
load_dotenv()

API_ID = os.environ.get("API_ID", None) 
API_HASH = os.environ.get("API_HASH", None) 
SD_URL = os.environ.get("SD_URL", None) 

app = Client(
    "stable",
    api_id=API_ID,
    api_hash=API_HASH,
)

# create API client
api = webuiapi.WebUIApi()

# create API client with custom host, port
api = webuiapi.WebUIApi(host='127.0.0.1', port=7861, sampler='DPM++ SDE Karras', steps=10)

# create API client with custom host, port and https
#api = webuiapi.WebUIApi(host='webui.example.com', port=443, use_https=True)

# create API client with default sampler, steps.
#api = webuiapi.WebUIApi(sampler='Euler a', steps=20)

# optionally set username, password when --api-auth is set on webui.
#api.set_auth('username', 'password')


@app.on_message(filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    Photo = "https://media.discordapp.net/attachments/1028156834944655380/1062018608022171788/3aac7aaf-0065-40aa-9e4d-430c717b3d87.jpg"

    buttons = [[
        InlineKeyboardButton("Add to your group",
                             url="http://t.me/botname?startgroup=true"),
        InlineKeyboardButton("Channel", url="https://t.me/aipicfree"),
        InlineKeyboardButton("Support", url="https://t.me/aipicfree")
    ]]
    await message.reply_photo(
        photo=Photo,
        caption=
        f"Hello! I'm botname Ai and I can make an anime-styled picture!\n\n/generate - Reply to Image\n/draw text to anime image\n\nPowered by @aipicfree",
        reply_markup=InlineKeyboardMarkup(buttons))

prompt_negative = r'(worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, backlight,(ugly:1.331), (duplicate:1.331), (morbid:1.21), (mutilated:1.21), (tranny:1.331), deformed eyes, deformed lips, mutated hands, (poorly drawn hands:1.331), blurry, (bad anatomy:1.21), (bad proportions:1.331), three arms, extra limbs, extra legs, extra arms, extra hands, (more than 2 nipples:1.331), (missing arms:1.331), (extra legs:1.331), (fused fingers:1.61051), (too many fingers:1.61051), (unclear eyes:1.331), bad hands, missing fingers, extra digit, (futa:1.1), bad body, pubic hair, glans, easynegative, three feet, four feet, (bra:1.3)'

def get_dress_mask(photo, color):
    prompt_positive = f'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0 sketch_color="{color}" sketch_alpha=80.0]dress[/txt2mask]see-through'
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.35, inpainting_fill=1)
    return result

def dress_api(photo, mask, strength, inp_fill, color):
    print(mask)
    print(f'strength={strength}, inp_fill={inp_fill}')
    prompt_positive = f'(8k, RAW photo, best quality, masterpiece:1.2), (realistic, photo-realistic:1.37), fmasterpiecel, 1girl, extremely delicate facial, perfect female figure, ({color} strapless dress:1.6), see-through, smooth fair skin, bare shoulders, clavicle, large breasts, cleavage, slim waist, very short hair, an extremely delicate and beautiful, extremely detailed,intricate,'
    print(prompt_positive)
    return api.img2img(images=[photo], prompt=prompt_positive,negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=strength, inpainting_fill=inp_fill, mask_image=mask)

def tripple_api(photo, mask, strength, inp_fill):
    print(mask)
    print(f'strength={strength}, inp_fill={inp_fill}')
    prompt_positive = f'(8k, RAW photo, best quality, masterpiece:1.2), (realistic, photo-realistic:1.37), fmasterpiecel, 1girl, nsfw, perfect female figure, (nude:1.6), smooth fair skin, clavicle, large breasts, slim waist, very short hair, an extremely delicate and beautiful, extremely detailed,intricate,'
    print(prompt_positive)
    return api.img2img(images=[photo], prompt=prompt_positive,negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=strength, inpainting_fill=inp_fill, mask_image=mask)

def byteBufferOfImage(img, mode):
    img_buffer = BytesIO()
    img.save(img_buffer, mode)
    img_buffer.seek(0)
    return img_buffer
    

@app.on_message(filters.photo)
async def img2img(client, message):
    if message.photo:
        print("Message contains one photo.")
        photo_path = await client.download_media(message.photo.file_id)
        print(photo_path)
        with open(photo_path, "rb") as f:
            file_bytes = f.read()
        img_ori = Image.open(BytesIO(file_bytes))

        result = get_dress_mask(img_ori, "229,205,197")
        result = get_dress_mask(img_ori, "wheat")
        print("=============================mask===============================")
        for img_mask in result.images:
            if img_mask.mode == "RGBA":
                mask = img_mask
            await message.reply_photo(byteBufferOfImage(img_mask, 'PNG'))

        print(mask)
        #img = img_ori
        img = result.image
        colors = ['white', 'pink', 'red', 'blue', 'yellow', 'green', 'black']
        random.shuffle(colors)
        color = random.choice(colors)
        for i in range(1): ## for each color
            #color = random.choice(colors)
            result = dress_api(img, mask, 0.45, 1, color)
            print(f"=============================result{i}: color_{color}===============================")
            for image in result.images:
                await message.reply_photo(byteBufferOfImage(image, 'JPEG'))
                img_input = image
                for i in range(2): ## iteration for change clothes
                    result1 = dress_api(img_input, mask, 0.45, 1, color)
                    img_input = result1.image 
                    await message.reply_photo(byteBufferOfImage(img_input, 'JPEG'))
                for i in range(2): ## iteration for tripple
                    result1 = tripple_api(img_input, mask, 0.45, 1)
                    img_input = result1.image 
                    await message.reply_photo(byteBufferOfImage(img_input, 'JPEG'))

app.run()
