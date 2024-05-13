import os
import multiprocessing
from ocr.ocr_utils import *
import asyncio

### Global to facilitate progress bar for parallel processing of images
count = 0

def img_recognition(img_dir, p_in):
    """
    Function to perform the bulk of the text recognition tasks

    :param img_dir: list of image paths
    :param total_images: Number of images to be processed
    :param process_signal: Signal for GUI process bar
    :return: Dictionary with extracted data as {image path: extracted text}
    """

    extractions = {}
    bar_img = cv2.imread("barsepimg.png")
    for img_path in img_dir:
        print("Beggining extraction  on image: ", img_path)

        ext_txt = ""

        img = cv2.imread(img_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pred = text_detection(img_path, ocr_obj)
        pred = get_distance(pred)
        pred = sorted(pred, key=lambda x:x['distance_y'])
        pred = list(distinguish_groups(pred))
        for group in pred:
            group = list(distinguish_rows(group))
            image_crops = []
            crop_labels = []
            for row in group:
                row = sorted(row, key=lambda x:x['distance_x'])
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

                    image_crops.append(cropped_img)
                    image_crops.append(bar_img)
                    crop_labels.append(text_classification(cropped_img, ocr_obj))

            label = most_frequent(crop_labels)

            cropped_img = hconcat_resize(image_crops)

            if label == 'typed':
                ext_txt = ext_txt + " " + text_recognition(
                    cropped_img,
                    label, 
                    ocr_obj
                )
            elif label == 'handwritten':
                ext_txt = ext_txt + " " + text_recognition(
                    cropped_img,
                    label,
                    ocr_obj
                )

            crop_label_writer(img_path, crop_labels)

            #ext_txt = ''.join('' if c in punctuation else c for c in ext_txt)
            #ext_txt = ' '.join(ext_txt.split())

        extractions[img_path] = ext_txt + " "
        print("Completed extraction on image: ", img_path)
        p_in.send(1)

    p_in.send("done")
    return extractions

async def update_prog_bar(prog_bar_func, total_images, p_out):
    sum = 0
    msg_comp_ct = 0
    while True:
        msg = p_out.recv()
        if msg == 1:
            sum += msg
        else:
            msg_comp_ct += 1
        #print(sum, total_images)
        prog_bar_func(sum/total_images)
        if msg_comp_ct == 2:
            break

@function_timer('main_process')
def main(path, update_progress_bar):
    print("Beginning Script")
    #dirs = ['./tests/test_img_dir']

    p_out, p_in = multiprocessing.Pipe()

    processed_file_count = 0
    with multiprocessing.Pool(processes=2) as pool:
        extracted_data = []
        collected_data_proc_1 = []
        collected_data_proc_2 = []
        img_dir = os.listdir(path)
        img_dir = [os.path.join(path, img) for img in img_dir]

        validation = dir_validation(img_dir)

        if validation == 201:
            print("Selected data has odd number of images")
            return

        elif validation == 202:
            print("Selected data has an invalid file type")
            return

        img_dir.sort(key=lambda x: os.path.getctime(x))

        total_images = len(img_dir)
        processed_file_count += total_images
        #halfpoint = False
        hp = total_images//2
        collected_data_proc_1.append(pool.apply_async(img_recognition,
                                                      (img_dir[:hp],
                                                       p_in)))
        collected_data_proc_2.append(pool.apply_async(img_recognition,
                                                      (img_dir[hp:],
                                                       p_in)))

        asyncio.run(update_prog_bar(update_progress_bar, total_images, p_out))

        for obj in range(len(collected_data_proc_1)):
            extracted_data.append(collected_data_proc_1[obj].get())

        for obj in range(len(collected_data_proc_2)):
            extracted_data.append(collected_data_proc_2[obj].get())

        #if (idx > int(len(img_dir)/2)) and halfpoint == False:
        #    halfpoint = True
        #    write_dataframe(extracted_data)

        ext_pth = write_dataframe(extracted_data)
        pool.close()
        pool.join()
    
    print("Image Processing Completed")
    return processed_file_count, ext_pth


if multiprocessing.current_process().name != 'MainProcess':
    ocr_obj = ocr(load_ocr_models=True, load_field_classifier=False) 

#if __name__ == '__main__':
#    main()