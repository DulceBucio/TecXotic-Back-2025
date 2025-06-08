import cv2
from flask import Response, Blueprint
from flask_cors import CORS
from Capture import Capture
from flask import request

camServer = Blueprint('camServer', __name__)
CORS(camServer)

cap1 = Capture()
# cap2 = Capture(1)

alphaPos = 60
betaPos = 60

@camServer.route('/alpha', methods=['POST'])
def setAlpha():
    global alphaPos
    data = request.get_json()
    if 'alpha' in data:
        alphaPos = int(data['alpha'])
        return {'status': 'success', 'alpha': alphaPos}
    else:
        return {'status': 'error', 'message': 'Alpha value not provided'}, 400

@camServer.route('/beta', methods=['POST'])
def setBeta():
    global betaPos
    data = request.get_json()
    if 'beta' in data:
        betaPos = int(data['beta'])
        return {'status': 'success', 'beta': betaPos}
    else:
        return {'status': 'error', 'message': 'Beta value not provided'}, 400

def brightnessAjustment(img):
    imgBrightness = cv2.convertScaleAbs(img, alpha=(alphaPos/100), beta=betaPos)
    return imgBrightness   

def generate(capture):
    while True:
        ret, frame = capture.get_frame()
        if ret:
            frame = brightnessAjustment(frame)
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')


@camServer.route("/video1")
def video1():
    return Response(generate(cap1),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


# @camServer.route("/video2")
# def video2():
#     return Response(generate(cap2),
#                     mimetype="multipart/x-mixed-replace; boundary=frame")

def release_video():
    # Releasing video
    #cap2.release()
    cap1.release()

# Returns screenshot for the measurements tasks
@camServer.route('/screenshot/<capture>', methods=['GET'])
def screenshot(capture):
    _, frame = cap1.get_frame()
    (flag, encodedImage) = cv2.imencode(".jpg", frame)
    return Response(
        encodedImage.tobytes(),
        status=200,
        mimetype='img/jpeg'
        )