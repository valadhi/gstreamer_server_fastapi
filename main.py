from threading import Thread
import json, os
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import GLib, Gst, GstRtspServer

from fastapi import FastAPI

app = FastAPI()
loop = GLib.MainLoop()

CONFIG_DEFAULTS = {
    'host': '127.0.0.1',
    'port': '8554',
    'mount': '/test',
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
    return config['host'] + ":" + config['port'] + config['mount']

@app.get("/start-stream")
def start_stream():

    Gst.init(None)
    config = load_config()
    server = GstRtspServer.RTSPServer()
    port = config['port']
    mount = config['mount']
    width = config['width']
    height = config['height']
    fps = config['fps']
    bitrate = config['bitrate']
    server.service = port
    mounts = server.get_mount_points()
    factory = GstRtspServer.RTSPMediaFactory()
    pipeline = ("v4l2src device=/dev/video0 io-mode=2  ! " +
                "image/jpeg,width={},height={},framerate={}/1 ! " +
                "nvjpegdec ! " +
                "video/x-raw ! " +
                "omxh264enc bitrate={} control-rate=constant ! " +
                "rtph264pay name=pay0 pt=96". format(width, height, fps, bitrate))
    factory.set_launch(pipeline)
    factory.set_shared(True)
    mounts.add_factory(mount, factory)
    server.attach()

    loop_thread = Thread(target=run_loop)
    loop_thread.start()
    return 'stream ready at rtsp://127.0.0.1:%s%s' % (port, mount)

def run_loop():
    global loop
    loop.run()

@app.get("/stop-stream")
def stop_stream():
    global loop
    loop.quit()
    return True
