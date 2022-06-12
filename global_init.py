# Just some global variable initialisation

import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
PROVIDER_TOKEN = os.getenv("PROVIDER_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
TERMINAL = os.getenv("TERMINAL")
TERM_PASS = os.getenv("TERM_PASS")
PRICE = os.getenv("PRICE")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")
SERVERNAME = os.getenv("SERVERNAME")
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = 'dbkeys.json'
