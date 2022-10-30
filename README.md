# YoloV5 Object Detection using a Flask backend

This is a simple example of using the Yolov5 pre-trained object detection model to 
do near real-time objet detection of scenery. I was originally using this in conjunction 
with a DJI Tello drone to do object inference from frames captured by the drone camera 
and figured it would make a good project in its own right to help someone get started
with object detection using a pre-trained model. 

The project makes use of the following technologies
- Yolov5 Object Detection Model
- Flask
- WebSockets

You can see a YouTube clip of the finished product here: 
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/6fK5lKfih3A/0.jpg)](https://www.youtube.com/watch?v=6fK5lKfih3A)

But this repository is concerned only with running the server to do the real-time inference. 

## Install

    Build the container from the provided `Dockerfile`.

## Run the app

    `docker run -it -p 5000:5000 <image id>`


# Endpoints

## Inference
Use this endpoint to pass Base64 image data to, for object detection. Will return an array
of inference results including object type and confidence. (For a full list of objects recognised
by the pre-trained model, check the YoloV5 documentation) 

`Url`

| Method | Url | 
| - | :- |
| POST | http://127.0.0.1:5000/infer | 

`Body`

```json
{"binary":"<Base64 string>"}
```

`Response`

```json
[
   {
      "xmin":537.3125610352,
      "ymin":259.6194152832,
      "xmax":770.5920410156,
      "ymax":1080.0832519531,
      "confidence":0.9210409522,
      "class":0,
      "name":"person"
   },
   {
      "xmin":905.0319824219,
      "ymin":308.224029541,
      "xmax":1203.6735839844,
      "ymax":1057.7418212891,
      "confidence":0.904270649,
      "class":0,
      "name":"sports ball"
   }
]
```

Note, any time you post image data to the server for inference, you should also see a response 
in the server output, including the objects detected, speed of inference etc. Example: 

`
-> request received
image 1/1: 1118x1692 3 persons, 1 car, 1 umbrella, 1 sports ball
Speed: 14.7ms pre-process, 185.5ms inference, 1.9ms NMS per image at shape (1, 3, 448, 640)
`

## Viewer
Navigate to this endpoint in your browser for a simple page which shows the bounding boxes and
object detection results for the image(s) you pass to the inference endpoint. 

`Url`

| Method | Url | 
| - | :- |
| GET | http://127.0.0.1:5000/view | 

If you pass in video frame-by-frame, you will be able to see near real-time inference on the images. Here's a sample python functioN I was using from the Tello drone to pass an image to the infer endpoint

```python
def post_base64_image_to_api(image):
    url = "http://127.0.0.1:5000/infer"
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(image)
    response = requests.post(url, headers=headers, data=data)
    print(response)
```

## Healthcheck
Use this endpoint just to check the server is up and running. 

`Url`

| Method | Url | 
| - | :- |
| GET | http://127.0.0.1:5000 | 