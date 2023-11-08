import os
import logging

LOG_LEVEL = logging.DEBUG
PRESERVE_CONTEXT_ON_EXCEPTION = True
DEBUG = False

SESSION_COOKIE_SAMESITE = 'strict'
SESSION_COOKIE_PATH = '/PDFAnalyzerX'
SESSION_KEY_PREFIX = "hello"
SESSION_COOKIE_NAME = "PDFAnalyzerX_session"
# SESSION_COOKIE_SECURE = True
# REMEMBER_COOKIE_SECURE = True

ROOT_DIR = os.path.abspath(os.path.join(os.path.abspath(__file__), '..', '..'))
LOG_DIR = os.path.join(ROOT_DIR, 'logs')
PDF_DIR = os.path.join(ROOT_DIR, 'pdf_docs')
PDF_IMAGES_PDF = os.path.join(ROOT_DIR, 'pdfimages')
PDF_RESULT_JSON=os.path.join(ROOT_DIR, 'pdfjson')
DATA_DIR = os.path.join(ROOT_DIR, "portal")
STATIC_DIRECTORY = os.path.join(ROOT_DIR, "portal","static")


DIRECTORIES = [LOG_DIR, PDF_DIR]
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', '7z'}
SECRET_KEY = "Kc5c3zTk'-3<&BdL:P92O{_(:-NkY+"



PROPAGATE_EXCEPTIONS = True

CORS_HEADERS = [
    'Content-Type',
    'Authorization'
]

CORS_ORIGIN_WHITELIST = [
    "http://127.0.0.1",
    "https://127.0.0.1",
    "http://127.0.0.1:5000",
    "https://127.0.0.1:5000",
    "http://127.0.0.1:4200",
    "https://127.0.0.1:4200",
    "http://localhost",
    "https://localhost",
    "http://localhost:5000",
    "https://localhost:5000",
    "http://localhost:4200",
    "https://localhost:4200",
]
