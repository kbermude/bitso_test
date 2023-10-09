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
API_KEY             = 'YOUR_API_KEY' # CHANGE FOR YOUR OWN API KEY FROM STAGE ACCOUNT
API_SECRET          = 'YOUR_API_SECRET' # CHANGE FOR YOUR OWN API SECRET FROM STAGE ACCOUNT

# Function to validate and create directories
async def validate_dir(date,book_name,datadir):
    """
    validates the fixed time directory is already created
    or create if not exists.
    """
    dateiso         = datetime.fromisoformat(date)
    fixed_minutes   = (dateiso.minute // 10) * 10
    datefixed       = dateiso.replace(minute=fixed_minutes)
    dateformatted   = datefixed.strftime("%Y%m%d")
    timeformatted   = datefixed.strftime("%H%M")
    formatted_dir   = datadir + os.sep + book_name + os.sep + dateformatted + os.sep + timeformatted
    os.makedirs(formatted_dir,exist_ok=True)
    return formatted_dir

# Function to make requests to the Bitso API
def order_book_request(book_name):
    """
    Generate the request header and request it using the bitso
    api. 
    """
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
    """
    Format the data from the request to the required format
    and send and alert if the bid-ask spread overpass a
    threshold
    """
    # best bid is the maximum price bidded
    best_bid    = float(max(payload["bids"], key=lambda x: float(x["price"]))["price"])
    # best ask is the minimum price asked for
    best_ask    = float(min(payload["asks"], key=lambda x: float(x["price"]))["price"])
    # obtainthe spread
    spread      = (best_ask-best_bid)*100/best_ask
    if spread>spread_threshold: 
        #This is the alert of the spread, but can be better implemented.
        print (f"ALERT: spread is bigger than {spread_threshold} ")
    updated_at  = payload["updated_at"]
    # format information
    info_line   = f"'{updated_at}',{book_name},{best_bid},{best_ask},{spread}\n"
    return info_line

# Main function to get order book information
async def get_order_book_info(args): 
    """
    asynchronous function to obtain the books orders informations. 
    Implements asynchronous functions and a time sleep to wait
    every seconds for a new request.
    """
    while True:
        # start time of the request
        start_time  = time.time()
        # generate the api request and retrieve data
        data        = order_book_request(args["bookname"])
        if data["success"]:
            # if success then apply transformations to save the information
            updated_at      = data["payload"]["updated_at"]
            # validate the directory is created for the fixed time
            valida_dir_task = asyncio.create_task(validate_dir(updated_at,args["bookname"],args["datadir"]))    
            info_line       = format_data(data["payload"],args["bookname"],args["alertspread"])
            current_dir     = await valida_dir_task
            # write information in the corresponding directory
            with open(current_dir + os.sep + "data.csv",'a') as f:
                f.write(info_line)
        else:
            print(data)
        # wait for 0 or 0-1 seconds depending the time taken
        # in the request
        await asyncio.sleep(max(0, 1 - (time.time() - start_time)))

async def main(args):
    task = asyncio.create_task(get_order_book_info(args))
    await task
    print("Main function is done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Arguments for the process.")
    parser.add_argument("-b", "--bookname", default="btc_mxn", type=str, help="The book name of the orders to checks. example 'btc_mxn'.")
    parser.add_argument("-a","--alertspread", default=1.0, type=float, help="The percentage of bid-ask spread to alert. example 1.0 for 1 percent")
    parser.add_argument("-d","--datadir", default="./data", type=str, help="full path for the data directory.")
    args = vars(parser.parse_args())    
    asyncio.run(main(args))