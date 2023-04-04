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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import webuiapi

from dotenv import load_dotenv
load_dotenv()

API_ID = os.environ.get("API_ID", None) 
API_HASH = os.environ.get("API_HASH", None) 
TOKEN = os.environ.get("TOKEN", None) 
SD_URL = os.environ.get("SD_URL", None) 

app = Client(
    "stable",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
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

def byteBufferOfImage(img, mode):
    img_buffer = BytesIO()
    img.save(img_buffer, mode)
    img_buffer.seek(0)
    return img_buffer

def saveImage(image: Image, fileName): 
    image.save(f'{fileName}.jpg', 'JPEG', quality=90)
    return f'{fileName}.jpg'


def fileName(pre):
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    chars1 = "1234564890"
    gen1 = random.choice(chars)
    gen2 = random.choice(chars)
    gen3 = random.choice(chars1)
    gen4 = random.choice(chars)
    gen5 = random.choice(chars)
    gen6 = random.choice(chars)
    gen7 = random.choice(chars1)
    gen8 = random.choice(chars)
    gen9 = random.choice(chars)
    gen10 = random.choice(chars1)
    word = f"{pre}-{gen1}{gen2}{gen3}{gen4}{gen5}{gen6}{gen7}{gen8}{gen9}{gen10}"
    return word

def txt2Image(msg, client, message):
    try:
        name = msg.split(':')[1]
    except Exception as e:
        name = msg
    prompt_pos = f'(beautiful face)), extremely delicate facial,(best quality),(extremely detailed cg 8k wallpaper),(arms behind back:1.2) ,fmasterpiecel, an extremely delicate and beautiful, extremely detailed,intricate,photorealistic. 1girl, hyper detailed, (nude:1.4), (large breasts:1.3), slim waist, long legs, high heels, long hair,light smile, outdoors, {msg}'
    #prompt_pos = f'(beautiful face), extremely delicate facial,(best quality),(extremely detailed cg 8k wallpaper),arms behind back,fmasterpiecel, an extremely delicate and beautiful, extremely detailed,intricate,photorealistic. 1girl, hyper detailed, (nude body:1.6), full body, (large breasts:1.3), long silver hair, long legs, high heels, light smile,outdoors,{msg}' 
    #prompt_pos = msg

    prompt_neg= r'(worst quality, low quality:1.4), (fuze:1.4), (worst quality:1.1), (low quality:1.4:1.1), lowres, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark, username, blurrypolar,bad body,bad proportions,gross proportions,text,error,missing fingers, missing arms,missing legs, extra digit, extra fingers,fewer digits,extra limbs,extra arms,extra legs,malformed limbs,fused fingers,too many fingers,long neck,cross-eyed,mutated hands, cropped,poorly drawn hands,poorly drawn face,mutation,deformed,worst quality,low quality, normal quality, blurry,ugly,duplicate,morbid,mutilated,out of frame, body out of frame,'
    K = message.reply_text("Please Wait 1-2 Minutes")

    print(prompt_pos)
    result1 = api.txt2img(prompt=prompt_pos, negative_prompt=prompt_neg, width=512, height=768, batch_size=2, denoising_strength=0.45, enable_hr=True, hr_second_pass_steps=10, hr_scale=1.5, restore_faces=True, steps=15, seed=-1)
    #result1 = api.txt2img(prompt=prompt_pos)

    for i in result1.images:
        #image = byteBufferOfImage(i, 'JPEG')
        image = saveImage(i, fileName(name))
        #client.send_photo(chat_id=message.chat.id, photo=image, caption=f"Prompt - **{msg}**\n **[{message.from_user.first_name}](tg://user?id={message.from_user.id})**\n Join @aipicfree")
        message.reply_photo(photo=image, caption= f"Prompt - **{name}**\n Join @aipicfree")
        os.remove(image)
    K.delete()

    
def button_callback(bot, update, message, button):
    message.edit_text(text=f'Format: /draw {button.callback_data}')
    return True

@app.on_callback_query()
def handle_callback(client, callback_query):
    msg = callback_query.data
    # 获取原始消息对象
    message = callback_query.message
    txt2Image(msg, client, message)

buttons1 = [
    InlineKeyboardButton("Default", callback_data="solo"),
    InlineKeyboardButton("佟丽娅", callback_data="<lora:Liliya_v10:0.7>"),
    InlineKeyboardButton("高启兰", callback_data="rimless eyewear, <lora:gaoqilan_v20:0.8>"),
    InlineKeyboardButton("刘亦菲", callback_data="<lora:liuyifei_10:0.8>"),
    InlineKeyboardButton("万茜", callback_data="<lora:wanqian_shorthair_v01:0.8>"),
]
buttons2 = [
    InlineKeyboardButton("赵丽颖", callback_data="<lora:zhaoliying:0.8>"),
    InlineKeyboardButton("鞠婧祎", callback_data="<lora:jJNgy_jJNgy:0.8>"),
    InlineKeyboardButton("杨幂", callback_data="<lora:mimi_V3:0.8>"),
    InlineKeyboardButton("宋祖儿", callback_data="<lora:songzuer-000018:0.8>"),
    InlineKeyboardButton("娜扎", callback_data=" <lora:guninazha:0.8>"),
]
buttons3 = [
]


keyboard = InlineKeyboardMarkup([buttons1, buttons2])

@app.on_message(filters.command(["draw"]))
def draw(client, message):
    message.reply_text("Please choose a prompt:", reply_markup=keyboard)

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

#prompt_negative = r'(worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, backlight,(ugly:1.331), (duplicate:1.331), (morbid:1.21), (mutilated:1.21), (tranny:1.331), deformed eyes, deformed lips, mutated hands, (poorly drawn hands:1.331), blurry, (bad anatomy:1.21), (bad proportions:1.331), three arms, extra limbs, extra legs, extra arms, extra hands, (more than 2 nipples:1.331), (missing arms:1.331), (extra legs:1.331), (fused fingers:1.61051), (too many fingers:1.61051), (unclear eyes:1.331), bad hands, missing fingers, extra digit, (futa:1.1), bad body, pubic hair, glans, easynegative, three feet, four feet, (bra:1.3)'
prompt_negative = r'(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, (ugly:1.331), (duplicate:1.331), (morbid:1.21), (mutilated:1.21), (tranny:1.331), deformed eyes, deformed lips, mutated hands, (poorly drawn hands:1.331), blurry, (bad anatomy:1.21), (bad proportions:1.331), three arms, extra limbs, extra legs, extra arms, extra hands, (more than 2 nipples:1.331), (missing arms:1.331), (extra legs:1.331), (fused fingers:1.61051), (too many fingers:1.61051), (unclear eyes:1.331), bad hands, missing fingers, extra digit, (futa:1.1), bad body, pubic hair, glans, easynegative, three feet, four feet, (bra:1.3)'

def get_mask(photo, txt, color, alpha, precision):
    prompt_positive = f'[txt2mask mode="add" show precision={precision} padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0 sketch_color="{color}" sketch_alpha={alpha}]{txt}[/txt2mask]'
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.35, inpainting_fill=1)
    return result

