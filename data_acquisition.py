
'''
Script python qui récupère les images et les mesures de poids et les envoies à la base de données influxDB
'''

import time
import datetime
import RPi.GPIO as GPIO
from picamera2 import Picamera2, Preview
from data_acquisition import get_height_pix
import configparser

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import ASYNCHRONOUS

def photo(path):
	cam.start_preview(Preview.NULL)
	cam.start()
	time.sleep(8)
	date = datetime.datetime.now()
    path_img = path + "/%s.jpg"  % date
	cam.capture_file(path)
	cam.stop_preview()
	cam.stop()

	return path_img




def main():
    # Parse Config.ini file
	parser = configparser.ConfigParser()
	parser.read(config.ini)

	led = int(parser["Pins"]["led"])

	token = str(parser["InfluxDB"]["token"])
	org = str(parser["InfluxDB"]["org"])
	bucket = str(parser["InfluxDB"]["bucket"])
	url = str(parser["InfluxDB"]["url"])

	path = str(parser["Path_to_save_img"]["absolute_path"])

    # Initialization of the camera and GPIO's
    GPIO.setmode(GPIO.BOARD)
	GPIO.setwarnings(False)
	LED = led
	GPIO.setup(LED, GPIO.OUT)
	GPIO.output(LED,GPIO.LOW)
	cam = Picamera2()
    
	# Initialization of the InfluxDB client
	client = InfluxDBClient(
    	url=url,
    	token=token,
    	org=org
	)
    

    while True:
		# Take photo
        GPIO.output(LED, GPIO.HIGH)
		path_img = photo(path)
		time.sleep(2)
		GPIO.output(LED,GPIO.LOW)

		# Get numerical value from the photo
		growth_value = get_height_pix(path_img, pot_lim=117)
	
		# Send data to the DB
		write_api = client.write_api(write_options=ASYNCHRONOUS)
		p = Point("my_measurement").field("Growth", float(data)).field("Growth_station_one", int(growth_value) )
        write_api.write(bucket=bucket, org=org, record=p)

		time.sleep(2)
        

if __name__ == "__main__":
    main()

