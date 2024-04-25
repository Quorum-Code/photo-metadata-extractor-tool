from scipy import ndimage as ndi
import time
import os
from functools import wraps
import numpy as np
import math
import cv2
import pandas as pd
import string 
import datetime
from transformers import TrOCRProcessor, VisionEncoderDecoderModel, utils
import ultralytics 
from onnxruntime import InferenceSession
from ocr_test import *
import glob

### Call to skip warning function directly above and further warning suppression ###
import warnings

def warn(*args, **kwargs):
    """
    Warning Suppression

    :return: nothing
    """
    pass

warnings.warn = warn
warnings.filterwarnings("ignore", category=FutureWarning) 
utils.logging.set_verbosity_error()
###

### The device with which to run image recognition functions on
device = 'cpu'

timers = ('main_process',
          'model_load',
          'text_recognition',
          'text_detection',
          'text_type_classification',
          'field_classification')

def function_timer(timer_target):
    """
    Wrapper function to collect and write 

        :param load_ocr_models: Load all necessary ML models except field_classifier which is not needed 
                                until the last part of the process
        :param load_field_classifier: Load field_classifier only 
    """

    def outer_wrap(func):
        @wraps(func)
        def wrap(*args, **kwargs):
            if timer_target == 'main_process':
                os.makedirs("./ml_pipeline_diagnostics/", exist_ok=True)
                data_dir = get_out_dir_pth(init=True)
                os.makedirs(data_dir, exist_ok = True)
            else: 
                data_dir = get_out_dir_pth()
            start = time.time()
            result = func(*args, **kwargs)
            end_timing = time.time() - start
            datapath = data_dir + timer_target + "_timings.txt"
            time_file = open(datapath, 'a')
            if timer_target == 'main_process':
                final_summary = {}
                final_summary['num_of_imgs'] = result
                time_file.write("Number of Images: " + str(result) + "\n")
                final_summary['total_proc_time'] = end_timing
                time_file.write("Processing Time: " + str(end_timing) + "\n")
                avg_time = end_timing/result
                final_summary['proc_time_per_img'] = avg_time
                time_file.write("Average Processing Time Per Image: " + str(avg_time))
                time_file.close()
                for timer_list in timers:
                    if timer_list in ('main_process', 'model_load'):
                        continue
                    fin_datapath = data_dir + timer_list + "_timings.txt"
                    time_file = open(fin_datapath, 'a')
                    time_data = pd.read_csv(fin_datapath, header=None, delim_whitespace=True)
                    avg = time_data.mean(axis=0).to_string(name=False,
                                                           index=False,
                                                           dtype=False)
                    time_file.write("Average: " + str(avg))    
                    time_file.close()
                    final_summary[timer_list] = avg
                final_summary = pd.DataFrame(final_summary, index=[0])
                fin_summ_pth = data_dir + "run_summary.csv"
                final_summary.to_csv(fin_summ_pth, index=False)
                print("Run statistics saved to: ", data_dir)
            else:
                time_file.write(str(end_timing) + "\n")
            return result
        return wrap
    return outer_wrap