def body_mask(photo):
    prompt_positive = r'[txt2mask mode="add" show precision=70.0 padding=8.0 smoothing=80.0 negative_mask="face" neg_precision=80.0 neg_padding=8.0 neg_smoothing=20.0]dress|skirt|shorts|shirt|pants[/txt2mask]'
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.0, inpainting_fill=1)
    for img_mask in result.images:
        if img_mask.mode == "RGBA":
            return img_mask
    return None

def get_dress_mask(photo):
    prompt_positive = r'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0 sketch_color="229,205,197" sketch_alpha=180.0]dress|shorts[/txt2mask] untied bikini,<lora:nudify:1>'
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.35, inpainting_fill=1)
    return result

def dress_api(photo, mask, strength, inp_fill):
    print(mask)
    print(f'strength={strength}, inp_fill={inp_fill}')
    if mask is not None:
        print("mask exist")
        #prompt_positive = r'(8k, RAW photo, best quality, masterpiece:1.2), (realistic, photo-realistic:1.37), best quality, , (KPOP:1),1girl,nsfw,(absolutely naked,large breast,nipples,pussy,pubic hair),slim waist,very short hair, smooth skin, topless, bottomless,(high nipples:1.4), <lora:nudify:1>'
        prompt_positive = r'(realistic, photo-realistic:1.37), large breasts, best quality, 1girl, topless, bottomless, nsfw, fully naked, short hair, pussy, smooth skin, <lora:nudify:1>'
    else:
        print("mask is none")
        prompt_positive = r'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0 sketch_color="247,200,166" sketch_alpha=50.0]dress[/txt2mask]best quality,(realistic),nsfw,1girl,solo,((large breasts)),nude,topless,cleavage,navel'
        prompt_positive = r'[txt2mask mode="add" precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0]dress[/txt2mask] [file color] dress'
        prompt_positive = r'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0]dress[/txt2mask] pink dress'
        prompt_positive = r'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0]dress[/txt2mask] best quality,(realistic),nsfw,1girl,solo,((large breasts)),nude,topless,cleavage,navel'
    print(prompt_positive)
    return api.img2img(images=[photo], prompt=prompt_positive,negative_prompt=prompt_negative, cfg_scale=7, batch_size=2, denoising_strength=strength, inpainting_fill=inp_fill, mask_image=mask)

@app.on_message(filters.photo)
#@app.on_message(filters.photo & filters.regex("dress"))
#@app.on_message(filters.command(["img2img"], prefixes="/") & filters.photo)
async def img2img(client, message):
    if message.photo:
        print("Message contains one photo.")
        photo_path = await client.download_media(message.photo.file_id)
        print(photo_path)
        with open(photo_path, "rb") as f:
            file_bytes = f.read()
        img_ori = Image.open(BytesIO(file_bytes))

        mask_body = body_mask(img_ori)
        result = get_dress_mask(img_ori)
        print("=============================mask===============================")
        for img_mask in result.images:
            if img_mask.mode == "RGBA":
                mask = img_mask
            await message.reply_photo(byteBufferOfImage(img_mask, 'PNG'))

        print(mask)
        img = result.image
        denoising_strength = 0.4
        inp_fill = 1
        for i in range(2):
            result = dress_api(img, mask, denoising_strength, inp_fill)
            #inp_fill = i % 2
            print(f"=============================result:{i}===============================")
            denoising_strength = 0.5
            for image in result.images:
                img = image
                await message.reply_photo(byteBufferOfImage(img, 'JPEG'))
                result_body = dress_api(img, mask_body, 0.4, 1)
                print("=============================result:last==============================")
                img = result_body.image
                await message.reply_photo(byteBufferOfImage(img, 'JPEG'))
    else:
        num_photos = len(message.photo)
        print(f"Message contains {num_photos} photos.")
        photo = message.photo[-1]
        file_bytes = client.download_media(photo.file_id)
        img = Image.open(BytesIO(file_bytes))
        img = dress_api(img)
        await message.reply_photo(img)


app.run()
