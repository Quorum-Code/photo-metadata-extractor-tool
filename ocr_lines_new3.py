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
import torch
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

def write_dataframe(data, label):

    print("Writing Out Data to CSV")

    #change this to test each individual element in data

    label_classifier = pickle.load(open("classifiers/rf_model.sav", 'rb')) 

    curr_time = datetime.datetime.now()

    init_datapath =  '.\\extracted_data\\'

    #curr_time = curr_time.strftime('%Y-%m-%d %H-%M-%S')[:-3] + "_" + label + '_extracted_data.csv'

    #datapath = init_datapath + curr_time

    datapath = "extracted_data/extracted_data.csv"

    os.makedirs(init_datapath, exist_ok=True)

    #print(datapath)

    output_data = pd.DataFrame(columns=['Title', 'SuDoc', 'Publication Year','Error Code','Query Status'])

    print(data)

    for idx in range(len(data)):

            label_pred = np.reshape(text_feature_extractor(data[idx]), (1, -1)) 

            #print(label_pred)

            text_type = label_classifier.predict(label_pred)[0]

            if text_type == 'title':
                text_type = 'Title'
            elif text_type == 'sudoc':
                text_type = 'SuDoc'

            output_data = pd.concat([pd.DataFrame([{text_type:data[idx]}]), output_data], ignore_index=True)

    #print(output_data)

    output_data.to_csv(datapath, index=False)

    print("Completed Writing Step")

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

    print("Loading Models")

    writing_classifier = pickle.load(open("classifiers/text_classifier.sav", 'rb'))

    data_dir = '.'
    alphabet = string.digits + string.ascii_letters + "./-(),#:"

    recognizer_alphabet = ''.join(sorted(set(alphabet.lower())))

    detector = keras_ocr.detection.Detector(weights='clovaai_general')
    recognizer = keras_ocr.recognition.Recognizer(
        alphabet=recognizer_alphabet
    )

    recognizer.compile()

    recognizer.model.load_weights('classifiers/curr_recognizer.h5')

    pipeline = keras_ocr.pipeline.Pipeline(detector=detector, recognizer=recognizer)

    processor_typed = TrOCRProcessor.from_pretrained('./ocr_models/typed_ocr_models')
    model_typed = VisionEncoderDecoderModel.from_pretrained(
        './ocr_models/typed_ocr_models'
    ).to(device)

    processor_hw = TrOCRProcessor.from_pretrained('./ocr_models/hw_ocr_models')
    model_hw = VisionEncoderDecoderModel.from_pretrained(
        './ocr_models/hw_ocr_models'
    ).to(device)

    print("Successfully Loaded Models")
    
    return processor_typed, model_typed, processor_hw, model_hw, \
           writing_classifier, pipeline

def text_feature_extractor(value):

    text_length = len(value)

    words = value.count(" ") + 1

    numbers = sum(c.isdigit() for c in value)

    letters = sum(c.isalpha() for c in value)

    if text_length == 0:

        num_text_ratio = 0

    else:

        num_text_ratio = numbers/text_length

    avg_word_length = sum(len(word) for word in value) / words

    return [ text_length, words, num_text_ratio, avg_word_length]
 
def img_recognition(img_dir, processor_typed, model_typed, processor_hw,
                    model_hw, writing_classifier, pipeline):

    print("Beggining extraction on image: ", img_dir)

    img = keras_ocr.tools.read(img_dir)

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
            
            label = text_classification(cropped_img, writing_classifier)

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

            ext_txt = ''.join('' if c in string.punctuation else c for c in ext_txt)

    print("Completed extraction on image: ", img_dir)
    
    return ext_txt

def par_img_proc_caller(img_dir, progress_signal, total_images):

    #load models outside of this call

    processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline = load_models()

    extracted_data = []
    
    exe = ThreadPoolExecutor(math.ceil(cpu_count()/2))
    i = 0
    print("Total images", total_images)
    for img in img_dir:
        extracted_data.append(exe.submit(img_recognition, img, processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline))
        progress = (i+ 1)/(total_images+1)
        progress_signal.emit(progress)
        i +=1

    for obj in range(len(extracted_data)):
        extracted_data[obj] = extracted_data[obj].result()
    i+=1
    progress =(i+1)/(total_images+1)
    progress_signal.emit(progress)
    print(extracted_data)

    return extracted_data
'''
#This read_data is here only for debugging
def read_data():

    print("Beginning Script")

    #dirs = [ "c:/Users/Karkaras/Desktop/proc_sample_imgs/typed_sudoc_imgs" ]

    #dirs = [ "c:/Users/Karkaras/Desktop/proc_sample_imgs/title_imgs" ]

    dirs = [  "c:/Users/Karkaras/Desktop/proc_sample_imgs/typed_sudoc_imgs",
              "c:/Users/Karkaras/Desktop/proc_sample_imgs/hw_sudocs",
              "c:/Users/Karkaras/Desktop/proc_sample_imgs/title_imgs",
              "c:/Users/Karkaras/Desktop/Sudocsv2",
              "c:/Users/Karkaras/Desktop/classifier scripts/proc_sample_imgs/spare_text_imgs",
              "c:/Users/Karkaras/Desktop/img recs" ]
            

    for path in dirs:
    
        img_dir = os.listdir(path)

        img_dir = [ os.path.join(path,
                                 img) for img in img_dir ]

        #images_coll = [ keras_ocr.tools.read(img) for img in img_dir ]

        #extracted_data = par_img_proc_caller(images_coll)

        extracted_data = par_img_proc_caller(img_dir)

        #extracted_data = img_recognition(img_dir, images_coll)

        datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

        print(datapath)
    
    print("finished image reading lines")
'''
#The read_data function for use

def read_data(path,progress_signal):

    print("Beginning Script")
       
    img_dir = os.listdir(path)

    img_dir = [ os.path.join(path,
                                 img) for img in img_dir ]

    images_coll = [ keras_ocr.tools.read(img) for img in img_dir ]
    total_images = len(images_coll)
    extracted_data = par_img_proc_caller(images_coll, progress_signal,total_images)

        #extracted_data = img_recognition(img_dir, images_coll)

    datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

    return(datapath)
   
    print("finished image reading lines")

#read_data()


