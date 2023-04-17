'''
Script python qui process les images prisent par la caméra pour évaluer la croissance des plantes
'''
import matplotlib.pyplot as plt
from plantcv import plantcv as pcv
import numpy as np
import datetime
import os
import cv2

def get_height_pix(image_path, pot_limit, channel='k', kernel_size=3, fill_size=1):
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    path = "/home/pi/Desktop/edges_img/edge%s.jpg"  % date
    print(path)
    pcv.params.debug = None
    
    img, path, filename = pcv.readimage(image_path)
    
    height, width = img.shape[0], img.shape[1]
    
    k = pcv.rgb2gray_cmyk(rgb_img=img, channel=channel)
    k_mblur = pcv.median_blur(k, kernel_size)
    
    edges = pcv.canny_edge_detect(k_mblur,sigma=2)
    edges_crop = pcv.crop(edges, 5, 5, height- pot_limit - 10, width - 10)
    new_height = edges_crop.shape[0]
    edges_filled = pcv.fill(edges_crop, fill_size)
    #pcv.print_image(edges_filled, path)
    non_zero = np.nonzero(edges_filled)
    #height = position of the last non-zero pixel
    plant_height_pix = new_height - min(non_zero[0])
    
    return plant_height_pix
