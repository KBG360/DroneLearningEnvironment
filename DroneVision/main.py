import cv2
import numpy as np

# The camera to use
capture = cv2.VideoCapture(0)
# Width and height of the blob target
whT = 320
minConfidence = 0.5
nms_threshold = 0.3
# List which stores all the objects you can recognize
classesFile = 'coco.names'
classNames = []

with open(classesFile, 'rt') as f:
    classNames = f.read().rstrip('\n').split('\n')

modelConfiguration = 'yolov3-320.cfg'
modelWeights = 'yolov3.weights'

net = cv2.dnn.readNet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)


def findObject(outputsValue, imgValue):
    global classId
    hT, wT, cT = imgValue.shape
    bbox = []
    classIds = []
    confidence = []

    for output in outputsValue:
        for detection in output:
            scores = detection[5:]
            classId = np.argmax(scores)
            conf = scores[classId]
            if conf > minConfidence:
                w, h = int(detection[2] * wT), int(detection[3] * hT)
                x, y = int((detection[0] * wT) - w / 2), int((detection[1] * hT) - h / 2)
                bbox.append([x, y, w, h])
                classIds.append(classId)
                confidence.append(float(conf))
    print(len(bbox))
    indices = cv2.dnn.NMSBoxes(bbox, confidence, minConfidence, nms_threshold)
    for i in indices:
        i = i[0]
        box = bbox[i]
        x, y, w, h = box[0], box[1], box[2], box[3]
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 255), 2)
        cv2.putText(img, f'{classNames[classIds[i]].upper()} {int(confidence[i] * 100)}%', (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 1)


# Loop to show the camera feed
while True:
    success, img = capture.read()
    # The DNN requires blob types to read camera output
    blob = cv2.dnn.blobFromImage(img, 1 / 255, (whT, whT), [0, 0, 0], 1, crop=False)
    net.setInput(blob)

    layerNames = net.getLayerNames()
    outputNames = [layerNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]
    outputs = net.forward(outputNames)

    findObject(outputs, img)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
