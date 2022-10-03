from flask import Flask, request, render_template
from PIL import Image
import numpy as np
import torch 
import cv2
import base64
from flask_socketio import SocketIO, emit
import eventlet
from eventlet import wsgi
from io import BytesIO
import warnings
warnings.filterwarnings("ignore", message="torch.distributed.reduce_op is deprecated")

# cooperatively yield
eventlet.monkey_patch()

# load our pretrained model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True, trust_repo=True)  # force_reload = recache latest code
model.eval()

# initialize our Flask application and websockets
app = Flask(__name__)
app.config['SECRET_KEY']='1gqbt8mo7wwpm9aah53z44v4sqh89jz0rke24s'
socketio = SocketIO(app, async_mode='eventlet')
print('Flask starting up...')
print('[Inference endpoint] [post] http://127.0.0.1:5000/infer')
print('[View in browser] [get] http://127.0.0.1:5000/view')
print('[Health check] [get] http://127.0.0.1:5000')
# This is our viewing page
@app.route('/view')
def view():
    print("view")
    return render_template('view.html')

@socketio.on('connect')
def test_connect():
    emit('my response', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('image-upload')
def image_upload(image):
    emit('send-image', image)

# This is our inference endpoint. Send our base64 image here and we'll return the inference
@app.route('/infer', methods=['POST'])
def post():
    if request.method == 'POST':
        try:
            print("-> request received")
            encoded_data = request.get_json()
            base64_string = encoded_data['binary'].split(',')

            np_array = np.frombuffer(base64.b64decode(base64_string[1]), np.uint8)
            img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
            # Not clear why I needed to create a list for imgs when we're working with one at a time
            # but it wouldn't work without it
            imgs = []
            imgs.append(img)
            results = model(imgs, size=640)
            results.imgs = imgs
            print(results)
            results.render()
    
            buffered = BytesIO()
            img_base64 = Image.fromarray(results.imgs[0])
            img_base64.save(buffered, format="JPEG")
            # re-encode the image
            encoded_data['binary'] = "data:image/jpeg;base64," + base64.b64encode(buffered.getvalue()).decode('utf-8')
            socketio.emit('send-image',encoded_data)
            # respond with the results of the inference
            return results.pandas().xyxy[0].to_json(orient="records")
        except Exception as e:
            print(e)
            return "failed inference"

@app.route('/')
def index():
    return('<h1>Flask is running OK</h1>')


socketio.run(app, host='0.0.0.0', port=5000)
