from jiwer import cer
from string import punctuation
import pandas as pd
import numpy as np
from ocr_utils import *

import warnings
warnings.filterwarnings("ignore", category=FutureWarning) 

pd.set_option('display.max_rows', 1000); pd.set_option('display.max_columns', 1000); pd.set_option('display.width', 1000)

class ocr_test():
    """
    Class to collect and write reported data from latest image extraction run to a csv

    """

    def __init__(self):
        self.data = ''
        self.recognition_cer_base = 0
        self.recognition_cer_no_pct = 0
        self.recognition_cer_hw_base = 0
        self.recognition_cer_hw_no_pct = 0        
        self.recognition_cer_typed_base = 0
        self.recognition_cer_typed_no_pct = 0 
        self.text_type_acc = 0
        self.field_label_acc = 0
        self.output_file_pth = None
        self.text_type_pth = None
        self.field_label_pth = None
        self.true_data_pth = None
        self.extracted_data = None
        self.text_type_data = None
        self.field_label_data = None
        self.true_data = None
        self.get_data()
        self.get_text_type_acc()
        self.get_field_acc()
        self.get_cer()
        self.write_acc_scores()

    def get_data(self):
        """
        Function to read in reported and true data from the latest image extraction run

        :return: Nothing
        """

        data_dir = get_out_dir_pth()

        if self.output_file_pth == None:
            self.output_file_pth = data_dir + 'run_summary.csv' 
        if self.text_type_pth == None:
            self.text_type_pth = data_dir + 'text_type_label_data.csv'
        if self.field_label_pth == None:
            self.field_label_pth = data_dir + 'field_label_data.csv'
        if self.true_data_pth == None:
            self.true_data_pth = './tests/labels.csv'

        self.data = pd.read_csv(self.output_file_pth)
        self.field_label_data = pd.read_csv(self.field_label_pth, header = None)
        self.true_data = pd.read_csv(self.true_data_pth, header = None)
        self.text_type_data = pd.read_csv(self.text_type_pth, header = None)
        self.true_data.columns = ['path', 'tt', 'field', 'ext_true']

    def get_cer(self):
        """
        Function to collect the necessary data and compute the character error rate (CER) given the complete run and a 
        few modifications to the collected data for reporting purposes

        :return: Nothing
        """

        conc_dt = pd.merge(self.field_label_data, self.true_data, how = 'left', on = 'path')
        conc_dt['ext'] = conc_dt['ext'].apply(lambda x: x.strip())
        conc_dt['ext_no_pct'] = conc_dt['ext'].apply(lambda x: remove_punctuation(x))
        conc_dt['ext_true_no_pct'] = conc_dt['ext_true'].apply(lambda x: remove_punctuation(x))
        conc_dt = pd.merge(conc_dt, self.text_type_data[['path', 'max_label']], how = 'left', on = 'path')
        hw_rows = conc_dt.loc[conc_dt['max_label'] == 'hw']        
        typed_rows = conc_dt.loc[conc_dt['max_label'] == 'typed']
        self.recognition_cer_base = cer(conc_dt['ext_true'].tolist(), conc_dt['ext'].tolist())
        self.recognition_cer_no_pct = cer(conc_dt['ext_true_no_pct'].tolist(), conc_dt['ext_no_pct'].tolist())
        self.recognition_cer_hw_base = cer(hw_rows['ext_true'].tolist(), hw_rows['ext'].tolist())
        self.recognition_cer_hw_no_pct = cer(hw_rows['ext_true_no_pct'].tolist(), hw_rows['ext_no_pct'].tolist())        
        self.recognition_cer_typed_base = cer(typed_rows['ext_true'].tolist(), typed_rows['ext'].tolist())
        self.recognition_cer_typed_no_pct = cer(typed_rows['ext_true_no_pct'].tolist(), typed_rows['ext_no_pct'].tolist())

    def get_text_type_acc(self):
        """
        Function to collect the necessary data and compute the handwritten/printed classification accuracy

        :return: Nothing
        """

        self.text_type_data.columns = ['tt', 'path']
        self.text_type_data['path'] = self.text_type_data['path'].apply(lambda x: x.replace('\\', "/"))
        self.text_type_data['tt'] = self.text_type_data['tt'].apply(lambda x: x.replace('handwritten', "hw"))
        self.text_type_data['path'] = self.text_type_data['path'].apply(lambda x: x.lower())
        self.text_type_data = self.text_type_data.groupby(['path', 'tt']).size().unstack(fill_value = 0)
        self.text_type_data = self.text_type_data.reset_index()
        self.text_type_data['max_label'] = self.text_type_data[['hw', 'typed']].idxmax(axis=1)
        conc_dt = pd.merge(self.text_type_data, self.true_data[['path', 'tt']], how = 'left', on = 'path')
        self.text_type_acc = len(np.where(conc_dt['max_label'] == conc_dt['tt'])[0]) / len(conc_dt['path'])

    def get_field_acc(self):
        """
        Function to collect the necessary data and compute the field classification accuracy

        :return: Nothing
        """

        self.field_label_data.columns = ['path', 'ext', 'field']
        self.field_label_data['path'] = self.field_label_data['path'].apply(lambda x: x.replace('\\', "/"))
        self.field_label_data['path'] = self.field_label_data['path'].apply(lambda x: x.lower())
        conc_dt = pd.merge(self.field_label_data, self.true_data[['path', 'field']], how = 'left', on = 'path')
        self.field_label_acc = len(np.where(conc_dt['field_x'] == conc_dt['field_y'])[0]) / len(conc_dt['path'])

    def write_acc_scores(self):
        """
        Function to collect the above computed data and write it out to a csv

        :return: Nothing
        """

        self.data['cer_base'] = self.recognition_cer_base
        self.data['cer_no_pct'] = self.recognition_cer_no_pct
        self.data['cer_hw_base'] = self.recognition_cer_hw_base
        self.data['cer_hw_no_pct'] = self.recognition_cer_hw_no_pct
        self.data['cer_typed_base'] = self.recognition_cer_typed_base
        self.data['cer_typed_no_pct'] = self.recognition_cer_typed_no_pct
        self.data['text_type_acc'] = self.text_type_acc
        self.data['field_label_acc'] = self.field_label_acc
        self.data.to_csv(self.output_file_pth, index = False)

def remove_punctuation(text):
    """
        Function to remove punctuation from a given string

        :param text: String to process
        :return: String without any punctuation
    """
    
    return ''.join('' if c in punctuation else c for c in text)

if __name__ == '__main__':
    ocr_test()