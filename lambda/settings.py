# settings.py
import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
AWS_LAMBDA_FUNCTION_NAME = os.environ.get("AWS_LAMBDA_FUNCTION_NAME")
if AWS_LAMBDA_FUNCTION_NAME is None:
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_HOST = os.environ.get("AWS_HOST")
    AWS_REGION = os.environ.get("AWS_REGION")
