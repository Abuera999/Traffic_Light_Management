import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import cv2
import numpy as np
from io import BytesIO

app = Flask(__name__)
CORS(app) 

def detect_and_count_vehicles(image_path):
    net = cv2.dnn.readNet("yolov4.weights", "yolov4.cfg")

    classes = []
    with open("coco.names", "r") as f:
        classes = f.read().strip().split("\n")


    image = cv2.imread(image_path)
    height, width, _ = image.shape
    blob = cv2.dnn.blobFromImage(image, 1/255.0, (608, 608), swapRB=True, crop=False)
    net.setInput(blob)
    output_layers = net.getUnconnectedOutLayersNames()
    detections = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    for detection in detections:
        for obj in detection:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]

            if confidence > 0.6 and class_id == 2:  # Adjust threshold and class ID as needed
                center_x = int(obj[0] * width)
                center_y = int(obj[1] * height)
                w = int(obj[2] * width)
                h = int(obj[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indices = cv2.dnn.NMSBoxes(boxes, confidences, score_threshold=0.6, nms_threshold=0.3)

    vehicle_count = len(indices)

    for i in indices.flatten():
        box = boxes[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image, "Vehicle", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    result_image_path = "D:/JAIN UNIVERSITY/3rd Year/Semester 6/In House Project/Project/images/result.jpg"
    cv2.imwrite(result_image_path, image)

    return vehicle_count, result_image_path


@app.route('/get_result_image', methods=['GET'])
def get_result_image():
    result_image_path = request.args.get('result_image_path')
    return send_file(result_image_path, mimetype='image/jpeg')


@app.route('/detect_vehicles', methods=['POST'])
def detect_vehicles():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    upload_dir = "D:\\JAIN UNIVERSITY\\3rd Year\\Semester 6\\In House Project\\Project\\images"
    image_path = os.path.join(upload_dir, image_file.filename)
    image_file.save(image_path)

    vehicle_count, result_image_path = detect_and_count_vehicles(image_path)

    adjusted_green_time = max(15, min(60, vehicle_count * 2))
    
    response = {
        'vehicle_count': vehicle_count,
        'adjusted_green_time': adjusted_green_time,
        'result_image_path': result_image_path
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)