class ocr():
    def __init__(self, load_ocr_models=True, load_field_classifier=False):
        
        """
        An OCR object to hold and load the necessary machine learning models.

        :param load_ocr_models: Load all necessary ML models except field_classifier which is not needed 
                                until the last part of the process
        :param load_field_classifier: Load field_classifier only 
        """

        self.processor_typed = ''
        self.model_typed = ''
        self.processor_hw = ''
        self.model_hw = ''
        self.writing_classifier = ''
        self.field_classifier = ''
        self.detector = ''

        if load_ocr_models:
            self.load_ocr_models()
        if load_field_classifier:
            self.load_field_classifier()

    @function_timer('model_load')
    def load_ocr_models(self):
        """
        Function to load text detection, text recognition, and text classification models

        :return: Text detection, text recognition, and classification models
        """
        print("Loading Text Type Classifier")
      
        self.writing_classifier = ultralytics.YOLO('./ml_models/text_type_classifiers/yolo_text_type_clf.pt').to(device)

        print("Loading Text Detector")

        self.detector = ultralytics.YOLO('./ml_models/text_detectors/yolotextdet.pt').to(device)

        print("Loading TrOCR models")

        self.processor_typed = TrOCRProcessor.from_pretrained('./ml_models/ocr_models/typed_ocr_models')
        self.model_typed = VisionEncoderDecoderModel.from_pretrained(
            './ml_models/ocr_models/typed_ocr_models'
        ).to(device)

        self.processor_hw = TrOCRProcessor.from_pretrained('./ml_models/ocr_models/hw_ocr_models')
        self.model_hw = VisionEncoderDecoderModel.from_pretrained(
            './ml_models/ocr_models/hw_ocr_models'
        ).to(device)
        
        print("Successfully Loaded Models")

    @function_timer('model_load')
    def load_field_classifier(self):
        """
        Function to load field classification model

        :return: Text detection, text recognition, and classification models
        """

        self.field_classifier = InferenceSession("./ml_models/label_classifiers/field_onnx_etc_model.onnx" \
                        , providers=["CPUExecutionProvider"])

def get_out_dir_pth(init = False):
    """
        Function to find or create the directory where the OCR pipeline performance reports will go.

        :param init: If true a new directory will be created for the current run, else the latest directory will be returned
        :return: The output directory path
    """

    base_dir = "./ml_pipeline_diagnostics/"

    if init == True:
        if len([os.path.basename(path)[3:] for path in glob.iglob(base_dir + 'run[0-9]*') if os.path.isdir(path)])>0:
             return base_dir + "run" + str(max([int(os.path.basename(path)[3:]) for path in glob.iglob(base_dir + 'run[0-9]*') if os.path.isdir(path)])+1) + "/" 
        else:
            return base_dir + "run0/"       
    else:
        if len([os.path.basename(path)[3:] for path in glob.iglob(base_dir + 'run[0-9]*') if os.path.isdir(path)])>0:
            return base_dir + "run" + str(max([int(os.path.basename(path)[3:]) for path in glob.iglob(base_dir + 'run[0-9]*') if os.path.isdir(path)]))+"/" 
        else:
            return base_dir + "run0/"


def dir_validation(dir):
    """
    Function to check if the passed directory has the right format

    :param dir: Directory to check
    :return: error code
    """

    supported_file_types = [ 'bmp', 'dib', 'jpeg', 'jpg', 'jpe', 'jp2', 'png', 'webp', 'avif',
                            'pbm', 'pgm', 'ppm', 'pxm', 'pnm', 'pfm', 'sr', 'ras', 'tiff', 'tif',
                            'exr', 'hdr', 'pic'
                            ]
    
    if (len(dir) % 2) == 1:
        return 201
    for file in dir:
        ext = file.split(".")[-1]
        if ext not in supported_file_types:
            return 202
    return 200

def hconcat_resize(img_list, interpolation = cv2.INTER_CUBIC): 
    """
    Function to resize images and concatenate images horizontally

    :param img_list: list of images to perform operations on
    :param interpolation: interpolation argument for resize function from cv2 library

    :return: Concatenated image
    """

    h_min = min(img.shape[0]  
                for img in img_list) 
    
    im_list_resize = [cv2.resize(img, 
                                 (int(img.shape[1] * h_min / img.shape[0])
                                  if (img.shape[1] * h_min / img.shape[0]) > 1
                                  else img.shape[1], 
                                  h_min),
                                 interpolation = interpolation)  
                      for img in img_list] 

    return cv2.hconcat(im_list_resize) 

def most_frequent(lst):
    """
    Function to find the most common element in a list

    :param lst: List with elements
    :return: most common element
    """

    unique, counts = np.unique(lst, return_counts=True)
    index = np.argmax(counts)
    return unique[index]

