import os
import datetime
import matplotlib.pyplot as plt
import numpy as np
import string
import math
import cv2
import tensorflow as tf
import pandas as pd
import keras_ocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, utils
from PIL import Image
import torch
import glob
import scipy.misc
import pickle
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

device = 'cpu'
utils.logging.set_verbosity_error()
	
def read_image(image_path):
    image = Image.open(image_path).convert('RGB')
    return image
	
def ocr(image, processor, model):
    
    pixel_values = processor(image, return_tensors='pt').pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text
	
def eval_new_data(img, processor, num_samples=4, model=None):
    text = ocr(img, processor, model)
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

    output_data = pd.DataFrame(columns=['Title', 'SuDoc', 'Publication Year','Error Code','Query Status'])

    output_data['SuDoc'] = data

    print(output_data)

    output_data.to_csv(datapath)

    return datapath

def text_classification(img, rf_classifier):
    rows = img.shape[0]
    cols = img.shape[1]
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #print(rows)
    #print(cols)
    #print(rows/cols)
    retval, bwMask =cv2.threshold(img, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    mycnt=0
    myavg=0
    for xx in range (0,cols):
        mycnt=0
        for yy in range (0,rows):
            if bwMask[yy,xx]==0:
                mycnt=mycnt+1
                
        myavg=myavg+(mycnt*1.0)/rows
    myavg=myavg/cols
    #print(myavg)
    change=0
    for xx in range (0,rows):
        mycnt=0
        for yy in range (0,cols-1):
            if bwMask[xx:yy].all()!=bwMask[xx:yy+1].all():
                mycnt=mycnt+1
        change=change+(mycnt*1.0)/cols
    change=change/(rows)

    #rf_classifier = pickle.load(open("text_classifier.sav", 'rb'))

    ext_features = np.reshape([rows, cols, rows/cols, myavg, change], (1, -1))

    label = rf_classifier.predict(ext_features)

    #pickle.dump(rf_classifier, open("text_classifier.sav", 'wb'))

    return label

def load_models():

    rf_classifier = pickle.load(open("./text_classifier.sav", 'rb'))

    data_dir = '.'
    alphabet = string.digits + string.ascii_letters + "./-(),#:"

    recognizer_alphabet = ''.join(sorted(set(alphabet.lower())))

    detector = keras_ocr.detection.Detector(weights='clovaai_general')
    recognizer = keras_ocr.recognition.Recognizer(
        alphabet=recognizer_alphabet
    )

    recognizer.compile()

    recognizer.model.load_weights('./curr_recognizer.h5')

    pipeline = keras_ocr.pipeline.Pipeline(detector=detector, recognizer=recognizer)

    processor_typed = TrOCRProcessor.from_pretrained('microsoft/trocr-large-printed')
    model_typed = VisionEncoderDecoderModel.from_pretrained(
        'microsoft/trocr-large-printed'
    ).to(device)

    processor_hw = TrOCRProcessor.from_pretrained('microsoft/trocr-large-handwritten')
    model_hw = VisionEncoderDecoderModel.from_pretrained(
        'microsoft/trocr-large-handwritten'
    ).to(device)
    
    return processor_typed, model_typed, processor_hw, model_hw, rf_classifier, pipeline
 
def img_recognition(img, processor_typed, model_typed, processor_hw, model_hw, rf_classifier, pipeline):

    ext_txt = ""

    pred = pipeline.recognize([img])

    pred = get_distance(pred)

    pred = list(distinguish_rows(pred))

    pred = list(filter(lambda x:x!=[], pred))

    for row in pred:

        row = sorted(row, key=lambda x:x['dist_from_origin'])

        for box in row:

            uby = int(round(box['top_left_y'])) if int(round(box['top_left_y'])) >= 0 else 0 
            lby = int(round(box['bottom_right_y'])) if int(round(box['bottom_right_y'])) >= 0 else 0 
            ubx = int(round(box['top_left_x'])) if int(round(box['top_left_x'])) >= 0 else 0 
            lbx = int(round(box['bottom_right_x'])) if int(round(box['bottom_right_x'])) >= 0 else 0 
            
            if ubx >= lbx:
                ubx = ubx - ( ubx - lbx + 1 )

            if uby >= lby:
                uby = lby - ( uby - lby + 1 )

            cropped_img = img[uby:lby,ubx:lbx]
            
            label = text_classification(cropped_img, rf_classifier)


            if label in [ 'Printed_extended', 'Other_extended' ]:

                ext_txt = ext_txt + " " + eval_new_data(
                    cropped_img,
                    processor=processor_typed,
                    num_samples=20,
                    model=model_typed
                    ) 

            elif label in [ 'Handwritten_extended', 'Mixed_extended' ]:

                ext_txt = ext_txt + " " + eval_new_data(
                    cropped_img,
                    processor=processor_hw,
                    num_samples=20,
                    model=model_hw
                    )

            ext_txt = ext_txt.replace(string.punctuation, '')
    
    return ext_txt

def par_img_proc_caller(img_list):

    processor_typed, model_typed, processor_hw, model_hw, rf_classifier, pipeline = load_models()

    extracted_data = []
    
    exe = ThreadPoolExecutor(cpu_count())

    for img in img_list:
        extracted_data.append(exe.submit(img_recognition, img, processor_typed, model_typed, processor_hw, model_hw, rf_classifier, pipeline))

    for obj in range(len(extracted_data)):
        extracted_data[obj] = extracted_data[obj].result()

    print(extracted_data)

    return extracted_data

def read_data(path):

    print("Beginning Script")
       
    img_dir = os.listdir(path)

    img_dir = [ os.path.join(path,
                                 img) for img in img_dir ]

    images_coll = [ keras_ocr.tools.read(img) for img in img_dir ]

    extracted_data = par_img_proc_caller(images_coll)

        #extracted_data = img_recognition(img_dir, images_coll)

    datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

    return(datapath)
    
    print("finished image reading lines")

#read_data()


