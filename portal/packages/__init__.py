import fitz
import re
import PyPDF2
from collections import OrderedDict


def count_images_in_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    image_count = 0
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        image_list = page.get_images(full=True)
        image_count += len(image_list)

    pdf_document.close()
    return image_count


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
    dict_final_, pdf_document_page_count = text_font(pdf_file)
    return count_urls_, count_images_, dict_final_, pdf_document_page_count


def get_font_size(page):
    temp_dic_ = {}
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
                            line_total_text_ = str(text_2[jk]["text"]).strip().replace('    ','')
                        else:
                            line_total_text_ = str(line_total_text_).strip().replace('    ','') + ' ' + str(text_2[jk]["text"]).strip().replace('    ','')
                        if str(text_2[jk]["text"]).strip() != '•' or str(text_2[jk]["text"]).strip() != '●':
                            line_diff_text_.append(str(text_2[jk]["text"]).strip().replace('    ',''))
                            if str(text_2[jk]["font"]) not in line_font_:
                                line_font_.append(str(text_2[jk]["font"]).strip().replace('    ',''))
                            if str(text_2[jk]["size"]) not in line_size:
                                line_size.append(str(text_2[jk]["size"]).strip().replace('    ',''))
                if line_total_text_ != '':
                    temp_dic_[str(data_1)][str(i)] = {"font_line": line_total_text_, "font_font_type": line_font_,
                                                      "font_sizes": line_size, "font_diff_text": line_diff_text_}
                    line_total_text_ = ''
                    line_font_ = []
                    line_size = []
    except:
        temp_dic_ = {}
    return temp_dic_


def text_font(pdf_path):
    pdf_document = fitz.open(pdf_path)
    dict_final_ = {}
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        font_sizes = get_font_size(page)
        font_sizes = font_sizes
        dict_final_[str(page_number)] = font_sizes

    return dict_final_, pdf_document.page_count
