import argparse
import requests
import pandas as pd
import requests
import hashlib
import hmac
import time
import asyncio
import os
from datetime import datetime

# Bitso API Configuration
BITSO_API_URL       = 'https://api.bitso.com/v3/order_book'
DATA_DIR            = './data'  
API_KEY             = 'YOUR_API_KEY'
API_SECRET          = 'YOUR_API_SECRET'
threshold            = [1.0, 0.5, 0.1] # Spread Alert Thresholds (percentage) to use as arguments in the main fuction.

# Function to validate and create directories
async def validate_dir(date,book_name):
    dateiso         = datetime.fromisoformat(date)
    fixed_minutes   = (dateiso.minute // 10) * 10
    datefixed       = dateiso.replace(minute=fixed_minutes)
    dateformatted   = datefixed.strftime("%Y%m%d")
    timeformatted   = datefixed.strftime("%H%M")
    formatted_dir   = DATA_DIR + os.sep + book_name + os.sep + dateformatted + os.sep + timeformatted
    os.makedirs(formatted_dir,exist_ok=True)
    return formatted_dir

# Function to make requests to the Bitso API
def generate_request(book_name):
    url_prefix          = "https://sandbox.bitso.com"
    RequestPath         = f"/api/v3/order_book/?book={book_name}"
    url                 = f"{url_prefix}{RequestPath}"
    secs                = str(int(time.time()))
    dnonce              = secs+"000"
    HTTPmethod          = "GET"
    JSONPayload         = ""
    signature_message   = f"{dnonce}{HTTPmethod}{RequestPath}{JSONPayload}".encode('utf-8')
    signature           = hmac.new(API_SECRET.encode('utf-8'), signature_message, hashlib.sha256).hexdigest()
    auth_header         = f"Bitso {API_KEY}:{dnonce}:{signature}"
    response            = requests.get(url, headers={"Authorization": auth_header}).json()
    return response

# Function to format order book data
def format_data(payload,book_name,spread_threshold):
    best_bid    = float(max(payload["bids"], key=lambda x: float(x["price"]))["price"])
    best_ask    = float(min(payload["asks"], key=lambda x: float(x["price"]))["price"])
    spread      = (best_ask-best_bid)*100/best_ask
    if spread>spread_threshold: 
        #This is the alert of the spread, but can be better implemented.
        print (f"ALERT: spread is bigger than {spread_threshold} ")
    updated_at  = payload["updated_at"]
    info_line   = f"'{updated_at}',{book_name},{best_bid},{best_ask},{spread}\n"
    return info_line

# Main function to get order book information
async def get_book_info(book_name, spread_threshold): 
    while True:
        start_time  = time.time()
        data        = generate_request(book_name)
        if data["success"]:
            updated_at      = data["payload"]["updated_at"]
            valida_dir_task = asyncio.create_task(validate_dir(updated_at,book_name))    
            info_line       = format_data(data["payload"],book_name,spread_threshold)
            current_dir     = await valida_dir_task
            with open(current_dir + os.sep + "data.csv",'a') as f:
                f.write(info_line)
        else:
            print(data)
        await asyncio.sleep(max(0, 1 - (time.time() - start_time)))

# Main execution function
async def main(args):
    task = asyncio.create_task(get_book_info(args["bookname"],args["alertspread"]))
    await task
    print("Main function is done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments for the process.")
    parser.add_argument("-b", "--bookname", default="btc_mxn", type=str, help="The book name of the orders to checks. example 'btc_mxn'.")
    parser.add_argument("-a","--alertspread", default=1.0, type=float, help="The percentage of bid-ask spread to alert. example 1.0 for 1 percent")
    args = vars(parser.parse_args())    
    asyncio.run(main(args))