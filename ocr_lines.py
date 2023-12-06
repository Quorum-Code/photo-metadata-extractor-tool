import os
import datetime
import time
import numpy as np
from string import digits, ascii_letters, punctuation
import math
import cv2
import pandas as pd
import keras_ocr
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, utils
import pickle
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

def warn(*args, **kwargs):
    """
    Warning Suppression

    :return: nothing
    """
    pass

### Call to skip warning function directly above and further warning suppression ###
import warnings

warnings.warn = warn
utils.logging.set_verbosity_error()
###

### Global to facilitate progress bar for parallel processing of images
count = 0

### The device with which to run image recognition functions on
device = 'cpu'

def ocr(image, processor, model):
    """
    Calls transformers functions to perform text recognition from image.

    :param image: Image with text.
    :param processor: Class to preprocess images for extraction.
    :param model: VisionEncoderDecoder model to generate text from image.
    :return: The extracted text.
    """

    pixel_values = processor(image, return_tensors='pt').pixel_values.to(device)
    generated_ids = model.generate(pixel_values)
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

def distinguish_rows(lst, thresh=15):
    """
    Parses returned bounding boxes from objected detected function by rows
    :param lst: List of bounding boxes
    :param thresh: Max number of boxes per row
    :return: Sublists containing the bounding boxes grouped by row
    """

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
    """
    Gathers measurements for a list of bounding boxes for further processing

    :param preds: List of bounding boxes
    :return: List of dictionary elements built as {bounding box:data}
    """
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
    """
    Parse extracted text for phrase that could be a year

    :param data: Text string to be parsed for a value representing a year
    :return: Value to be used as year
    """
    pub_year = ""
    for phrase in data.split():
        if phrase.isdigit() and (1600 <= int(phrase) <= datetime.datetime.today().year+1):
            pub_year = phrase
    return pub_year

def merge_dicts(data):
    """
    Function to merge a list of dictionaries into one

    :param data: List of dictionaries
    :return: Dictionary
    """
    merged_dict = data[0]
    for idx in range(len(data)):
        merged_dict.update(data[idx])
    return merged_dict

def write_dataframe(data, label):
    """
    Function to write extracted data out to a csv

    :param data: Dictionary containing data as {image path: extracted data}
    :param label: Path of directory
    :return: Path of csv containing the data
    """

    print("Writing Out Data to CSV")

    #change this to test each individual element in data

    label_classifier = pickle.load(open("classifiers/rf_model.sav", 'rb'))
    #label_classifier = pickle.load(open("MLModelsList/classifiers/rf_model.sav", 'rb'))
    curr_time = datetime.datetime.now()
    init_datapath = './extracted_data'
    datapath = "extracted_data/extracted_data.csv"
    os.makedirs(init_datapath, exist_ok=True)
    data = merge_dicts(data)
    output_data = pd.DataFrame(columns=['ID', 'Title', 'SuDoc', 'Publication Year', 'Path','Error Code','Query Status', 'Sudoc Image', 'Title Image'])
    title_key = sudoc_key = text_type_1_val = text_type_2_val = pub_year = ""
    #for idx in range(len(data)):
    for idx, key in enumerate(data):
        label_pred = np.reshape(text_feature_extractor(data[key]), (1, -1))
        text_type = label_classifier.predict(label_pred)[0]
        if text_type == 'title':
            text_type_1_key = 'Title'
            text_type_1_val = data[key]
            title_key = key
        elif text_type == 'sudoc':
            text_type_2_key = 'SuDoc'
            text_type_2_val = data[key]
            data[key] = data[key].replace(" ", "")
            sudoc_key = key
            pub_year = pub_year_extraction(data[key])
        if (idx % 2) == 1:
            output_data = pd.concat([output_data, pd.DataFrame([{'ID': (idx-1)/2, text_type_1_key: text_type_1_val, text_type_2_key: text_type_2_val,
                                    'Publication Year': pub_year, 'Sudoc Image': sudoc_key, 'Title Image': title_key}])], ignore_index=True)
            title_key = sudoc_key = text_type_1_val = text_type_2_val = pub_year = ""
    #print(output_data)
    output_data.to_csv(datapath, index=False)
    print("Completed Writing Step")
    return datapath

def text_classification(img, classifier):
    """
    Function to classify text within an image as handwritten or typed

    :param img: Image with text
    :param classifier: Model to classify image
    :return: Label from resulting classification
    """

    rows = img.shape[0]
    cols = img.shape[1]
    img=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
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
    change=0
    for xx in range (0,rows):
        mycnt=0
        for yy in range (0,cols-1):
            if bwMask[xx:yy].all()!=bwMask[xx:yy+1].all():
                mycnt=mycnt+1
        change=change+(mycnt*1.0)/cols
    change=change/(rows)
    ext_features = np.reshape([rows, cols, rows/cols, myavg, change], (1, -1))
    label = classifier.predict(ext_features)
    return label


