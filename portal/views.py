import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, make_response, \
    Response, jsonify
import threading
from . import APP, LOG
from werkzeug.utils import secure_filename
from .security.updated_jwt import jwt_required
from .packages import get_final_result
import time
import random
import string
from datetime import datetime, date
import shutil

bp = Blueprint('view', __name__, url_prefix='/PDFAnalyzerX', template_folder="./templates", static_folder="./static")


@bp.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("pdf_upload.html")


@bp.route('/dashboard/', methods=["GET", "POST"])
def dashboard():
    if request.method == "GET":
        return render_template("index.html")


@bp.route('/get_random_numbers/', methods=["GET", "POST"])
def get_random_numbers(string_length=5):
    random_numbers= ''.join(random.choice(string.digits) for x in range(string_length))
    random_numbers=datetime.now().strftime("%d%m%Y%H%M%S") + random_numbers
    return jsonify({"random_numbers":random_numbers})


def remove_file_after_wait(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


@bp.route("/api_upload_pdf", methods=["GET", 'POST'])
def api_upload_bill():
    if request.method == "POST":
        pdf_docs = APP.config["PDF_DIR"]
        try:
            if 'pdf_file' not in request.files:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf_file is request"})
                resp.status_code = 400
                return resp
            file = request.files['pdf_file']
            if file.filename == '':
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "no pdf selected for uploading"})
                resp.status_code = 400
                return resp
            filename = secure_filename(file.filename)
            if ".pdf" not in filename.lower():
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "please check the file format"})
                resp.status_code = 400
                return resp
            if os.path.exists(os.path.join(pdf_docs)):
                file.save(os.path.join(pdf_docs, filename))
                count_urls_, count_images_, dict_final_, pdf_document_page_count = get_final_result(
                    os.path.join(pdf_docs, filename))
                resp = {"success": True,
                        "data": {"pdf name": str(filename),
                                 "no of images in pdf": str(count_images_),
                                 "no of urls": str(count_urls_),
                                 "no of pages in pdf": str(pdf_document_page_count),
                                 "font": dict_final_},
                        "errors": "None"}
                return resp

            else:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf file directory is not created"})
                resp.status_code = 400
                return resp
        except Exception as e:
            LOG.error(e, exc_info=True)
            resp = jsonify({"success": False,
                            "data": {"pdf name": "None"},
                            "errors": "Something went wrong"})
            resp.status_code = 400
            return resp


