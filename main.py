
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
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont



def init():
    # Parse Config.ini file
	parser = configparser.ConfigParser()
	parser.read('config.ini')
	
	global LED, token, org, bucket, url, path, pot_limit, channel, kernel_size, fill_size, cam, client, disp, WIDTH, HEIGHT, but_cal_prev,but_start_stop
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
	
	
	# Camera and LED init
	cam = Picamera2()
	gpio.setwarnings(False)
	gpio.setup(LED, gpio.OUT)
	gpio.output(LED,gpio.HIGH)
	
	#Button init
	but_cal_prev = 21
	but_start_stop = 16
	gpio.setup(but_cal_prev, gpio.IN, pull_up_down=gpio.PUD_UP)
	gpio.setup(but_start_stop, gpio.IN, pull_up_down=gpio.PUD_UP)


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
    disp.clear()
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
    
    disp.clear()
    # Initialize display.
    disp.begin()

    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    draw.text((0, 60), "Collecting data...", font=font, fill=(255, 255, 255))
    disp.display(img)
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
        path_img = photo("/home/pi/Desktop/phenostation/Assets", preview = True)
        show_image(disp, path_img, WIDTH, HEIGHT)
        time.sleep(2)
        
        if gpio.input(but_cal_prev) == False:
            show_menu()
            break
        
def show_menu():
    # Initialize display.
    disp.clear()
    # Initialize display.
    disp.begin()

    img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    #Title
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
    draw.text((4, 20), "PhenoHive", font=font, fill=(255, 255, 255))

    #Menu
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    draw.text((40, 60), "Menu", font=font, fill=(255, 255, 255))

    #Button
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 140), "<-- Preview     Start -->", font=font, fill=(255, 255, 255))

    disp.display(img)
    
    
def main():
    init()
    show_image(disp, "/home/pi/Desktop/phenostation/Assets/logo_phenohive.png", WIDTH, HEIGHT)
    time.sleep(3)
    show_menu()
    while True:
        #Choose Button
        if gpio.input(but_cal_prev) == False:
            plant_preview()
            time.sleep(5)
            
        if gpio.input(but_start_stop) == False:
            start_measuring()
            time.sleep(5)
        
    
        

if __name__ == "__main__":
    main()