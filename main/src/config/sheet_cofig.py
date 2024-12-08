import os
from dotenv import load_dotenv


load_dotenv(dotenv_path="../.env")


service_account_file = os.getenv("SERVICE_ACCOUNT_FILE")
spreadsheet_id = os.getenv("SPREADSHEET_ID")
api_key = os.getenv("API_KEY")

class Config:
    SERVICE_ACCOUNT_FILE = os.getenv("SERVICE_ACCOUNT_FILE", "../../secrets/google_credentials.json")
    SPREADSHEET_ID = os.getenv("SPREADSHEET_ID", "spreadsheet_id")
    DATA_FETCH_INTERVAL = int(os.getenv("DATA_FETCH_INTERVAL", 1800))
    API_PORT = int(os.getenv("API_PORT", 5000))
    RANGE_NAME = os.getenv("RANGE_NAME", "Sheet1!A1:Z1000")

