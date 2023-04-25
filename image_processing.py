'''
Script python qui process les images prisent par la caméra pour évaluer la croissance des plantes
'''
from plantcv import plantcv as pcv
import numpy as np
import datetime
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

def get_segment_list(image_path, channel='k', kernel_size=20):

    pcv.params.debug = None
    
    #read image
    img, path, filename = pcv.readimage(image_path)
    
    #get image dimension
    height, width = img.shape[0], img.shape[1]
    
    #extract channel (gray image)
    k = pcv.rgb2gray_cmyk(rgb_img=img, channel=channel)
    
    #perform canny edge detection
    edges = pcv.canny_edge_detect(k,sigma=2)
    
    #crop image edges
    edges_crop = pcv.crop(edges, 5, 5, height - 10, width - 10)
    
    
    #close gaps in plant contour
    kernel = np.ones((kernel_size,kernel_size), np.uint8) 
    closing = cv2.morphologyEx(edges_crop, cv2.MORPH_CLOSE, kernel)
    
    #find countours
    thresh = cv2.threshold(closing, 128, 255, cv2.THRESH_BINARY)[1]
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0]
    big_contour = max(contours, key=cv2.contourArea)
    
    #fill contour to get maize shape
    result = np.zeros_like(closing)
    cv2.drawContours(result, [big_contour], 0, (255,255,255), cv2.FILLED)
    
    #draw plant skeleton and segment
    pcv.params.line_thickness = 3
    skeleton = pcv.morphology.skeletonize(mask=result)
    segmented_img, obj = pcv.morphology.segment_skeleton(skel_img=skeleton)
    labeled_img = pcv.morphology.segment_path_length(segmented_img=segmented_img, 
                                                 objects=obj, label="default")
    #get segment lengths
    path_lengths = pcv.outputs.observations['default']['segment_path_length']['value']
    
    return path_lengths

def get_total_length(image_path, channel='k', kernel_size=20):
    
    segment_list = get_segment_list(image_path, channel,kernel_size)
    
    #get sum of segment lengths
    return sum(segment_list)