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
import numpy as np

import webuiapi

from scipy import stats

from dotenv import load_dotenv
load_dotenv()

API_ID = os.environ.get("API_ID", None) 
API_HASH = os.environ.get("API_HASH", None) 
TOKEN = os.environ.get("TOKEN", None) 
SD_URL = os.environ.get("SD_URL", None) 
USER_IDS = os.environ.get("USER_IDS", "*") 

app = Client(
    "stable",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)

user_ids = ser_ids = USER_IDS.split(',')

# create API client
api = webuiapi.WebUIApi()

# create API client with custom host, port
api = webuiapi.WebUIApi(host='0.0.0.0', port=7861, sampler='DPM++ SDE Karras', steps=10)

# create API client with custom host, port and https
#api = webuiapi.WebUIApi(host='webui.example.com', port=443, use_https=True)

# create API client with default sampler, steps.
#api = webuiapi.WebUIApi(sampler='Euler a', steps=20)

# optionally set username, password when --api-auth is set on webui.
#api.set_auth('username', 'password')

def get_skin_rgb(image, mask):
    mask = np.array(mask)
    image = np.array(image)

    skin_pixels = image[np.nonzero(mask)].reshape(-1,3)
    print("=====skin_pixels==========")
    print(skin_pixels)

    n_skin_pixels = skin_pixels.shape[0]
    print(f"=====skins:{n_skin_pixels}==========")
    if n_skin_pixels == 0:
        return "229,205,197"
    else:
        r = skin_pixels[:,0]
        print(r)
        g = skin_pixels[:,1]
        print(g)
        b = skin_pixels[:,2]
        print(b)

        final_r = stats.mode(r)[0][0]
        final_g = stats.mode(g)[0][0]
        final_b = stats.mode(b)[0][0]

        result = f'{final_r},{final_g},{final_b}'
        print(result)
        return result

def is_allowed(message) -> bool:
    if USER_IDS == '*':
        return True
    print(message.from_user.id)
    if str(message.from_user.id) in user_ids:
        print("allow!")
        return True
    print("not allow!")
    return False


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

@app.on_callback_query(filters.regex("GuoFeng|chill|Basil"))
def change_model(client, callback_query):
    msg = callback_query.data
    print(msg)

    # 获取原始消息对象
    message = callback_query.message
    K = message.reply_text("Please Wait 1-2 Minutes")

    # set model (find closest match)
    api.util_set_model(f'{msg}')

    # wait for job complete
    api.util_wait_for_ready()

    K.delete()

@app.on_callback_query(filters.regex("solo|lora"))
def handle_callback(client, callback_query):
    msg = callback_query.data
    # 获取原始消息对象
    message = callback_query.message
    print(msg)
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
    InlineKeyboardButton("刘诗诗", callback_data="<lora:lss_V1:0.8>"),
    InlineKeyboardButton("赵露诗", callback_data="<lora:rosyZhao_rosyZhao:0.8>"),
    InlineKeyboardButton("刘亦菲2", callback_data="<lora:crystalLiuLiYFI_crystalLiu:0.8>"),
    InlineKeyboardButton("刘亦菲3", callback_data="<lora:airyGirl_v10:0.8>"),
    InlineKeyboardButton("热巴", callback_data="<lora:dilrabaDilmurat_v1:0.8>"),
]


keyboard = InlineKeyboardMarkup([buttons1, buttons2, buttons3])

model_btns = [
    InlineKeyboardButton("GF2", callback_data="GuoFeng2"),
    InlineKeyboardButton("GF3.2", callback_data="GuoFeng3.2"),
    InlineKeyboardButton("chill", callback_data="chilloutmix_NiPrunedFp32Fix"),
    InlineKeyboardButton("Basil", callback_data="Basil_mix_fixed"),
]
models_board = InlineKeyboardMarkup([model_btns])

@app.on_message(filters.command(["draw"]))
def draw(client, message):
    if (not is_allowed(message)):
        message.reply_text("you are not allowed to use this bot! Please contact to @aipicfree")
        return
    message.reply_text("Please choose a prompt:", reply_markup=keyboard)

@app.on_message(filters.command(["model"]))
def model(client, message):
    if (not is_allowed(message)):
        message.reply_text("you are not allowed to use this bot! Please contact to @aipicfree")
        return
    # save current model name
    old_model = api.util_get_current_model()
    print(old_model)

    # get list of available models
    models = api.util_get_model_names()
    print(models)

    message.reply_text("Please choose a models:", reply_markup=models_board)

