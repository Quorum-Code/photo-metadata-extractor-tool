import os
import datetime
#import matplotlib.pyplot as plt
import numpy as np
from string import digits, ascii_letters, punctuation
import math
import cv2
#import tensorflow as tf
import pandas as pd
import keras_ocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, utils
#import torch
import pickle
from concurrent.futures import ThreadPoolExecutor

from multiprocessing import cpu_count
import time
import gc

def warn(*args, **kwargs):
    pass
import warnings
warnings.warn = warn

count = 0

device = 'cpu'
utils.logging.set_verbosity_error()

#keras_ocr.config.configure()

def ocr(image, processor, model):
    pixel_values = processor(image, return_tensors='pt').pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

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
            bottom_right_x, bottom_right_y = group[1][2]
            center_x = (top_left_x + bottom_right_x)/2
            center_y = (top_left_y + bottom_right_y)/2
            dist_from_origin = math.dist([x0,y0], [center_x, center_y])
            distance_y = center_y - y0
            detections.append({
                'text': group[0],
                'top_left_x': top_left_x,
                'top_left_y': top_left_y,
                'bottom_right_x': bottom_right_x,
                'bottom_right_y': bottom_right_y,
                'dist_from_origin': dist_from_origin,
                'distance_y': distance_y})
            idx = idx +1
    return detections

def pub_year_extraction(data):
    pub_year = ""
    for phrase in data.split():
        if phrase.isdigit() and (1600 <= int(phrase) <= datetime.datetime.today().year+1):
            pub_year = phrase
    return pub_year

def merge_dicts(data):
    merged_dict = data[0]
    for idx in range(len(data)):
        merged_dict.update(data[idx])
    return merged_dict

def write_dataframe(data, label):

    print("Writing Out Data to CSV")

    #change this to test each individual element in data

    label_classifier = pickle.load(open("classifiers/rf_model.sav", 'rb'))
    #label_classifier = pickle.load(open("MLModelsList/classifiers/rf_model.sav", 'rb'))

    curr_time = datetime.datetime.now()

    init_datapath =  './extracted_data'

    datapath = "extracted_data/extracted_data.csv"

    os.makedirs(init_datapath, exist_ok=True)

    data = merge_dicts(data)

    output_data = pd.DataFrame(columns=['ID', 'Title', 'SuDoc', 'Publication Year', 'Path','Error Code','Query Status'])

    idx = 0

    #for idx in range(len(data)):
    for key in data:

            #print(data[0][key])

            label_pred = np.reshape(text_feature_extractor(data[key]), (1, -1))

            #print(label_pred)

            text_type = label_classifier.predict(label_pred)[0]

            pub_year = pub_year_extraction(data[key])

            if text_type == 'title':
                text_type = 'Title'
            elif text_type == 'sudoc':
                text_type = 'SuDoc'
                data[key] = data[key].replace(" ", "")

            output_data = pd.concat([output_data, pd.DataFrame([{'ID': idx, text_type: data[key], 'Publication Year': pub_year,
                                    'File Name': key}],)], ignore_index=True)
            idx = idx + 1

    print(output_data)

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
    #writing_classifier = pickle.load(open("MLModelsList/classifiers/text_classifier.sav", 'rb'))
    data_dir = '.'
    alphabet = digits + ascii_letters + "./-(),#:"

    recognizer_alphabet = ''.join(sorted(set(alphabet.lower())))

    print("Loading keras_ocr models")

    detector = keras_ocr.detection.Detector(weights='clovaai_general')
    recognizer = keras_ocr.recognition.Recognizer(
        alphabet=recognizer_alphabet
    )

    recognizer.compile()

    recognizer.model.load_weights('classifiers/curr_recognizer.h5')
    #recognizer.model.load_weights('MLModelsList/curr_recognizer.h5')

    pipeline = keras_ocr.pipeline.Pipeline(detector=detector, recognizer=recognizer)

    print("Loading trocr models")

    '''processor_typed = TrOCRProcessor.from_pretrained('./MLModelsList/ocr_models/typed_ocr_models')
    model_typed = VisionEncoderDecoderModel.from_pretrained(
        './MLModelsList/ocr_models/typed_ocr_models'
    ).to(device)
    '''
    processor_typed = TrOCRProcessor.from_pretrained('./ocr_models/typed_ocr_models')
    model_typed = VisionEncoderDecoderModel.from_pretrained(
        './ocr_models/typed_ocr_models'
    ).to(device)
    

    processor_hw = TrOCRProcessor.from_pretrained('./ocr_models/hw_ocr_models')
    model_hw = VisionEncoderDecoderModel.from_pretrained(
        './ocr_models/hw_ocr_models'
    ).to(device)
    

    print("Successfully Loaded Models")
    
    return processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline

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
                    model_hw, writing_classifier, pipeline, total_images, progress_signal):
    global count

    extractions = {}

    for img_path in img_dir:

        print("Beggining extraction  on image: ", img_path)

        img = keras_ocr.tools.read(img_path)

        ext_txt = ""

        #print([img])

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

                    ext_txt = ext_txt + " " + ocr(
                        cropped_img,
                        processor=processor_typed,
                        model=model_typed
                        )

                elif label in [ 'Handwritten_extended', 'Mixed_extended' ]:

                    ext_txt = ext_txt + " " + ocr(
                        cropped_img,
                        processor=processor_hw,
                        model=model_hw
                        )

                ext_txt = ''.join('' if c in punctuation else c for c in ext_txt)

        #print(ext_txt)

        extractions[img_path]=ext_txt

        #print("Completed extraction on image: ", img_dir)

        count +=1
        progress_signal.emit(count/total_images)

    return extractions

