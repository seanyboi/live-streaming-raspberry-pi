# import the necessary packages
from imutils import build_montages
from datetime import datetime
import numpy as np
from imagezmq import imagezmq
import argparse
import imutils
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-p", "--prototxt", required=True,
	help="path to Caffe 'deploy' prototxt file")
ap.add_argument("-m", "--model", required=True,
		help="path to Caffe pre-trained model")
ap.add_argument("-c", "--confidence", type=float, default=0.2,
		help="minimum probability to filter weak detections")
ap.add_argument("-mW", "--montageW", required=True, type=int,
		help="montage frame width")
ap.add_argument("-mH", "--montageH", required=True, type=int,
		help="montage frame height")
args = vars(ap.parse_args())

# initialise the ImageHub object
imageHub = imagezmq.ImageHub() # accepts connections from Raspberry Pi

# initialise the list of class labels MobileNet SSD was trained to detect, 
# then generate a set of bounding box colors for each class
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
	"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
	"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
	"sofa", "train", "tvmonitor"]

# load our serialised model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(args["prototxt"], args["model"])

# initialise the consider set (class labels we care about and want to count)
CONSIDER = set(["dog", "person", "cat"])
objCount = {obj: 0 for obj in CONSIDER}
frameDict = {}

# initialise the dictionary which will contain info regarding when device was
# last active, store last time to check 
lastActiv = {}
lastActiveCheck = datetime.now()

# stores the estimated number of Pis, active checking period, and 
# calculates duration seconds to wait before making a check to see if active
ESTIMATED_NUM_PIS = 1
ACTIVE_CHECK_PERIOD = 10
ACTIVE_CHECK_SECONDS = ESTIMATED_NUM_PIS * ACTIVE_CHECK_PERIOD

# assign the montage width and height so we can view all incoming frames
mW = args["montageW"]
mH = args["montageH"]
print("[INFO] detecting: {}...".format(", ".join(obj for obj in
	CONSIDER)))

# start looping over all frames
while True:
	# recieve RPi name and frame from the RPi and acknowledge the reciept
	(rpiName, frame) = imageHub.recv_image()
	imageHub.send_reply(b'OK')

	# if a device is not in the last active ditionary then it means
	# that its a newly connected device
	if rpiName not in lastActive.keys():
		print("[INFO] recieving data from {}...".format(rpiName))

	# record last active time for the device from which we just recieved a frame
	lastActive[rpiName] = datetime.now()

	# resize the frame to have a maximum width of 400 px, then
	# grab the frame dimensions and construct a blob
	frame = imutils.resize(frame, width=400)
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300,300), 127.5)

	# pass the blob through network and obtain detections and predictions
	net.setInput(blob)
	detections = net.forward()

	# reset the object count for each object in CONSIDER set
	objCount = {obj: 0 for obj in CONSIDER}

	# loop over the detections
	for i in np.arange(0, detections.shape[2]):
		# extract the confidence associated with the predictions
		confidence = detections[0,0,i,2]

		# filter out weak detections by ensuring confidence is 
		# greater than the minimum confidence
		if confidence > args["confidence"]:
			# extract the index of the class label from the detections
			idx = int(detections[0,0,i,1])

			# check to see if the predicted class is in the set of 
			# classes that need to be considered
			if CLASSES[idx] in CONSIDER:
				# increment the count of the object detected in frame
				objCount[CLASSES[idx]] += 1

				# computer the (x, y) coordinates of the bounding box for the obj
				box = detections[0,0,i,3:7] * np.array([w, h, w, h])
				(startX, startY, endX, endY) = box.astype("int")

				# draw bounding box around detected object
				cv2.rectangle(frame, (startX, startY), (endX, endY), (255,0,0), 2)

	# draw the sending device name on the frame
	cv2.putText(frame, rpiName, (10, 25), 
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 22), 2)

	# draw object count on the frame 
	label - ", ".join("{}: {}".format(obj, count) for (obj, count) in
		objCount.items())
	cv2.putText(frame, label, (10, h - 20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

	# update the new frame in the frame dictionary
	frameDict[rpiName] = frame

	# build the montage using images in the frame dictionary
	montages = build_montages(frameDict.values(), (w, h), (mW, mH))

	# display monatges on screen
	for (i, montage) in enumerate(montages):
		cv2.imshow("Home detector ({})".format(i), montage)

	# detect any keypressed
	key = cv2.waitKey(1) & 0xFF

	# if current time *minus* last time when active device check
	# was made is greater than the threshold set then do a check
	if (datetime.now() - lastActiveCheck).seconds > ACTIVE_CHECK_SECONDS:
		# loop over all previous active devices
		for (rpiName, ts) in list(lastActive.items()):
			# remove the rpi from last active and frame
			# dictionaries if the device hasn't been active recently
			if (datetime.now() - ts).seconds > ACTIVE_CHECK_SECONDS:
				print("[INFO] lost connection to {}".format(rpiName))
				lastActive.pop(rpiName)
				frameDict.pop(rpiName)

		# set the last active check time as current time
		lastActiveCheck = datetime.now()

	# if the q key was pressed, break from the loop
	if key == ord("p"):
		break

# do a bit of cleanup
cv2.destroyAllWindows() 

