# import necessary packages
from imutils.video import VideoStream
from imagezmq import imagezmq
import argparse
import socket
import time

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-s", "--server-ip", required=True, help="ip address")
args = vars(ap.parse_args())

# initialise the ImageSender object with the socket address of the 
# server
sender = imagezmq.ImageSender(connect_to="tcp://{}:5555".format(args["server_ip"]))

# get the host name, initialise the video, and allow the camera sensor to warmup
rpiName = socket.gethostname() # hostname is stored as rpiName
vs = VideoStream(usePiCamera=True).start() #  grabs frames  from camera, TODO: may need to reduce resolution
time.sleep(2.0)

while True:
	# read the frame from the camera and send it to the server
	frame = vs.read()
	sender.send_image(rpiName, frame)
