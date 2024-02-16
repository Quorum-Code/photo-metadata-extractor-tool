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
# from multiprocessing import cpu_count
from gc import collect

from scipy.ndimage import maximum_filter
from scipy.signal import find_peaks


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
    del pixel_values, generated_ids, processor, image
    collect()
    return generated_text


def distinguish_rows(lst, thresh=50):
    """
    Parses returned bounding boxes from objected detected function by rows
    :param lst: List of bounding boxes
    :param thresh: Max distance between bounding boxes
    :return: Sublists containing the bounding boxes grouped by row
    """

    sublists = []
    for i in range(0, len(lst) - 1):
        if lst[i + 1]['distance_y'] - lst[i]['distance_y'] <= thresh:
            if lst[i] not in sublists:
                sublists.append(lst[i])
            sublists.append(lst[i + 1])
        else:
            if i == 0:
                sublists.append(lst[i])
            yield sublists
            sublists = [lst[i + 1]]
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
            center_x = (top_left_x + bottom_right_x) / 2
            center_y = (top_left_y + bottom_right_y) / 2
            dist_from_origin = math.dist([x0, y0], [center_x, center_y])
            distance_y = center_y - y0
            detections.append({
                'text': group[0],
                'top_left_x': top_left_x,
                'top_left_y': top_left_y,
                'bottom_right_x': bottom_right_x,
                'bottom_right_y': bottom_right_y,
                'dist_from_origin': dist_from_origin,
                'distance_y': distance_y})
            idx = idx + 1
    return detections


