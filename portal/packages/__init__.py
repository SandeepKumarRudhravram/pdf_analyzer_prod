import fitz
import re
import PyPDF2
from collections import OrderedDict
from portal import LOG,APP
import os
from datetime import datetime, date


def count_images_in_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    image_count = 0
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)
        image_count += len(image_list)

    pdf_document.close()
    return image_count


def get_random_numbers(string_length=5):
    import random
    import string
    return ''.join(random.choice(string.digits) for x in range(string_length))

def count_custom_urls_in_pdf(pdf_file):
    pdf_file = PyPDF2.PdfFileReader(open(pdf_file, "rb"))
    url_count = 0
    for page in pdf_file.pages:
        text = page.extractText()
        urls = re.findall(r'h?%?ps?://\S+', text)
        url_count += len(urls)
    return url_count


def get_final_result(pdf_file):
    count_urls_ = count_custom_urls_in_pdf(pdf_file)
    count_images_ = count_images_in_pdf(pdf_file)
    dict_final_, pdf_document_page_count,counYimg_fr_pdf_ = text_font(pdf_file)
    return count_urls_, counYimg_fr_pdf_, dict_final_, pdf_document_page_count


def save_image(image_data, image_name):
    with open(os.path.join(APP.config["PDF_IMAGES_PDF"], image_name), "wb") as img_file:
        img_file.write(image_data)

def get_font_size(page,counYimg_fr_pdf_):
    temp_dic_ = {}
    tmp_counYimg_fr_pdf_=counYimg_fr_pdf_
    try:
        temp_data_ = page.get_text("dict")["blocks"]
        for data_1 in range(len(temp_data_)):
            temp_dic_[str(data_1)] = {}
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            # print("data_1",temp_data_[data_1])
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

            try:
                text_1 = temp_data_[data_1]["lines"]
            except:
                try:
                    text_1 = []
                    text_12 = temp_data_[data_1]["image"]
                    tmp_counYimg_fr_pdf_ = tmp_counYimg_fr_pdf_ + 1
                    img_index = "original"+ datetime.now().strftime("%d%m%Y%H%M%S") + get_random_numbers(5)+ str(tmp_counYimg_fr_pdf_)
                    image_filename = f"{img_index}.png"
                    save_image(text_12,image_filename)
                except:
                    text_1 = []
            for i in range(len(text_1)):
                line_total_text_ = ''
                line_font_ = []
                line_size = []
                line_diff_text_ = []
                text_2 = text_1[i]["spans"]
                for jk in range(len(text_2)):
                    if str(text_2[jk]["text"]).strip() == "":
                        pass
                    else:
                        if jk == 0:
                            line_total_text_ = str(text_2[jk]["text"]).strip().replace('    ', '')
                        else:
                            line_total_text_ = str(line_total_text_).strip().replace('    ', '') + ' ' + str(
                                text_2[jk]["text"]).strip().replace('    ', '')
                        if str(text_2[jk]["text"]).strip() != '•' or str(text_2[jk]["text"]).strip() != '●':
                            line_diff_text_.append(str(text_2[jk]["text"]).strip().replace('    ', ''))
                            if str(text_2[jk]["font"]) not in line_font_:
                                line_font_.append(str(text_2[jk]["font"]).strip().replace('    ', ''))
                            if str(text_2[jk]["size"]) not in line_size:
                                line_size.append(str(round(text_2[jk]["size"], 2)).strip().replace('    ', ''))
                if line_total_text_ != '':
                    temp_dic_[str(data_1)][str(i)] = {"font_line": line_total_text_, "font_font_type": line_font_,
                                                      "font_sizes": line_size, "font_diff_text": line_diff_text_}
                    line_total_text_ = ''
                    line_font_ = []
                    line_size = []


    except:
        temp_dic_ = {}
    return temp_dic_,tmp_counYimg_fr_pdf_


def text_font(pdf_path):
    pdf_document = fitz.open(pdf_path)
    dict_final_ = {}
    counYimg_fr_pdf_=0
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        font_sizes,counYimg_fr_pdf_ = get_font_size(page,counYimg_fr_pdf_)
        font_sizes = font_sizes
        dict_final_[str(page_number)] = font_sizes

    return dict_final_, pdf_document.page_count,counYimg_fr_pdf_
