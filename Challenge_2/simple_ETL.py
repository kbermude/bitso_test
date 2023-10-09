import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Extract data from CSV files
data_deposits = pd.read_csv('./data/deposit_sample_data.csv')
data_withdrawals = pd.read_csv('./data/withdrawals_sample_data.csv')
data_events = pd.read_csv('./data/event_sample_data.csv')
data_users = pd.read_csv('./data/user_id_sample_data.csv')

# Transform data 
data_deposits['amount'] = data_deposits['amount'].apply(lambda x: max(0, x))
data_withdrawals['amount'] = data_withdrawals['amount'].apply(lambda x: max(0, x))
data_events['event_timestamp'] = pd.to_datetime(data_events['event_timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
data_deposits['event_timestamp'] = pd.to_datetime(data_deposits['event_timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
data_withdrawals['event_timestamp'] = pd.to_datetime(data_withdrawals['event_timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
data_deposits['interface']='web' #by default
data_deposits['type']='deposits'
data_withdrawals['type']='withdrawals' 
transactions=pd.concat([data_deposits,data_withdrawals], ignore_index=True, sort=False)

#Load data
data_users.to_csv('./output_data/users.csv',index=False, encoding='utf-8')
data_events.to_csv('./output_data/events.csv',index=False, encoding='utf-8')
transactions.to_csv('./output_data/transactions.csv',index=False, encoding='utf-8')