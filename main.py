import json, os

from fastapi import FastAPI

app = FastAPI()

CONFIG_DEFAULTS = {
    'host': '127.0.0.1',
    'port': '8554',
    'width': '1280',
    'height': '800',
    'bitrate': '50000',
    'fps': '30'
}
CONFIGFILE = "config.cfg"


def load_config():
    with open(CONFIGFILE) as f:
        return json.load(f)


def save_config(config):
    with open(CONFIGFILE, 'w') as f:
        json.dump(config, f)
    return True


@app.on_event("startup")
async def startup_event():
    if not os.path.exists(CONFIGFILE):
        with open(CONFIGFILE, 'w') as f:
            json.dump(CONFIG_DEFAULTS, f)


@app.get("/get-fps")
def get_fps():
    config = load_config()
    return config['fps']


@app.get("/set-fps/{fps}")
def set_fps(fps: int):
    config = load_config()
    config['fps'] = fps
    save_config(config)
    return True

@app.get("/get-bitrate")
def get_bitrate():
    config = load_config()
    return config['bitrate']


@app.get("/set-bitrate/{bitrate}")
def set_bitrate(bitrate: int):
    config = load_config()
    config['bitrate'] = bitrate
    save_config(config)
    return True

@app.get("/get-resolution")
def get_resolution():
    config = load_config()
    return {
        'width': config['width'],
        'height': config['height'],
    }


@app.get("/set-resolution/{width}&{height}")
def set_resolution(width: int, height: int):
    config = load_config()
    config['width'] = width
    config['height'] = height
    save_config(config)
    return True

@app.get("/get-url")
def get_url():
    config = load_config()
    return config['host'] + ":" + config['port']