@app.on_message(filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    if (not is_allowed(message)):
        message.reply_text("you are not allowed to use this bot! Please contact to @aipicfree")
        return
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
        f"Hello! I'm botname Ai and I can make an anime-styled picture!\n\n/model - change model\n/draw text to anime image\n\nPowered by @aipicfree",
        reply_markup=InlineKeyboardMarkup(buttons))

#prompt_negative = r'(worst quality:2), (low quality:2), (normal quality:2), lowres, normal quality, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, age spot, backlight,(ugly:1.331), (duplicate:1.331), (morbid:1.21), (mutilated:1.21), (tranny:1.331), deformed eyes, deformed lips, mutated hands, (poorly drawn hands:1.331), blurry, (bad anatomy:1.21), (bad proportions:1.331), three arms, extra limbs, extra legs, extra arms, extra hands, (more than 2 nipples:1.331), (missing arms:1.331), (extra legs:1.331), (fused fingers:1.61051), (too many fingers:1.61051), (unclear eyes:1.331), bad hands, missing fingers, extra digit, (futa:1.1), bad body, pubic hair, glans, easynegative, three feet, four feet, (bra:1.3)'
prompt_negative = r'(worst quality:2), (low quality:2), (normal quality:2), lowres, ((monochrome)), ((grayscale)), skin spots, acnes, skin blemishes, tattoo, body painting, age spot, (ugly:1.331), (duplicate:1.331), (morbid:1.21), (mutilated:1.21), (tranny:1.331), deformed eyes, deformed lips, mutated hands, (poorly drawn hands:1.331), blurry, (bad anatomy:1.21), (bad proportions:1.331), three arms, extra limbs, extra legs, extra arms, extra hands, (more than 2 nipples:1.331), (missing arms:1.331), (extra legs:1.331), (fused fingers:1.61051), (too many fingers:1.61051), (unclear eyes:1.331), bad hands, missing fingers, extra digit, (futa:1.1), bad body, pubic hair, glans, easynegative, three feet, four feet, (bra:1.3)'

def see_through(photo, color):
    prompt_positive = f'[txt2mask mode="add" precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0 sketch_color="{color}" sketch_alpha=80.0]dress|bra|underwear[/txt2mask](8k, RAW photo, best quality, masterpiece:1.2), (realistic, photo-realistic:1.37), fmasterpiecel, 1girl, extremely delicate facial, perfect female figure, ({color} strapless dress:1.6), see-through,leotard, smooth fair skin, bare shoulders, bare arms, clavicle, large breasts, cleavage, slim waist, bare waist, bare legs, very short hair, an extremely delicate and beautiful, extremely detailed,intricate,'
    print(prompt_positive)
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.4, inpainting_fill=1)
    return result

def get_mask(photo, txt, color, alpha, precision, replace):
    prompt_positive = f'[txt2mask mode="add" show precision={precision} padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0 sketch_color="{color}" sketch_alpha={alpha}]{txt}[/txt2mask]see-through'
    print(prompt_positive)
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.35, inpainting_fill=1)
    return result

def skin_mask(photo):
    prompt_positive = r'[txt2mask mode="discard" show precision=100.0 padding=0.0 smoothing=20.0]skin|face[/txt2mask]'
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.0, inpainting_fill=1)
    for img_mask in result.images:
        if img_mask.mode == "RGBA":
            return img_mask
    return None

def body_mask(photo):
    prompt_positive = r'[txt2mask mode="add" show precision=65.0 padding=0.0 smoothing=20.0 negative_mask="face" neg_precision=80.0 neg_padding=0.0 neg_smoothing=20.0]dress|skirt|shorts|shirt|pants|underwear|bra[/txt2mask]'
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.0, inpainting_fill=1)
    for img_mask in result.images:
        if img_mask.mode == "RGBA":
            return img_mask
    return None

def get_dress_mask(photo, color):
    prompt_positive = f'[txt2mask mode="add" show precision=100.0 padding=0.0 smoothing=20.0 negative_mask="face|hands|bare legs" neg_precision=100.0 neg_padding=-6.0 neg_smoothing=20.0 sketch_color="{color}" sketch_alpha=200.0]dress|skirts|pants|underwear|bra[/txt2mask] untied bikini,<lora:nudify:1>'
    result = api.img2img(images=[photo], prompt=prompt_positive, negative_prompt=prompt_negative, cfg_scale=7, batch_size=1, denoising_strength=0.35, inpainting_fill=1)
    return result