def pub_year_extraction(data):
    """
    Parse extracted text for phrase that could be a year

    :param data: Text string to be parsed for a value representing a year
    :return: Value to be used as year
    """
    pub_year = ""
    for phrase in data.split():
        if phrase.isdigit() and (1600 <= int(phrase) <= datetime.datetime.today().year + 1):
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

    label_classifier = pickle.load(open("classifiers/rf_model.sav", 'rb'))
    # label_classifier = pickle.load(open("MLModelsList/classifiers/rf_model.sav", 'rb'))
    curr_time = datetime.datetime.now()
    init_datapath = './extracted_data'
    datapath = "extracted_data/extracted_data.csv"
    os.makedirs(init_datapath, exist_ok=True)
    data = merge_dicts(data)
    output_data = pd.DataFrame(
        columns=['ID', 'Title', 'SuDoc', 'Publication Year', 'Path', 'Error Code', 'Query Status', 'Sudoc Image',
                 'Title Image'])
    title_key = sudoc_key = text_type_1_val = text_type_2_val = text_type_1_key = text_type_2_key = pub_year = ""
    for idx, key in enumerate(data):
        label_pred = np.reshape(text_feature_extractor(data[key]), (1, -1))
        text_type = label_classifier.predict(label_pred)[0]
        if text_type == 'title':
            text_type_1_key = 'Title'
            text_type_1_val = data[key]
            title_key = key
        elif text_type == 'sudoc':
            text_type_2_key = 'SuDoc'
            pub_year = pub_year_extraction(data[key])
            data[key] = data[key].replace(" ", "")
            if data[key][:4].lower() == 'docs':
                data[key] = data[key][4:]
            text_type_2_val = data[key]
            sudoc_key = key
        if (idx % 2) == 1:
            output_data = pd.concat([output_data, pd.DataFrame(
                [{'ID': int((idx - 1) / 2), text_type_1_key: text_type_1_val, text_type_2_key: text_type_2_val,
                  'Publication Year': pub_year, 'Sudoc Image': sudoc_key, 'Title Image': title_key}])],
                                    ignore_index=True)
            title_key = sudoc_key = text_type_1_val = text_type_2_val = text_type_1_key = text_type_2_key = pub_year = ""
    # print(output_data)
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
    img_num = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    th, th_img = cv2.threshold(img_num, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    img_height, img_width = np.array(img_num).shape
    counts, bins = np.histogram(img_num, range(257))
    peaks = find_peaks(counts)
    maxima_count = len(peaks[0])
    c = 255 / (np.log(1 + np.max(img_num)))
    log_transformed = c * np.log(1 + img_num)
    log_transformed = np.array(log_transformed, dtype=np.uint8)
    log_transformed_mean = log_transformed.mean()
    log_transformed_var = log_transformed.var()
    log_transformed_std = log_transformed.std()
    max_int = img_num.max()
    min_int = img_num.min()
    quart_range = (max_int - min_int) / 4
    upper_quart_count = np.count_nonzero(img_num >= (max_int - quart_range))
    upper_quart_perc = (upper_quart_count / (img_width * img_height) if (img_width * img_height) > 0 else 1) * 100
    lower_quart_count = np.count_nonzero(img_num <= (min_int + quart_range))
    lower_quart_perc = (lower_quart_count / (img_width * img_height) if (img_width * img_height) > 0 else 1) * 100

    ext_features = np.reshape([log_transformed_mean, th,
                               maxima_count, upper_quart_perc, lower_quart_perc,
                               log_transformed_std, log_transformed_var], (1, -1))

    label = classifier.predict(ext_features)
    del img_num, th_img, img
    return label


def load_models():
    """
    Function to load text detection, text recognition, and text classification models

    :return: Text detection, text recognition, and classification models
    """
    print("Loading Models")
    writing_classifier = pickle.load(open("classifiers/hgbc_model.sav", 'rb'))
    # writing_classifier = pickle.load(open("classifiers/text_classifier.sav", 'rb'))
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
    # recognizer.model.load_weights('MLModelsList/curr_recognizer.h5')
    pipeline = keras_ocr.pipeline.Pipeline(detector=detector, recognizer=recognizer)
    print("Loading trocr models")
    processor_typed = TrOCRProcessor.from_pretrained('./MLModelsList/ocr_models/typed_ocr_models')
    model_typed = VisionEncoderDecoderModel.from_pretrained(
        './MLModelsList/ocr_models/typed_ocr_models'
    ).to(device)
    processor_hw = TrOCRProcessor.from_pretrained('./MLModelsList/ocr_models/hw_ocr_models')
    model_hw = VisionEncoderDecoderModel.from_pretrained(
        './MLModelsList/ocr_models/hw_ocr_models'
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
        num_text_ratio = numbers / text_length
    avg_word_length = sum(len(word) for word in value) / words
    return [text_length, words, num_text_ratio, avg_word_length]


img_read_flag = True


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
    global count, img_read_flag
    extractions = {}
    ext_txt = ""
    print("Beggining extraction  on image: ", img_path)
    while img_read_flag == False:
        pass
    img_read_flag = False
    img = keras_ocr.tools.read(img_path)
    pred = pipeline.recognize([img])
    img_read_flag = True
    del pipeline
    collect()
    pred = get_distance(pred)
    pred = list(distinguish_rows(pred))
    for row in pred:
        row = sorted(row, key=lambda x: x['dist_from_origin'])
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
            if label == 'typed':
                ext_txt = ext_txt + " " + ocr(
                    cropped_img,
                    processor=processor_typed,
                    model=model_typed
                )
            elif label == 'handwritten':
                ext_txt = ext_txt + " " + ocr(
                    cropped_img,
                    processor=processor_hw,
                    model=model_hw
                )
            ext_txt = ''.join('' if c in punctuation else c for c in ext_txt)
            ext_txt = ' '.join(ext_txt.split())
            del cropped_img
            collect()
    extractions[img_path] = ext_txt
    print("Completed extraction on image: ", img_path)
    count += 1
    progress_signal.emit(count / total_images)
    del img, processor_hw, model_hw, processor_typed, model_typed
    collect()
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
    # num_workers = 2 # if cpu_count() > 5 else 1
    exe = ThreadPoolExecutor(2)
    start_time = time.time()
    collected_data = []
    halfpoint = False
    for idx in range(0, len(img_dir), 2):
        for worker in range(0, 2):
            collected_data.append(
                exe.submit(img_recognition, img_dir[(idx + worker)], processor_typed, model_typed, processor_hw,
                           model_hw, writing_classifier,
                           pipeline, total_images, progress_signal))

        for obj in range(len(collected_data)):
            extracted_data.append(collected_data[obj].result())
        if (idx > int(len(img_dir) / 2)) and halfpoint == False:
            halfpoint = True
            write_dataframe(extracted_data,
                            os.path.basename(os.path.normpath("extracted_data/temp_extracted_data.csv")))
        collected_data = []
    load_time = time.time() - start_time
    time_file.write("Total Extraction Time: " + str(load_time) + "\n")
    return extracted_data


def dir_validation(dir):
    """
    Function to check if the passed directory has the right format

    :param dir: Directory to check
    :return: error code
    """

    supported_file_types = ['bmp', 'dib', 'jpeg', 'jpg', 'jpe', 'jp2', 'png', 'webp', 'avif',
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


def read_data(path, progress_signal):
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

    dir_check = dir_validation(img_dir)

    if dir_check == 201:
        print(201)
        return 201
    elif dir_check == 202:
        print(202)
        return 202

    img_dir = [os.path.join(path, img) for img in img_dir]

    img_dir.sort(key=lambda x: os.path.getctime(x))

    total_images = len(img_dir)

    extracted_data = par_img_proc_caller(img_dir, progress_signal, total_images)

    datapath = write_dataframe(extracted_data, os.path.basename(os.path.normpath(path)))

    print("finished image reading lines")

    return (datapath)
