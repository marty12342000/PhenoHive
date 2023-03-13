'''
Script python qui process les images prisent par la caméra pour évaluer la croissance des plantes
'''
import matplotlib.pyplot as plt
from plantcv import plantcv as pcv
import numpy as np
import os
import cv2

def get_height_pix(image_path, pot_limit, channel='k', kernel_size=3, fill_size=1):
    
    pcv.params.debug = "print"
    
    img, path, filename = pcv.readimage(image_path)
    
    height, width = img.shape[0], img.shape[1]
    
    k = pcv.rgb2gray_cmyk(rgb_img=img, channel=channel)
    k_mblur = pcv.median_blur(k, kernel_size)
    
    edges = pcv.canny_edge_detect(k_mblur,sigma=2)
    edges_crop = pcv.crop(edges, pot_limit,5,height-10,width-pot_limit-10)
    edges_filled = pcv.fill(edges_crop, fill_size)
    #pcv.plot_image(edges_filled)
    non_zero = np.nonzero(edges_filled)
    print(non_zero)
    #height = position of the last non-zero pixel
    plant_height_pix = max(non_zero[1])
    
    return plant_height_pix