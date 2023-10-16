import gspread
from google.oauth2.service_account import Credentials
import psutil
import subprocess
import time
import schedule

# Function to get CPU temperature on Linux
def get_cpu_temperature():
    try:
        output = subprocess.check_output("sensors | grep 'Core 0'", shell=True).decode()
        temperature = int(output.split('+')[1].split('.')[0])
        return temperature
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to get GPU temperature using nvidia-smi
def get_gpu_temperature():
    try:
        output = subprocess.check_output("nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader,nounits", shell=True).decode().strip()
        return int(output)
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to get GPU usage using nvidia-smi
def get_gpu_usage():
    try:
        output = subprocess.check_output("nvidia-smi --query-gpu=utilization.gpu --format=csv,noheader,nounits", shell=True).decode().strip()
        return int(output)
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to get system performance data
def get_performance_data():
    cpu_percent = psutil.cpu_percent()
    ram_percent = psutil.virtual_memory().percent
    cpu_temperature = get_cpu_temperature()
    gpu_temperature = get_gpu_temperature()
    gpu_usage = get_gpu_usage()
    return cpu_percent, ram_percent, gpu_usage, cpu_temperature, gpu_temperature

# Initialize Google Sheets API credentials
scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]


credentials = Credentials.from_service_account_file(
    "credentials.json",   # Replace with your credentials file path
    scopes=scopes
)

gc = gspread.authorize(credentials)

# Open the Google Sheets document using the URL
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1YEmZ_O4zJkDEalOIri7QbjI5LKZpkvKji_54ZVr1DLE/edit#gid=0"
spreadsheet = gc.open_by_url(spreadsheet_url)
worksheet = spreadsheet.worksheet("ISC") # Assumes the data is in the first worksheet

# Function to update Google Sheets with data
def update_google_sheets():
    data = get_performance_data()
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    data = [current_time, data[0], data[1], data[2], data[3], data[4]]
    worksheet.append_row(data)

# Schedule the script to run every 10 seconds
schedule.every(10).minutes.do(update_google_sheets)

# Run the scheduling loop
while True:
    schedule.run_pending()
    time.sleep(1)
