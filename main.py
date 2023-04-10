
'''
Script python qui récupère les images et les mesures de poids et les envoies à la base de données influxDB
'''

import time
import datetime
import RPi.GPIO as gpio
from picamera2 import Picamera2, Preview
from image_processing import get_height_pix
import configparser
from PIL import Image
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS




def init():
    # Parse Config.ini file
	parser = configparser.ConfigParser()
	parser.read('config.ini')
	
	global LED, token, org, bucket, url, path, pot_limit, channel, kernel_size, fill_size, cam, client, disp, WIDTH, HEIGHT
	LED = int(parser["Pins"]["led"])
    
	token = str(parser["InfluxDB"]["token"])
	org = str(parser["InfluxDB"]["org"])
	bucket = str(parser["InfluxDB"]["bucket"])
	url = str(parser["InfluxDB"]["url"])
	

	path = str(parser["Path_to_save_img"]["absolute_path"])

	pot_limit = int(parser["image_arg"]["pot_limit"])
	channel = str(parser["image_arg"]["channel"])
	kernel_size = int(parser["image_arg"]["kernel_size"])
	fill_size = int(parser["image_arg"]["fill_size"])
	
	# InfluxDB client initialization
	client = InfluxDBClient(url=url, token=token, org=org)
	
	# Screen initialization
	WIDTH = 128
	HEIGHT = 160
	SPEED_HZ = 4000000
	DC = 24
	RST = 25
	SPI_PORT = 0
	SPI_DEVICE = 0
	
	disp = TFT.ST7735(
        DC,
        rst=RST,
        spi=SPI.SpiDev(
            SPI_PORT,
            SPI_DEVICE,
            max_speed_hz=SPEED_HZ))
	
	
	# Camera and GPIO's initialization
	cam = Picamera2()
	gpio.setwarnings(False)
	gpio.setup(LED, gpio.OUT)
	gpio.output(LED,gpio.HIGH)


def photo(path, preview = False):
    cam.start_preview(Preview.NULL)
    cam.start()
    time.sleep(8)

    if preview == False:
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            
    else :
        date = "img"
            
            
    path_img = path + "/%s.jpg"  % date
    cam.capture_file(path_img)
    cam.stop_preview()
    cam.stop()

    return path_img


def show_image(disp, path_img, WIDTH, HEIGHT):
    # Initialize display.
    disp.begin()
    # Load an image.
    image = Image.open(path_img)
    # Resize the image and rotate it so matches the display.
    image = image.rotate(0).resize((WIDTH, HEIGHT))
    # Draw the image on the display hardware.
    print('Drawing image')
    disp.display(image)
    
    
def send_to_db(client, bucket, point, field, value): 
	write_api = client.write_api(write_options=SYNCHRONOUS)
	p = Point(point).field(field, int(value))
	write_api.write(bucket=bucket, record=p)



def start_measuring():

    while True:
        # Take photo
        gpio.output(LED, gpio.LOW)
        path_img = photo(path)
        time.sleep(2)
        gpio.output(LED,gpio.HIGH)
        # Get numerical value from the photo
        growth_value = get_height_pix(image_path=path_img, pot_limit=pot_limit, channel=channel, kernel_size=kernel_size, fill_size=fill_size)
        print(growth_value)
        # Send data to the DB
        send_to_db(client, bucket, "my_measurement", "Growth_station_test", growth_value)
        time.sleep(1190)


def plant_preview():
    while True:
        path_img = photo("/home/pi/Desktop/Assets", preview = True)
        show_image(disp, path_img, WIDTH, HEIGHT)
        time.sleep(2)
        

def main():
	init()
	show_image(disp, "/home/pi/Desktop/phenostation/Assets/logo_phenohive.png", WIDTH, HEIGHT)
	
	while True:
		start_measuring()
        
    
        

if __name__ == "__main__":
    main()
