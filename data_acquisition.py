import time
import datetime
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
LED = 16
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED,GPIO.LOW)

cam = Picamera2()
#Determine the date in the console with : sudo date -s "2022-12-05 21:25:00"

def photo():
	cam.start_preview(Preview.NULL)
	cam.start()
	date = datetime.datetime.now()
	cam.capture_file("/home/pi/Desktop/memoire/image/%s.jpg"  % date)
	cam.stop_preview()
	cam.stop()
while True:
	GPIO.output(LED, GPIO.HIGH)
	print("High")
	#photo()
	time.sleep(2)
	GPIO.output(LED,GPIO.LOW)
	print("Low")
	time.sleep(2)
