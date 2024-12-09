import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="../.env")


service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
spreadsheet_id = os.getenv("SPREADSHEET_ID")
api_key = os.getenv("API_KEY")

class Config:
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE")
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
    RANGE_NAME = os.getenv("RANGE_NAME")

