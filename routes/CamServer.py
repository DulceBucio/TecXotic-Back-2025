import cv2
from flask import Response, Blueprint
from flask_cors import CORS
from Capture import Capture
from flask import request
import numpy as np

camServer = Blueprint('camServer', __name__)
CORS(camServer)

cap1 = Capture()
# cap2 = Capture(1)

alpha = 60
beta = 60
alphaMeasure = 60
betaMeasure = 60
maxXDistance = 0

@camServer.route('/alpha', methods=['POST'])
def setAlpha():
    global alpha
    data = request.get_json()
    if 'alpha' in data:
        alpha = int(data['alpha'])
        return {'status': 'success', 'alpha': alpha}
    else:
        return {'status': 'error', 'message': 'alpha value not provided'}, 400

@camServer.route('/beta', methods=['POST'])
def setBeta():
    global beta
    data = request.get_json()
    if 'beta' in data:
        beta = int(data['beta'])
        return {'status': 'success', 'beta': beta}
    else:
        return {'status': 'error', 'message': 'Beta value not provided'}, 400
    

@camServer.route('/alpha/measurement', methods=['POST'])
def setAlphaMeasure():
    global alphaMeasure
    data = request.get_json()
    if 'alpha' in data:
        alphaMeasure = int(data['alpha'])
        return {'status': 'success', 'alpha': alphaMeasure}
    else:
        return {'status': 'error', 'message': 'alpha value not provided'}, 400

@camServer.route('/beta/measurement', methods=['POST'])
def setBetaMeasure():
    global betaMeasure
    data = request.get_json()
    if 'beta' in data:
        betaMeasure = int(data['beta'])
        return {'status': 'success', 'beta': betaMeasure}
    else:
        return {'status': 'error', 'message': 'Beta value not provided'}, 400

@camServer.route('/video1/measurement/result', methods=['GET'])
def getMaxXDistance():
    global maxXDistance
    return {'maxXDistance': str(maxXDistance)}

def brightnessAjustment(img):
    imgBrightness = cv2.convertScaleAbs(img, alpha=(alpha/100), beta=beta)
    return imgBrightness   

def brightnessAjustmentMeasure(img):
    imgBrightness = cv2.convertScaleAbs(img, alpha=(alphaMeasure/100), beta=betaMeasure)
    return imgBrightness   

def ignoreBlue(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([40, 50, 125])   
    upper_blue = np.array([130, 255, 255])
    
    mask = cv2.inRange(hsv, lower_blue, upper_blue)

    result = image.copy()
    result[mask > 0] = [0, 0, 0]
    return result

def measureItems(image):
    global maxXDistance
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(gray, 30, 200) 
    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    result = image.copy()
    cv2.drawContours(result, contours, -1, (0, 255, 0), 3)  # Draw green contours
    if contours:
        all_x = np.concatenate([cnt[:, :, 0] for cnt in contours])  # Collect all x-coordinates
        min_x, max_x = np.min(all_x), np.max(all_x)
        maxXDistance = max_x - min_x  
    return result
 

def generateOriginalVideo(capture):
    while True:
        ret, frame = capture.get_frame()
        if ret:
            frame = brightnessAjustment(frame)
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')

def generateProcessedVideo(capture):
    while True:
        ret, frame = capture.get_frame()
        if ret:
            frame = brightnessAjustmentMeasure(frame)
            frame = ignoreBlue(frame)
            frame = measureItems(frame)
            (flag, encodedImage) = cv2.imencode(".jpg", frame)
            if not flag:
                continue
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')

@camServer.route("/video1")
def video1():
    return Response(generateOriginalVideo(cap1),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

@camServer.route("/video1/measurement")
def video1_measurement():
    return Response(generateProcessedVideo(cap1),
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