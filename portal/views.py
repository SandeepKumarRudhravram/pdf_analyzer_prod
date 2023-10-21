import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, send_file, make_response, \
    Response, jsonify
import threading
from . import APP, LOG

bp = Blueprint('view', __name__, url_prefix='/PDFAnalyzerX', template_folder="./templates", static_folder="./static")


@bp.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return 'This Is Pdf Analyzer'