def dress_api(photo, mask, strength, inp_fill, count):
    print(mask)
    print(f'strength={strength}, inp_fill={inp_fill}')
    if mask is not None:
        print("mask exist")
        prompt_positive = r'(8k, RAW photo, best quality, masterpiece:1.2), (realistic, photo-realistic:1.37), (perfect female figure:1.4), silm waist, (nude:1.4) 1girl, nsfw,(smooth shin skin:1.3), (large breast, high nipples:1.4), pussy,very short hair, topless, bottomless, <lora:nudify:1>'
        #prompt_positive = r'(realistic, photo-realistic:1.37), absolutely naked, full nude, large breasts, slim waist, best quality, 1girl, topless, bottomless, nsfw, (very short hair:1.2), smooth shin skin, <lora:nudify:1>'
    else:
        print("mask is none")
        prompt_positive = r'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0 sketch_color="247,200,166" sketch_alpha=50.0]dress[/txt2mask]best quality,(realistic),nsfw,1girl,solo,((large breasts)),nude,topless,cleavage,navel'
        prompt_positive = r'[txt2mask mode="add" precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0]dress[/txt2mask] [file color] dress'
        prompt_positive = r'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0]dress[/txt2mask] pink dress'
        prompt_positive = r'[txt2mask mode="add" show precision=100.0 padding=4.0 smoothing=20.0 negative_mask="face|arms|hands" neg_precision=100.0 neg_padding=4.0 neg_smoothing=20.0]dress[/txt2mask] best quality,(realistic),nsfw,1girl,solo,((large breasts)),nude,topless,cleavage,navel'
    print(prompt_positive)
    return api.img2img(images=[photo], prompt=prompt_positive,negative_prompt=prompt_negative, cfg_scale=7, batch_size=count, denoising_strength=strength, inpainting_fill=inp_fill, mask_image=mask, steps=15)

@app.on_message(filters.photo)
#@app.on_message(filters.photo & filters.regex("dress"))
#@app.on_message(filters.command(["img2img"], prefixes="/") & filters.photo)
async def img2img(client, message):
    if (not is_allowed(message)):
        message.reply_text("you are not allowed to use this bot! Please contact to @aipicfree")
        return
    if message.photo:
        print("Message contains one photo.")
        photo_path = await client.download_media(message.photo.file_id)
        print(photo_path)
        with open(photo_path, "rb") as f:
            file_bytes = f.read()
        img_ori = Image.open(BytesIO(file_bytes))

        #get skin rgb
        mask_skin = skin_mask(img_ori).convert('RGB')
        await message.reply_photo(byteBufferOfImage(mask_skin, 'JPEG'))
        rgb_values = get_skin_rgb(img_ori, mask_skin)
        print(rgb_values)

        mask_body = body_mask(img_ori)

        #result = see_through(img_ori, "229,205,197")
        result = see_through(img_ori, rgb_values)
        print("=============================see===============================")
        await message.reply_photo(byteBufferOfImage(result.image, 'JPEG'))
        img_ori = result.image

        result = get_dress_mask(img_ori, rgb_values)
        print("=============================mask===============================")
        for img_mask in result.images:
            if img_mask.mode == "RGBA":
                mask = img_mask
            await message.reply_photo(byteBufferOfImage(img_mask, 'PNG'))

        print(mask)
        img = result.image
        denoising_strength = 0.4
        inp_fill = 1
        for i in range(1):
            result = dress_api(img, mask, denoising_strength, inp_fill, 1)
            print(f"=============================result:{i}===============================")
            for image in result.images:
                img = image # img as the next range
                #output fill in origin
                await message.reply_photo(byteBufferOfImage(image, 'JPEG')) 

                #output body mask, fill in  origin
                result_body = dress_api(image, mask_body, 0.45, 1, 3)
                await message.reply_photo(byteBufferOfImage(result_body.image, 'JPEG'))
                await message.reply_photo(byteBufferOfImage(result_body.images[1], 'JPEG'))
                await message.reply_photo(byteBufferOfImage(result_body.images[2], 'JPEG'))

                #img = result_body.image

            denoising_strength += 0.1
    else:
        num_photos = len(message.photo)
        print(f"Message contains {num_photos} photos.")
        photo = message.photo[-1]
        file_bytes = client.download_media(photo.file_id)
        img = Image.open(BytesIO(file_bytes))
        img = dress_api(img)
        await message.reply_photo(img)


app.run()
