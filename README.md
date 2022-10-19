### Setup
- pip install uvicorn
- pip install fastapi
### Start server locally
uvicorn main:app --reload
#### lan play no latency
gst-launch-1.0 rtspsrc location=rtsp://192.168.1.226:8554/test latency=0 drop-on-latency=true ! decodebin ! videoconvert ! autovideosink
