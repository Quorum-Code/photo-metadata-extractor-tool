from PIL import *
import os
import sys
import datetime
import matplotlib.pyplot as plt
import numpy as np
import string
import multiprocessing
import math
import queue
import cv2
import tensorflow as tf
import imgaug
import skimage.exposure
from spellchecker import SpellChecker
import pandas as pd

import keras_ocr

import zipfile
import tqdm
import sklearn.model_selection

from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from PIL import Image
from tqdm.auto import tqdm
from urllib.request import urlretrieve
from zipfile import ZipFile
 
 

import torch
import glob
import scipy.misc

	
#device = torch.device('cuda:0' if torch.cuda.is_available else 'cpu')

device = 'cpu'
 
if not os.path.exists(asset_zip_path):
    download_and_unzip(URL, asset_zip_path)
	
def read_image(image_path):
    image = Image.open(image_path).convert('RGB')
    return image
	
def ocr(image, processor, model):
    
    pixel_values = processor(image, return_tensors='pt').pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text
	
def eval_new_data(img, processor, num_samples=4, model=None):
    #image_paths = glob.glob(data_path)
    #for i, image_path in tqdm(enumerate(image_paths), total=len(image_paths)):
    #    if i == num_samples:
    #        break
    #image = read_image(image_path)
    text = ocr(img, processor, model)
    #plt.figure(figsize=(7, 4))
    #plt.imshow(img)
    #plt.title(text)
    #plt.axis('off')
    #plt.show()
    return text



def distinguish_rows(lst, thresh=15): 
    sublists = []
    for i in range(0, len(lst)-1):
        if lst[i+1]['distance_y'] - lst[i]['distance_y'] <= thresh:
            if lst[i] not in sublists:
                sublists.append(lst[i])
            sublists.append(lst[i+1])
        else:
            yield sublists
            sublists = [lst[i+1]]
    yield sublists

def get_distance(preds):
    detections = []
    x0, y0 = 0, 0
    idx = 0
    for out in preds:
        for group in out:
            top_left_x, top_left_y = group[1][0]
            top_right_x, top_right_y = group[1][1]
            bottom_right_x, bottom_right_y = group[1][2]
            bottom_left_x, bottom_left_y = group[1][3]
            center_x = (top_left_x + bottom_right_x)/2
            center_y = (top_left_y + bottom_right_y)/2
            dist_from_origin = math.dist([x0,y0], [center_x, center_y])
            distance_y = center_y - y0
            height = math.sqrt( group[1][0][1]**2 + group[1][3][1]**2 ) 
            detections.append({
                'text': group[0],
                'center_x': center_x,
                'center_y': center_y,
                'top_left_x': top_left_x,
                'top_left_y': top_left_y,
                'top_right_x': top_right_x,
                'top_right_y': top_right_y,
                'bottom_left_x': bottom_left_x,
                'bottom_left_y': bottom_left_y,
                'bottom_right_x': bottom_right_x,
                'bottom_right_y': bottom_right_y,
                'dist_from_origin': dist_from_origin,
                'distance_y': distance_y,
                'height': height})
            idx = idx +1
    return detections

def get_train_val_test_split(arr):
    train, valtest = sklearn.model_selection.train_test_split(arr, train_size=0.8, random_state=42)
    val, test = sklearn.model_selection.train_test_split(valtest, train_size=0.5, random_state=42)
    return train, val, test    

def heightDiffCheck(currHeight, windowDict):
    for rec in windowDict.queue:
        if abs(currHeight - rec) > 400:
            return True
    return False

def write_dataframe(data, label):

    curr_time = datetime.datetime.now()

    init_datapath =  '.\\extracted_data\\'

    curr_time = curr_time.strftime('%Y-%m-%d %H-%M-%S')[:-3] + "_" + label + '_extracted_data.csv'

    datapath = init_datapath + curr_time

    os.makedirs(init_datapath, exist_ok=True)

    print(datapath)

    output_data = pd.DataFrame(columns=['Title', 'SuDoc', 'Publication Year'])

    output_data['SuDoc'] = data

    print(output_data)

    output_data.to_csv(datapath)

    return datapath
   
def img_recognition(img_list):

    data_dir = '.'
    alphabet = string.digits + string.ascii_letters + "./-(),#:"

    recognizer_alphabet = ''.join(sorted(set(alphabet.lower())))

    detector = keras_ocr.detection.Detector(weights='clovaai_general')
    recognizer = keras_ocr.recognition.Recognizer(
        alphabet=recognizer_alphabet
    )
    recognizer.compile()

    recognizer.model.load_weights('C:/Users/Karkaras/Desktop/curr_recognizer.h5')

    pipeline = keras_ocr.pipeline.Pipeline(detector=detector, recognizer=recognizer)

    print("Beginning Image Recognition")

    thresh = 15

    order='yes'

    processor = TrOCRProcessor.from_pretrained('microsoft/trocr-large-handwritten')
    model = VisionEncoderDecoderModel.from_pretrained(
        'microsoft/trocr-large-handwritten'
    ).to(device)

    text_strs = []

    ext_txt = ""

    for img in images_coll:
        pred = pipeline.recognize([img])

        pred = get_distance(pred)

        pred = list(distinguish_rows(pred, thresh))

        pred = list(filter(lambda x:x!=[], pred))

        for box in pred:

            uby = int(round(box[0]['top_left_y'])) if int(round(box[0]['top_left_y'])) >= 0 else 0 
            lby = int(round(box[0]['bottom_right_y'])) if int(round(box[0]['bottom_right_y'])) >= 0 else 0 
            ubx = int(round(box[0]['top_left_x'])) if int(round(box[0]['top_left_x'])) >= 0 else 0 
            lbx = int(round(box[0]['bottom_right_x'])) if int(round(box[0]['bottom_right_x'])) >= 0 else 0 

            if ubx >= lbx:
                ubx = ubx - ( ubx - lbx + 1 )

            if uby >= lby:
                uby = lby - ( uby - lby + 1 )

            cropped_img = img[uby:lby,ubx:lbx]

            ext_txt = ext_txt + " " + eval_new_data(
                cropped_img,
                processor=processor,
                num_samples=1,
                model=model
                )

        print(ext_txt)

        text_strs.append(ext_txt)

        ext_txt = ""

    print(text_strs)
      
    print("finished image text recognizing lines")
    
    return text_strs


print("Beginning Script")

dirs = [  "c:/Users/Karkaras/Desktop/img recs", "c:/Users/Karkaras/Desktop/proc_sample_imgs/spare_text_imgs", "c:/Users/Karkaras/Desktop/proc_sample_imgs/typed_sudoc_imgs"
         , "c:/Users/Karkaras/Desktop/proc_sample_imgs/hw_sudocs", "c:/Users/Karkaras/Desktop/proc_sample_imgs/title_imgs" ]

for path in dirs:
    
    img_dir = os.listdir(path)

    img_dir = [ os.path.join(path, img) for img in img_dir ]

    images_coll = [ keras_ocr.tools.read(img) for img in img_dir ]

    extracted_data = img_recognition(images_coll)

    
    datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

    print(datapath)
    
print("finished image reading lines")