@function_timer('text_recognition')
def text_recognition(image, label, ocr_obj):
    """
    Calls transformers functions to perform text recognition from image.

    :param image: Image with text.
    :param label: Label with type of data to be parsed
    :return: The extracted text.
    """

    if label in [ 'typed', 'cover' ]:
        pixel_values = ocr_obj.processor_typed(image, return_tensors='pt').pixel_values.to(device)
        generated_ids = ocr_obj.model_typed.generate(pixel_values)
        generated_text = ocr_obj.processor_typed.batch_decode(generated_ids, skip_special_tokens=True)[0]
    else:
        pixel_values = ocr_obj.processor_hw(image, return_tensors='pt').pixel_values.to(device)
        generated_ids = ocr_obj.model_hw.generate(pixel_values)
        generated_text = ocr_obj.processor_hw.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return generated_text

@function_timer('text_detection')
def text_detection(img, ocr_obj):
    """
    Calls detector model to perform text detection on the passed image

    :param img: Image with text.
    :return: List of boxes for the detected text
    """

    results = ocr_obj.detector.predict(source = img, imgsz=768, conf = .07,
                       iou = .12, augment = True, max_det = 1000, 
                       agnostic_nms = True, verbose = False)
    
    return [ box.numpy().boxes.xyxy.tolist() for box in results]

def distinguish_groups(lst):
    """
    Parses returned bounding boxes from objected detected function by text sections
    :param lst: List of bounding boxes
    :return: Sublists containing the bounding boxes grouped by text sections
    """
    sublists = []
    for i in range(0, len(lst)):
        added = False
        if i == 0:
            sublists.append([lst[i]])
            continue
        for j in range(0, len(sublists)):
            if added == True:
                break
            for k in range(0, len(sublists[j])):
                if added == True:
                    break
                if abs(sublists[j][k]['dist_from_origin'] - lst[i]['dist_from_origin']) <= \
                      (sublists[j][k]['height'] + lst[i]['height']) / 2: 
                    sublists[j].append(lst[i])
                    added = True

        if added == False:
            sublists.append([lst[i]])
    return sublists

def distinguish_rows(lst):
    """
    Parses returned bounding boxes from objected detected function by rows
    :param lst: List of bounding boxes
    :return: Sublists containing the bounding boxes grouped by rows
    """
    sublists = []
    if len(lst) == 1:
        sublists.append(lst[0])
    for i in range(0, len(lst)-1):
        if abs(lst[i+1]['distance_y'] - lst[i]['distance_y']) <=  \
           (lst[i]['height'] + lst[i+1]['height']) / 4: 
            if lst[i] not in sublists:
                sublists.append(lst[i])
            sublists.append(lst[i+1])
        else:
            if i == 0:
                sublists.append(lst[i])        
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
    for group in preds[0]:
        top_left_x = group[0]
        top_left_y = group[1] 
        bottom_right_x = group[2]
        bottom_right_y = group[3]
        center_x = (top_left_x + bottom_right_x)/2
        center_y = (top_left_y + bottom_right_y)/2
        dist_from_origin = math.dist([x0,y0], [.2*center_x, 1.8*center_y])
        distance_y = center_y - y0
        distance_x = center_x - x0
        height = abs(top_left_y - bottom_right_y)
        detections.append({
            'top_left_x': top_left_x,
            'top_left_y': top_left_y,
            'bottom_right_x': bottom_right_x,
            'bottom_right_y': bottom_right_y,
            'dist_from_origin': dist_from_origin,
            'distance_y': distance_y,
            'distance_x': distance_x,
            'height': height
            })
        idx = idx + 1
    return detections

@function_timer('text_type_classification')
def text_classification(img, ocr_obj):
    """
    Function to classify text within an image as handwritten or typed

    :param img: Image with text
    :return: Label from resulting classification
    """
    
    label = ocr_obj.writing_classifier(img, verbose = False)

    return 'handwritten' if label[0].probs.top1 == 0 else 'typed'

