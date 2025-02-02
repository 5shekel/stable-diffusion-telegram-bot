# AI Powered Art in a Telegram Bot!

this is a txt2img bot to converse with SDweb bot [API](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API) running on tami telegram channel

# How to

supported invocation:  
`/draw <text>` - send prompt text to the bot and it will draw an image  
you can add `negative_prompt` using `ng: <text>`  
you can add `denoised intermediate steps` using `steps: <text>`  

basicly anything the `/controlnet/txt2img` API payload supports  
like, 
```json
{
  "prompt": "",
  "negative_prompt": "",
  "denoising_strength": 0.5,
  "seed": -1,
  "n_iter": 1,
  "steps": 20,
  "cfg_scale": 7
}
```
examples:  
`/draw a city street`  
and without people  
`/draw a city street ng: people`  
with more steps  
`/draw a city street ng: people steps: 50`  

to change the model use:  
`/getmodels` - to get a list of models and then click to set it. 



- note1: Anything after ng will be considered as nergative prompt. a.k.a things you do not want to see in your diffusion!  
- note2: on [negative_prompt](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Negative-prompt) (aka ng):  
thia is a bit of a black art. i took the recommended defaults for the `Deliberate` model from this fun [alt-model spreadsheet](https://docs.google.com/spreadsheets/d/1Q0bYKRfVOTUHQbUsIISCztpdZXzfo9kOoAy17Qhz3hI/edit#gid=797387129).  
~~and you (currntly) can only ADD to it, not replace.~~  
- note3: on `steps` - step of 1 will generate only the first "step" of bot hallucinations. the default is 40. higher will take longer and will give "better" image. range is hardcoded 1-70.  
see ![video](https://user-images.githubusercontent.com/57876960/212490617-f0444799-50e5-485e-bc5d-9c24a9146d38.mp4)
## Setup

Install requirements

```bash
conda create -n sdw python=3.8
conda activate sdw
pip install -r requirements.txt
```
(note: conda is not strictly necessary, but it is recommended)

## Original readme

My Bot uses [Automatic1111's WebUI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) as the backend.
Follow the directions on their repo for setup instructions.

Once you have WebUI set up, run `webui.sh` with the `--api` argument. You can also add other
arguments such as `--xformers` to use xformers memory efficient attention.

You can use the web ui interface that Automatic1111 provides to select the model and VAE to use.
Their repo has documentation on how to do so. I also recommend doing a test generation

Create a file called `.env` in the same folder as `main.py`. Inside the `.env` file,
create a line `TOKEN = xxxx`, where xxxx is your telegram bot token.
create a line `API_ID = xxxx`, where xxxx is your telegram id api id.
create a line `API_HASH = xxxx`, where xxxx is your telegram id api hash.
create a line `SD_URL = xxxx`, where xxxx is your sd api url.

Now, you can run the bot

`python main.py`



