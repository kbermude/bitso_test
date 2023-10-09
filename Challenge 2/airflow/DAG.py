from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import create_engine

# Configure the connection to PostgreSQL
engine = create_engine('postgresql://username:password@localhost:5432/bitso_db')

# Extract fuction
def extract_data():
    #Load the data from CSV files
    data_deposits = pd.read_csv('/data/deposit_sample_data.csv')
    data_withdrawals = pd.read_csv('/data/withdrawals_sample_data.csv')
    data_events = pd.read_csv('/data/event_sample_data.csv')
    data_users = pd.read_csv('/data/user_id_sample_data.csv')
    return data_deposits, data_withdrawals, data_events, data_users

# Transform function
def transform_data(*args, **kwargs):
    data_deposits, data_withdrawals, data_events, data_users = args
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
    return transactions, data_events, data_users

# Load data to PostgreSQL
def load_data(*args, **kwargs):
    transactions, data_events, data_users = args
    transactions.to_sql('transactions', engine, if_exists='replace', index=False, schema='public')
    data_events.to_sql('events', engine, if_exists='replace', index=False, schema='public')
    data_users.to_sql('users', engine, if_exists='replace', index=False, schema='public')

# Define the DAG
default_args = {
    'owner': 'your_name',
    'depends_on_past': False,
    'start_date': datetime(2023, 10, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'my_etl_workflow',
    default_args=default_args,
    schedule_interval=timedelta(days=1),  # Daily execution
    catchup=False,
)

# Task of ETL
extract_task = PythonOperator(
    task_id='extract_data',
    python_callable=extract_data,
    provide_context=True,
    dag=dag,
)

transform_task = PythonOperator(
    task_id='transform_data',
    python_callable=transform_data,
    provide_context=True,
    dag=dag,
)

load_task = PythonOperator(
    task_id='load_data',
    python_callable=load_data,
    provide_context=True,
    dag=dag,
)

# Sequence of tasks (ETL)
extract_task >> transform_task >> load_task
