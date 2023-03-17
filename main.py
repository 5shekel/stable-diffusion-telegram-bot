import json
import requests
import io
import os
import random
import base64
from PIL import Image, PngImagePlugin
from pyrogram import Client, filters
from pyrogram.types import *

# Done! Congratulations on your new bot. You will find it at 
# t.me/gootmornbot
# You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

# Use this token to access the HTTP API:
# Keep your token secure and store it safely, it can be used by anyone to control your bot.

# For a description of the Bot API, see this page: https://core.telegram.org/bots/api

API_ID = os.environ.get("API_ID", None) 
API_HASH = os.environ.get("API_HASH", None) 
TOKEN = os.environ.get("TOKEN", None) 
SD_URL = os.environ.get("SD_URL", None) 
print(SD_URL)

app = Client(
    "stable",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=TOKEN
)


@app.on_message(filters.command(["draw"]))
def draw(client, message):
    msgs = message.text.split(' ', 1)
    if len(msgs) == 1:
        message.reply_text("Format : /draw < text to image >")
        return
    msg = msgs[1]

    K = message.reply_text("Please Wait 10-15 Second")

    payload = {"prompt": msg}

    r = requests.post(url=f'{SD_URL}/sdapi/v1/txt2img', json=payload).json()

    # save the image to a file

    def genr(): # generate random string
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
        return f"{message.from_user.id}-MOE{gen1}{gen2}{gen3}{gen4}{gen5}{gen6}{gen7}{gen8}{gen9}{gen10}"
    
    word=genr()
    for i in r['images']:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

        png_payload = {"image": "data:image/png;base64," + i}
        response2 = requests.post(url=f'{SD_URL}/sdapi/v1/png-info',
                                  json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f'{word}.png', pnginfo=pnginfo)

        message.reply_photo(
            photo=f"{word}.png",
            caption=
            f"Prompt - **{msg}**\n **[{message.from_user.first_name}-Kun](tg://user?id={message.from_user.id})**"
        )
        os.remove(f"{word}.png")
        K.delete()


# get the models, choose one, and set it as the model checkpoint
@app.on_message(filters.command(["getmodels"]))
async def get_models(client, message):
    response = requests.get(url=f'{SD_URL}/sdapi/v1/sd-models')
    if response.status_code == 200:
        models_json = response.json()
        # create buttons for each model name
        buttons = []
        for model in models_json:
            buttons.append([InlineKeyboardButton(model['title'], callback_data=model['model_name'])])
        # send the message
        await message.reply_text(
            text="Select a model [checkpoint] to use",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

@app.on_callback_query()
async def process_callback(client, callback_query):
    # if a model button is clicked, set sd_model_checkpoint to the selected model's title
    sd_model_checkpoint = callback_query.data

    # The sd_model_checkpoint needs to be set to the title from /sdapi/v1/sd-models
    # post using /sdapi/v1/options

    options = {
        "sd_model_checkpoint": sd_model_checkpoint
    }

    # post the options
    response = requests.post(url=f'{SD_URL}/sdapi/v1/options', json=options)
    if response.status_code == 200:
        # if the post was successful, send a message
        await callback_query.message.reply_text("checpoint set to " + sd_model_checkpoint)
    else:
        # if the post was unsuccessful, send an error message
        await callback_query.message.reply_text("Error setting options")


# start the bot
@app.on_message(filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    # Photo = "https://i.imgur.com/79hHVX6.png"

    buttons = [[
        InlineKeyboardButton("Add to your group",
                             url="https://t.me/gootmornbot?startgroup=true")
    ]]
    await message.reply_text(

        # photo=Photo,
        text=
        f"Hello!\nask me to imagine anything\n\n/draw text to image",
        reply_markup=InlineKeyboardMarkup(buttons)
        )


app.run()
