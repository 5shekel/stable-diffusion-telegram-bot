import json
import requests
import io
import os
import uuid
import base64
from PIL import Image, PngImagePlugin
from pyrogram import Client, filters
from pyrogram.types import *
from dotenv import load_dotenv

# Done! Congratulations on your new bot. You will find it at
# t.me/gootmornbot
# You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

# Use this token to access the HTTP API:
# Keep your token secure and store it safely, it can be used by anyone to control your bot.

# For a description of the Bot API, see this page: https://core.telegram.org/bots/api

load_dotenv()
API_ID = os.environ.get("API_ID", None)
API_HASH = os.environ.get("API_HASH", None)
TOKEN = os.environ.get("TOKEN", None)
SD_URL = os.environ.get("SD_URL", None)
print(SD_URL)
app = Client("stable", api_id=API_ID, api_hash=API_HASH, bot_token=TOKEN)

#default params
steps_value_default = 40

def process_input_string(string):
    ng_delimiter = "ng:"
    steps_delimiter = "steps:"
    
    ng_index = string.find(ng_delimiter)
    steps_index = string.find(steps_delimiter)
    
    if ng_index != -1 and steps_index != -1:
        if ng_index < steps_index:
            positive = string[:ng_index].strip()
            negative = string[ng_index + len(ng_delimiter):steps_index].strip()
            steps_str = string[steps_index + len(steps_delimiter):].strip().split()[0]
        else:
            positive = string[:steps_index].strip()
            negative = string[steps_index + len(steps_delimiter):ng_index].strip()
            steps_str = string[ng_index + len(ng_delimiter):].strip().split()[0]
    elif ng_index != -1:
        positive = string[:ng_index].strip()
        negative = string[ng_index + len(ng_delimiter):].strip()
        steps_str = None
    elif steps_index != -1:
        positive = string[:steps_index].strip()
        negative = None
        steps_str = string[steps_index + len(steps_delimiter):].strip().split()[0]
    else:
        positive = string.strip()
        negative = None
        steps_str = None

    try:
        steps_value = int(steps_str)
        #limit steps to range
        if not 1 <= steps_value <= 70:
            steps_value = steps_value_default
    except (ValueError, TypeError):
        steps_value = None
    

    return positive, negative, steps_value

@app.on_message(filters.command(["draw"]))
def draw(client, message):
    msgs = message.text.split(" ", 1)
    if len(msgs) == 1:
        message.reply_text(
            "Format :\n/draw < text to image >\nng: < negative (optional) >\nsteps: < steps value (1-70, optional) >"
        )
        return

    positive, negative, steps_value = process_input_string(msgs[1])
    payload = {
        "prompt": positive,
    }
    if negative is not None:
        payload["negative_prompt"] = negative
    if steps_value is not None:
        payload["steps"] = steps_value

    print(payload)

    # The rest of the draw function remains unchanged


    K = message.reply_text("Please Wait 10-15 Second")
    r = requests.post(url=f"{SD_URL}/sdapi/v1/txt2img", json=payload).json()

    def genr():
        unique_id = str(uuid.uuid4())[:7]
        return f"{message.from_user.first_name}-{unique_id}"

    word = genr()

    for i in r["images"]:
        image = Image.open(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))

        png_payload = {"image": "data:image/png;base64," + i}
        response2 = requests.post(url=f"{SD_URL}/sdapi/v1/png-info", json=png_payload)

        pnginfo = PngImagePlugin.PngInfo()
        pnginfo.add_text("parameters", response2.json().get("info"))
        image.save(f"{word}.png", pnginfo=pnginfo)

        message.reply_photo(
        photo=f"{word}.png",
        caption=(
            f"Prompt - **{positive}**\n"
            f"Negative Prompt - **{negative if negative is not None else 'None'}**\n"
            f"Steps - **{steps_value if steps_value != steps_value_default else 'Default'}**\n"
            f"**[{message.from_user.first_name}-Kun](tg://user?id={message.from_user.id})**"
        ),
)

        # os.remove(f"{word}.png")
        K.delete()


@app.on_message(filters.command(["getmodels"]))
async def get_models(client, message):
    response = requests.get(url=f"{SD_URL}/sdapi/v1/sd-models")
    if response.status_code == 200:
        models_json = response.json()
        # create buttons for each model name
        buttons = []
        for model in models_json:
            buttons.append(
                [
                    InlineKeyboardButton(
                        model["title"], callback_data=model["model_name"]
                    )
                ]
            )
        # send the message
        await message.reply_text(
            text="Select a model [checkpoint] to use",
            reply_markup=InlineKeyboardMarkup(buttons),
        )


@app.on_callback_query()
async def process_callback(client, callback_query):
    # if a model button is clicked, set sd_model_checkpoint to the selected model's title
    sd_model_checkpoint = callback_query.data

    # The sd_model_checkpoint needs to be set to the title from /sdapi/v1/sd-models
    # post using /sdapi/v1/options

    options = {"sd_model_checkpoint": sd_model_checkpoint}

    # post the options
    response = requests.post(url=f"{SD_URL}/sdapi/v1/options", json=options)
    if response.status_code == 200:
        # if the post was successful, send a message
        await callback_query.message.reply_text(
            "checpoint set to " + sd_model_checkpoint
        )
    else:
        # if the post was unsuccessful, send an error message
        await callback_query.message.reply_text("Error setting options")


@app.on_message(filters.command(["start"], prefixes=["/", "!"]))
async def start(client, message):
    # Photo = "https://i.imgur.com/79hHVX6.png"

    buttons = [
        [
            InlineKeyboardButton(
                "Add to your group", url="https://t.me/gootmornbot?startgroup=true"
            )
        ]
    ]
    await message.reply_text(
        # photo=Photo,
        text=f"Hello!\nask me to imagine anything\n\n/draw text to image",
        reply_markup=InlineKeyboardMarkup(buttons),
    )


app.run()