def load_models():
    """
    Function to load text detection, text recognition, and text classification models

    :return: Text detection, text recognition, and classification models
    """
    print("Loading Models")
    #writing_classifier = pickle.load(open("classifiers/hgbc_model.sav", 'rb'))
    writing_classifier = pickle.load(open("classifiers/text_classifier.sav", 'rb'))
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
    processor_typed = TrOCRProcessor.from_pretrained('ocr_models/typed_ocr_models')
    model_typed = VisionEncoderDecoderModel.from_pretrained(
        'ocr_models/typed_ocr_models'
    ).to(device)
    processor_hw = TrOCRProcessor.from_pretrained('ocr_models/hw_ocr_models')
    model_hw = VisionEncoderDecoderModel.from_pretrained(
        'ocr_models/hw_ocr_models'
    ).to(device)
    print("Successfully Loaded Models")
    return processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline

def text_feature_extractor(value):
    """
    Function to take measurements from a text string for classification purposes

    :param value: Text string
    :return: A list of values
    """
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

def img_recognition(img_path, processor_typed, model_typed, processor_hw,
                    model_hw, writing_classifier, pipeline, total_images, progress_signal):
    """
    Function to perform the bulk of the text recognition tasks

    :param img_path: Path of image to be processed
    :param processor_typed: Processor for typed TROCR
    :param model_typed: Model for typed TROCR
    :param processor_hw: Processor for handwritten TROCR
    :param model_hw: Model for handwritten TROCR
    :param writing_classifier: Classifier for text type(handwritten vs typed)
    :param pipeline: Wrapper class for text detection model
    :param total_images: Number of images to be processed
    :param progress_signal: Signal for GUI process bar
    :return: Dictionary with extracted data as {image path: extracted text}
    """
    global count
    extractions = {}
    print("Beggining extraction  on image: ", img_path)
    img = keras_ocr.tools.read(img_path)
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
                ubx = ubx - (ubx - lbx + 1)
            if uby >= lby:
                uby = lby - (uby - lby + 1)
            cropped_img = img[uby:lby, ubx:lbx]
            label = text_classification(cropped_img, writing_classifier)
            #print(label)
            if label in [ 'Printed_extended', 'Other_extended' ]:
            #if label == 'typed':
                ext_txt = ext_txt + " " + ocr(
                    cropped_img,
                    processor=processor_typed,
                    model=model_typed
                )
            elif label in [ 'Handwritten_extended', 'Mixed_extended' ]:
            #elif label == 'handwritten':
                ext_txt = ext_txt + " " + ocr(
                    cropped_img,
                    processor=processor_hw,
                    model=model_hw
                )
            ext_txt = ''.join('' if c in punctuation else c for c in ext_txt)
    #print(ext_txt)
    extractions[img_path]= ext_txt
    print("Completed extraction on image: ", img_path)
    count += 1
    progress_signal.emit(count/total_images)
    return extractions

def par_img_proc_caller(img_dir, progress_signal, total_images):
    """
    Function to call the image processing block in parallel

    :param img_dir: List of files to be processed
    :param progress_signal: Signal for GUI process bar
    :param total_images: Number of total images
    :return: List with the extracted data
    """
    start_time = time.time()

    processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline = load_models()

    load_time = time.time() - start_time

    time_file = open('ml_pipeline_timings.txt', 'a')

    time_file.write("Total images: " + str(len(img_dir)) + "\n")

    time_file.write("Model Loading Time: " + str(load_time) + "\n")

    extracted_data = []

    #num_workers = 2 # if cpu_count() > 5 else 1

    exe = ThreadPoolExecutor(2)

    start_time = time.time()

    collected_data = []

    for idx in range(0, len(img_dir), 2):
        for worker in range(0, 2):
            #extracted_data.append(exe.submit(img_recognition, img_dir[idx:idx+2], processor_typed, model_typed, processor_hw, model_hw, writing_classifier, pipeline, total_images, progress_signal))
            collected_data.append(exe.submit(img_recognition, img_dir[(idx+worker)], processor_typed, model_typed, processor_hw, model_hw, writing_classifier,
                   pipeline, total_images, progress_signal))

        for obj in range(len(collected_data)):
            extracted_data.append(collected_data[obj].result())
        collected_data = []
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
               #"c:/Users/Karkaras/Desktop/proc_sample_imgs/test_set/test_typed_sudoc"
               "c:/Users/Karkaras/Desktop/image_pairs"
        ]

    for path in dirs:

        img_dir = os.listdir(path)

        img_dir = [ os.path.join(path, img) for img in img_dir ]

        img_dir.sort(key=lambda x: os.path.getctime(x))

        #images_coll = [ keras_ocr.tools.read(img) for img in img_dir ]

        #extracted_data = par_img_proc_caller(images_coll)

        total_images = len(img_dir)

        extracted_data = par_img_proc_caller(img_dir, total_images)

        datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

        #print(datapath)
    
    print("finished image reading lines")
    return datapath
'''
#The read_data function for use

def read_data(path,progress_signal):
    """
    Function to initiate image processing

    :param path: Path of directory with images
    :param progress_signal: Signal for GUI process bar
    :return: Path of written csv
    """
    print("Beginning Script")
       
    global count
    count = 0

    img_dir = os.listdir(path)

    img_dir = [ os.path.join(path, img) for img in img_dir ]

    img_dir.sort(key=lambda x: os.path.getctime(x))

    total_images = len(img_dir)

    extracted_data = par_img_proc_caller(img_dir, progress_signal, total_images)

    datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

    print("finished image reading lines")

    return(datapath)

#read_data()