@function_timer('field_classification')
def text_feature_extractor(value, ocr_obj):
    """
    Function to take measurements from a text string for classification purposes

    :param value: Text string
    :return: A list of values
    """
    value=str(value)
    text_length = len(value)
    words = value.count(" ") + 1
    numbers = sum(c.isdigit() for c in value)
    #letters = sum(c.isalpha() for c in value)
    punctuation = sum((1 if c in string.punctuation else 0) for c in value)
    if text_length == 0:
        num_text_ratio = 0
        punc_text_ratio = 0
    else:
        num_text_ratio = numbers/text_length
        punc_text_ratio = punctuation/text_length
        
    avg_word_length = sum(len(word) for word in value) / words
    
    ext_features = np.reshape(  [text_length, words, num_text_ratio,
                                 avg_word_length, punc_text_ratio] , (1, -1))
    
    output_name = ocr_obj.field_classifier.get_inputs()[0].name
    field = ocr_obj.field_classifier.run(None, {output_name: ext_features.astype(np.float32)})[0]
    return field[0]

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

def crop_label_writer(img_path, crop_labels):
    """
    Function to write handwritten/printed inference results given from its original image

    :param img_path: Path of the image currently in process 
    :param crop_labels: List of inferred labels from crops extracted from the image given by img_path
    :return: Nothing
    """
    new_df = pd.DataFrame(list((zip(crop_labels, [img_path]))))
    outpth = get_out_dir_pth() + "text_type_label_data.csv"
    new_df.to_csv(outpth,
                   mode='a', index=False, header=False)

def write_dataframe(data):
    """
    Function to write extracted data out to a csv

    :param data: Dictionary containing data as {image path: extracted data}
    :param label: Path of directory
    :return: Path of csv containing the data
    """

    print("Writing Out Data to CSV")
    ocr_obj = ocr(load_ocr_models=False, load_field_classifier=True) 
    init_datapath = './extracted_data'
    datapath = "extracted_data/extracted_data.csv"

    if os.path.isfile(datapath):
        os.rename(datapath, str("extracted_data/extracted_data_moved_on_"+datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".csv"))

    label_out_pth = get_out_dir_pth() + "field_label_data.csv"
    label_out_file = open(label_out_pth, 'a')

    os.makedirs(init_datapath, exist_ok=True)
    data = merge_dicts(data)
    output_data = pd.DataFrame(columns=['ID', 'Title', 'SuDoc', 'Publication Year', 
                                        'Path','Error Code','Query Status',
                                        'Sudoc Image', 'Title Image', 
                                        'Image 1 Path', 'Image 2 Path',
                                        'Image 1 Ext', 'Image 2 Ext'])
    
    #output_data = pd.DataFrame(columns=['extract', 'text_type'])
    title_key = sudoc_key = text_type_1_val\
              = text_type_2_val = text_type_1_key\
              = text_type_2_key = pub_year = ""
    for idx, key in enumerate(data):
        text_type = text_feature_extractor(data[key], ocr_obj)
        if text_type == 'title':
            text_type_1_key = 'Title'
            text_type_1_val = data[key].strip()
            title_key = key
        elif text_type == 'sudoc':
            text_type_2_key = 'SuDoc'
            pub_year = pub_year_extraction(data[key])
            #data[key] = data[key] #.replace(" ", "")
            #if data[key][:4].lower() == 'docs':
            #    data[key] = data[key][4:]
            text_type_2_val = data[key].strip()
            sudoc_key = key

        if (idx % 2) == 1:
            img_2_pth = key
            img_2_ext = data[key]
            output_data = pd.concat([output_data, pd.DataFrame(
                [{'ID': int((idx - 1) / 2),
                   text_type_1_key: text_type_1_val, 
                   text_type_2_key: text_type_2_val,
                  'Publication Year': pub_year, 
                  'Sudoc Image': sudoc_key, 
                  'Title Image': title_key,
                  'Image 1 Path': img_1_pth,
                  'Image 2 Path': img_2_pth,
                  'Image 1 Ext': img_1_ext,
                  'Image 2 Ext': img_2_ext
                  }])],
                ignore_index=True)
            
            title_key = sudoc_key = text_type_1_val\
                      = text_type_2_val = text_type_1_key\
                      = text_type_2_key = pub_year = ""

        else:
            img_1_pth = key
            img_1_ext = data[key]

        label_out_file.write( key + "," + str(data[key].replace(",", "")) + "," + text_type + "\n")

    output_data.to_csv(datapath, index=False, mode="a")
    print("Completed Writing Step")
    return datapath