def par_img_proc_caller(img_dir, progress_signal, total_images):

    start_time = time.time()

    processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline = load_models()

    load_time = time.time() - start_time

    time_file = open('ml_pipeline_timings.txt', 'a')

    time_file.write("Total images: " + str(len(img_dir)) + "\n")

    time_file.write("Model Loading Time: " + str(load_time) + "\n")

    extracted_data = []

    num_workers = 2 if cpu_count() > 5 else 1

    exe = ThreadPoolExecutor(num_workers)

    img_list_split = np.array_split(img_dir, num_workers)

    i = 0

    start_time = time.time()

    for worker in range(num_workers):
        extracted_data.append(exe.submit(img_recognition, img_list_split[worker], processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline, total_images, progress_signal))
        #extracted_data.append(exe.submit(img_recognition, img_list_split[worker], processor_typed, model_typed, processor_hw, model_hw, writing_classifier,
        #           pipeline, total_images))  # , progress_signal))

    for obj in range(len(extracted_data)):
        extracted_data[obj] = extracted_data[obj].result()

    print(extracted_data)

    load_time = time.time() - start_time

    time_file.write("Total Extraction Time: " + str(load_time) + "\n")

    return extracted_data
'''
#This read_data is here only for debugging
def read_data():

    print("Beginning Script")

    #dirs = [ "c:/Users/Karkaras/Desktop/proc_sample_imgs/typed_sudoc_imgs" ]

    #dirs = [ "c:/Users/Karkaras/Desktop/proc_sample_imgs/title_imgs" ]

    dirs = [ #'C:/Users/Duff/Desktop/bryans files/proc_sample_imgs/proc_sample_imgs/typed_sudoc_imgs' ]#,
              #"C:/Users/Duff/Desktop/bryans files/proc_sample_imgs/proc_sample_imgs/hw_sudocs" ] #,
              #"C:/Users/Duff/Desktop/bryans files/proc_sample_imgs/proc_sample_imgs/title_imgs" ]#,
              #"C:/Users/Duff/Desktop/bryans files/proc_sample_imgs/proc_sample_imgs/Sudocsv2",
              #"C:/Users/Duff/Desktop/bryans files/proc_sample_imgs/proc_sample_imgs/spare_text_imgs"
               #"c:/Users/Karkaras/Desktop/proc_sample_imgs/test_set/test_hw_sudoc",
               #"c:/Users/Karkaras/Desktop/proc_sample_imgs/test_set/test_title"#,
               "c:/Users/Karkaras/Desktop/proc_sample_imgs/test_set/test_typed_sudoc"
        ]
    for path in dirs:
    
        img_dir = os.listdir(path)

        img_dir = [ os.path.join(path, img) for img in img_dir ]

        #images_coll = [ keras_ocr.tools.read(img) for img in img_dir ]

        #extracted_data = par_img_proc_caller(images_coll)

        total_images = len(img_dir)

        extracted_data = par_img_proc_caller(img_dir, total_images)

        #extracted_data = img_recognition(img_dir, images_coll)

        datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

        print(datapath)
    
    print("finished image reading lines")
'''
#The read_data function for use

def read_data(path,progress_signal):

    print("Beginning Script")
       
    global count
    count = 0

    img_dir = os.listdir(path)

    img_dir = [ os.path.join(path, img) for img in img_dir ]

    #images_coll = [ keras_ocr.tools.read(img) for img in img_dir ]
    total_images = len(img_dir)
    extracted_data = par_img_proc_caller(img_dir, progress_signal, total_images)

        #extracted_data = img_recognition(img_dir, images_coll)

    datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

    print("finished image reading lines")

    return(datapath)

#read_data()


