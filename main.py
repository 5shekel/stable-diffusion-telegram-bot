import json
import requests
import io
import re
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

# default params
steps_value_default = 40


def parse_input(input_string):
    default_payload = {
        "prompt": "",
        "negative_prompt": "",
        "controlnet_input_image": [],
        "controlnet_mask": [],
        "controlnet_module": "",
        "controlnet_model": "",
        "controlnet_weight": 1,
        "controlnet_resize_mode": "Scale to Fit (Inner Fit)",
        "controlnet_lowvram": False,
        "controlnet_processor_res": 64,
        "controlnet_threshold_a": 64,
        "controlnet_threshold_b": 64,
        "controlnet_guidance": 1,
        "controlnet_guessmode": True,
        "enable_hr": False,
        "denoising_strength": 0.5,
        "hr_scale": 1.5,
        "hr_upscale": "Latent",
        "seed": -1,
        "subseed": -1,
        "subseed_strength": -1,
        "sampler_index": "",
        "batch_size": 1,
        "n_iter": 1,
        "steps": 20,
        "cfg_scale": 7,
        "width": 512,
        "height": 512,
        "restore_faces": True,
        "override_settings": {},
        "override_settings_restore_afterwards": True,
    }
    # Initialize an empty payload with the 'prompt' key
    payload = {"prompt": ""}

    # Check if the input_string starts with "/draw "
    prompt = []

    # Find all occurrences of keys (words ending with a colon)
    matches = re.finditer(r"(\w+):", input_string)
    last_index = 0

    # Iterate over the found keys
    for match in matches:
        key = match.group(1)
        value_start_index = match.end()

        # If there's text between the last key and the current key, add it to the prompt
        if last_index != match.start():
            prompt.append(input_string[last_index : match.start()].strip())
        last_index = value_start_index

        # Check if the key is in the default payload
        if key in default_payload:
            # Extract the value for the current key
            value_end_index = re.search(
                r"(?=\s+\w+:|$)", input_string[value_start_index:]
            ).start()
            value = input_string[
                value_start_index : value_start_index + value_end_index
            ].strip()

            # Check if the default value for the key is an integer
            if isinstance(default_payload[key], int):
                # If the value is a valid integer, store it as an integer in the payload
                if value.isdigit():
                    payload[key] = int(value)
            else:
                # If the default value for the key is not an integer, store the value as is in the payload
                payload[key] = value

            last_index += value_end_index
        else:
            # If the key is not in the default payload, add it to the prompt
            prompt.append(f"{key}:")

    # Join the prompt words and store it in the payload
    payload["prompt"] = " ".join(prompt)

    # If the prompt is empty, return an empty dictionary
    if not payload["prompt"]:
        return {}

    # Return the final payload
    return payload


@app.on_message(filters.command(["draw"]))
def draw(client, message):
    msgs = message.text.split(" ", 1)
    if len(msgs) == 1:
        message.reply_text(
            "Format :\n/draw < text to image >\nng: < negative (optional) >\nsteps: < steps value (1-70, optional) >"
        )
        return

    payload = parse_input(msgs[1])
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

        info_dict = response2.json()
        seed_value = info_dict['info'].split(", Seed: ")[1].split(",")[0]
        # print(seed_value)

        caption = f"**[{message.from_user.first_name}-Kun](tg://user?id={message.from_user.id})**\n\n"
        for key, value in payload.items():
            caption += f"{key.capitalize()} - **{value}**\n"
        caption += f"Seed - **{seed_value}**\n"

        message.reply_photo(
            photo=f"{word}.png",
            caption=caption,
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