@bp.route("/upload_pdf/<string:process_id>", methods=["GET", 'POST'])
def upload_bill(process_id):
    if request.method == "POST":
        pdf_docs = APP.config["PDF_DIR"]
        pdf_docs_json = APP.config["PDF_RESULT_JSON"]
        folder_contents = os.listdir(pdf_docs)
        for item in folder_contents:
            item_path = os.path.join(pdf_docs, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)

        if not os.path.exists(os.path.join(pdf_docs, process_id)):
            os.mkdir(os.path.join(pdf_docs, process_id))
        try:
            if 'pdf_file' not in request.files:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf_file is request"})
                resp.status_code = 400
                return resp
            file = request.files['pdf_file']
            if file.filename == '':
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "no pdf selected for uploading"})
                resp.status_code = 400
                return resp
            filename = secure_filename(file.filename)
            if ".pdf" not in filename.lower():
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "please check the file format"})
                resp.status_code = 400
                return resp
            if os.path.exists(os.path.join(pdf_docs,process_id)):
                file.save(os.path.join(pdf_docs,process_id, filename))
                count_urls_, count_images_, dict_final_, pdf_document_page_count = get_final_result(
                    os.path.join(pdf_docs,process_id, filename),process_id)
                font_size_dict_ = {}
                font_type_dict_ = {}
                count_ = 0
                final_json_={"count_urls_":count_urls_,"dict_final_":dict_final_,"count_images_":count_images_,
                                     "pdf_document_page_count":pdf_document_page_count}

                if not os.path.exists(os.path.join(pdf_docs_json, process_id)):
                    os.mkdir(os.path.join(pdf_docs_json, process_id))
                with open(os.path.join(pdf_docs_json, process_id, "result.json"), "w") as file:
                    json.dump(final_json_, file)
                    file.close()
                for i in dict_final_:
                    for j in dict_final_[i]:
                        for k in dict_final_[i][j]:
                            # print(dict_final_[i][j][k]['font_line'])
                            if str(dict_final_[i][j][k]['font_line']).strip() == '' or dict_final_[i][j][k]['font_line'] == '':
                                pass
                            else:
                                count_ = count_ + 1
                                for fnt in dict_final_[i][j][k]['font_font_type']:
                                    font_ = fnt
                                    font_type_dict_[font_] = font_type_dict_.get(font_, 0) + 1

                                for fntsz in dict_final_[i][j][k]['font_sizes']:
                                    font_size = fntsz
                                    font_size_dict_[font_size] = font_size_dict_.get(font_size, 0) + 1
                top_4_fonts_types = dict(sorted(font_type_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                total_counts_types = sum(font_type_dict_.values())
                percentage_dict_types = {font: round((count / total_counts_types) * 100, 2) for font, count in
                                         top_4_fonts_types.items()}
                length_of_percentage_dict_types = len(percentage_dict_types)
                # for font, percentage in percentage_dict_types.items():
                #     print("Percentage of {} compared to all fonts: {:.2f}%".format(font, percentage))

                top_4_font_size_ = dict(sorted(font_size_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                total_counts_size = sum(font_size_dict_.values())
                percentage_dict_size = {font: round((count / total_counts_size) * 100, 2) for font, count in
                                        top_4_font_size_.items()}
                length_of_percentage_dict_size = len(percentage_dict_size)
                # for size, percentage in percentage_dict_size.items():
                #     print("Percentage of {} compared to all sizes: {:.2f}%".format(size, percentage))

                # resp = {"success": True,
                #         "data": {"pdf name": str(filename),
                #                  "no of images in pdf": str(count_images_),
                #                  "no of urls": str(count_urls_),
                #                  "no of pages in pdf": str(pdf_document_page_count),
                #                  "font": dict_final_},
                #         "errors": "None"}
                # return resp
                print('percentage_dict_size', percentage_dict_size)
                return render_template("index.html", top_4_font_size_=top_4_font_size_,
                                       top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
                                       total_counts_types=total_counts_types, count_urls_=count_urls_,
                                       count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
                                       percentage_dict_types=percentage_dict_types,
                                       percentage_dict_size=percentage_dict_size,
                                       length_of_percentage_dict_types=length_of_percentage_dict_types,
                                       length_of_percentage_dict_size=length_of_percentage_dict_size,
                                       count_=count_)
            else:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "pdf file directory is not created"})
                resp.status_code = 400
                return resp
        except Exception as e:
            LOG.error(e, exc_info=True)
            resp = jsonify({"success": False,
                            "data": {"pdf name": "None"},
                            "errors": "Something went wrong"})
            resp.status_code = 400
            return resp
    if request.method == "GET":
        pdf_docs_json = APP.config["PDF_RESULT_JSON"]
        if os.path.exists(os.path.join(pdf_docs_json, process_id)):
            if os.path.exists(os.path.join(pdf_docs_json, process_id,"result.json")):
                with open(os.path.join(pdf_docs_json, process_id, "result.json"), "r") as file:
                    finl_dd = json.load(file)
                    file.close()

                count_urls_=finl_dd['count_urls_']
                count_images_ = finl_dd['count_images_']
                dict_final_ = finl_dd['dict_final_']
                pdf_document_page_count = finl_dd['pdf_document_page_count']

                font_size_dict_ = {}
                font_type_dict_ = {}
                count_ = 0
                final_json_ = {"count_urls_": count_urls_, "dict_final_": dict_final_, "count_images_": count_images_,
                               "pdf_document_page_count": pdf_document_page_count}
                pdf_docs_json = APP.config["PDF_RESULT_JSON"]
                if not os.path.exists(os.path.join(pdf_docs_json, process_id)):
                    os.mkdir(os.path.join(pdf_docs_json, process_id))
                with open(os.path.join(pdf_docs_json, process_id, "result.json"), "w") as file:
                    json.dump(final_json_, file)
                    file.close()
                for i in dict_final_:
                    for j in dict_final_[i]:
                        for k in dict_final_[i][j]:
                            # print(dict_final_[i][j][k]['font_line'])
                            if str(dict_final_[i][j][k]['font_line']).strip() == '' or dict_final_[i][j][k]['font_line'] == '':
                                pass
                            else:
                                count_ = count_ + 1
                                for fnt in dict_final_[i][j][k]['font_font_type']:
                                    font_ = fnt
                                    font_type_dict_[font_] = font_type_dict_.get(font_, 0) + 1

                                for fntsz in dict_final_[i][j][k]['font_sizes']:
                                    font_size = fntsz
                                    font_size_dict_[font_size] = font_size_dict_.get(font_size, 0) + 1
                top_4_fonts_types = dict(sorted(font_type_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                total_counts_types = sum(font_type_dict_.values())
                percentage_dict_types = {font: round((count / total_counts_types) * 100, 2) for font, count in
                                         top_4_fonts_types.items()}
                length_of_percentage_dict_types = len(percentage_dict_types)

                top_4_font_size_ = dict(sorted(font_size_dict_.items(), key=lambda x: x[1], reverse=True)[:5])
                total_counts_size = sum(font_size_dict_.values())
                percentage_dict_size = {font: round((count / total_counts_size) * 100, 2) for font, count in
                                        top_4_font_size_.items()}
                length_of_percentage_dict_size = len(percentage_dict_size)
                print('percentage_dict_size', percentage_dict_size)
                return render_template("index.html", top_4_font_size_=top_4_font_size_,
                                       top_4_fonts_types=top_4_fonts_types, total_counts_size=total_counts_size,
                                       total_counts_types=total_counts_types, count_urls_=count_urls_,
                                       count_images_=count_images_, pdf_document_page_count=pdf_document_page_count,
                                       percentage_dict_types=percentage_dict_types,
                                       percentage_dict_size=percentage_dict_size,
                                       length_of_percentage_dict_types=length_of_percentage_dict_types,
                                       length_of_percentage_dict_size=length_of_percentage_dict_size,
                                       count_=count_)
            else:
                resp = jsonify({"success": False,
                                "data": {"pdf name": "None"},
                                "errors": "Result Not Found"})
                resp.status_code = 400
                return resp
        else:
            resp = jsonify({"success": False,
                            "data": {"pdf name": "None"},
                            "errors": "Data Is Not Available"})
            resp.status_code = 400
            return resp

