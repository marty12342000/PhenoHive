
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import ST7735 as TFT
import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI



def show_image(disp, WIDTH, HEIGHT, path_img):
    image = Image.open(path_img)
    image = image.rotate(0).resize((WIDTH, HEIGHT))
    disp.display(image)


def show_logo(disp, WIDTH, HEIGHT):
    logo = Image.open("/home/pi/Desktop/phenostation/assets/logo_phenohive.jpg")
    logo = logo.rotate(0).resize((128, 70))
    return logo


def show_measuring_menu(disp, WIDTH, HEIGHT):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 80), "Collecting data...", font=font, fill=(0, 0, 0))
    logo = show_logo(disp, WIDTH, HEIGHT)
    img.paste(logo, (0, 0))
    disp.display(img)



def show_menu(disp, WIDTH, HEIGHT):
    # Initialize display.    
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    #Menu
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
    draw.text((40, 80), "Menu", font=font, fill=(0, 0, 0))
    #Button
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 130), "<-- Config        Start -->", font=font, fill=(0, 0, 0))
    logo = show_logo(disp, WIDTH, HEIGHT)
    img.paste(logo, (0, 0))
    disp.display(img)



def show_cal_prev_menu(disp, WIDTH, HEIGHT):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    #Menu
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
    draw.text((13, 80), "Configuration", font=font, fill=(0, 0, 0))
    #Button
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 130), "<-- Calib           Prev -->", font=font, fill=(0, 0, 0))
    logo = show_logo(disp, WIDTH, HEIGHT)
    img.paste(logo, (0, 0))
    disp.display(img)


def show_cal_menu(disp, WIDTH, HEIGHT, raw_weight, tare):
    img = Image.new('RGB', (WIDTH, HEIGHT), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    #Menu
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 80), "Tare :" +  str(tare), font=font, fill=(0, 0, 0))
    draw.text((0, 95), "Raw val :" +  str(raw_weight), font=font, fill=(0, 0, 0))
    #Button
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 10)
    draw.text((0, 130), "<-- Measure    Back -->", font=font, fill=(0, 0, 0))
    logo = show_logo(disp, WIDTH, HEIGHT)
    img.paste(logo, (0, 0))
    disp.display(img)