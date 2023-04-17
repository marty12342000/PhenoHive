
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
from hx711 import HX711



def init():
    # Parse Config.ini file
    parser = configparser.ConfigParser()
    parser.read('config.ini')

    global LED, token, org, bucket, url, path, pot_limit, channel, kernel_size, fill_size, cam, client, disp, WIDTH, HEIGHT, but_left, but_right, hx, tare, raw_weight
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

    #Hx711 
    hx = HX711(dout_pin=5, pd_sck_pin=6)
    tare = sum(hx.get_raw_data())/5
    raw_weight = 0
        
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
    but_left = 21
    but_right = 16
    gpio.setup(but_left, gpio.IN, pull_up_down=gpio.PUD_UP)
    gpio.setup(but_right, gpio.IN, pull_up_down=gpio.PUD_UP)





def photo(path, preview = False, time_to_wait = 8):
    cam.start_preview(Preview.NULL)
    cam.start()
    time.sleep(time_to_wait)
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
    image = Image.open(path_img)
    image = image.rotate(0).resize((WIDTH, HEIGHT))
    disp.display(image)
    
    
def send_to_db(client, bucket, point, field, value): 
    write_api = client.write_api(write_options=SYNCHRONOUS)
    p = Point(point).field(field, int(value))
    write_api.write(bucket=bucket, record=p)


def show_logo():
    logo = Image.open("/home/pi/Desktop/phenostation/assets/logo_phenohive.jpg")
    logo = logo.rotate(0).resize((128, 70))
    return logo

def show_measuring_menu():
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 60), "Collecting data...", font=font, fill=(0, 0, 0))
    logo = show_logo()
    img.paste(logo, (0, 0))
    disp.display(img)

def start_measuring():
    
    show_measuring_menu()
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
        path_img = photo("/home/pi/Desktop/phenostation/assets", preview = True, time_to_wait=1)
        show_image(disp, path_img, WIDTH, HEIGHT)
        if gpio.input(but_right) == False:
            show_menu()
            break
        
def show_menu():
    # Initialize display.    
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    #Menu
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    draw.text((40, 80), "Menu", font=font, fill=(0, 0, 0))
    #Button
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 130), "<-- Config        Start -->", font=font, fill=(0, 0, 0))
    logo = show_logo()
    img.paste(logo, (0, 0))
    disp.display(img)


def show_cal_prev_menu():
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    #Menu
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    draw.text((13, 80), "Configuration", font=font, fill=(0, 0, 0))
    #Button
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 130), "<-- Calib           Prev -->", font=font, fill=(0, 0, 0))
    logo = show_logo()
    img.paste(logo, (0, 0))
    disp.display(img)


def show_cal_menu():
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    #Menu
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 80), "Tare :" +  str(tare), font=font, fill=(0, 0, 0))
    draw.text((0, 95), "Raw val :" +  str(raw_weight), font=font, fill=(0, 0, 0))
    #Button
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 130), "<-- Measure    Back -->", font=font, fill=(0, 0, 0))
    logo = show_logo()
    img.paste(logo, (0, 0))
    disp.display(img)



def get_weight():
    raw_weight = sum(hx.get_raw_data())/5
    return raw_weight
    


def weight_calibration():
    while True:
        show_cal_menu()
        if gpio.input(but_left) == False:
                global raw_weight
                raw_weight = get_weight()
        
        if gpio.input(but_right) == False:
                show_menu()
                break
    
    
def main():
    show_menu()
    while True:
        #Choose Button
        if gpio.input(but_left) == False:
            show_cal_prev_menu()
            time.sleep(1)
            while True:
                if gpio.input(but_left) == False:
                    weight_calibration()
                    time.sleep(1)
                    break

                if gpio.input(but_right) == False:
                    plant_preview()
                    time.sleep(1)
                    break
            
        if gpio.input(but_right) == False:
            start_measuring()

    
        

if __name__ == "__main__":
    init()
    disp.clear()
    disp.begin()
    show_image(disp, "/home/pi/Desktop/phenostation/assets/logo_elia.jpg", WIDTH, HEIGHT)
    main()