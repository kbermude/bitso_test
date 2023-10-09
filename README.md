# Bitso Test
This is the test for Data Engineer position, which consists in two challenges describe below.

# Challenge 1

Bitso Order Book Monitoring Script designed to enable the "Markets" team to monitor the bid-ask spread in the BTC_MXN and USD_MXN order books provided by the Bitso API. Additionally, it generates alerts when the spread exceeds certain predefined thresholds, such as 1.0%, 0.5%, 0.1%, or any other custom value. Below is the detailed documentation of the script.

## Requirements
Before running the script, make sure you have the following requriments:

- Python
  - requests: For making HTTP requests to the Bitso API.
  - pandas: For data manipulation and formatting.
- Bitso API
  - Testing account: you need create an account in bitso
  - Funds: as developer you can contact directly to the team for this step
  - Credentials: api key and api secret

## Main Functionality
The script performs the following actions:
- Makes requests to the Bitso API to fetch real-time data from an order book (BTC_MXN or USD_MXN).
- Calculates the bid-ask spread using the formula: (best_ask - best_bid) * 100 / best_ask.
- Generates alerts if the spread exceeds the specified threshold.
- Stores the records in CSV files every second and acumulate information for 10 minutes (600 records), in a directory structure simulating partitions in S3 by date and time.
  
## Alerts
When the spread exceeds the specified threshold, an alert will be generated in the console. Alerts indicate that the spread is greater than the set threshold. The alerts by consolo can be change by any other type of alert.

## Running the Script
To execute the script, follow these steps:

Open a terminal in your development environment.

Run the following command:

```
cd Challenge_1
python3 save_books.py --bookname btc_mxn --alertspread 0.5 --datadir ./data
```

To get help with the arguments:

```
python3 save_books.py --help
  usage: save_books.py [-h] [-b BOOKNAME] [-a ALERTSPREAD] [-d DATADIR]

  Arguments for the process.

  optional arguments:
    -h, --help            show this help message and exit
    -b BOOKNAME, --bookname BOOKNAME
                          The book name of the orders to checks. example 'btc_mxn'.
    -a ALERTSPREAD, --alertspread ALERTSPREAD
                          The percentage of bid-ask spread to alert. example 1.0 for 1 percent
    -d DATADIR, --datadir DATADIR
                          full path for the data directory.
```

## Justification of Partition Structure
The chosen partition structure for storing data is based on the need to organize records by date and time. This facilitates easy retrieval and analysis of historical data. The structure is as follows:
- 📁 ./data/
  - 📁 [book_name]/
    - 📁 [date]/
      - 📁 [fixed_time]/
        - 📄 data.csv
    
Fixed time refers to the modify time for every 10 minutos. Example: 17:00, 17:10, 17:20 ...
Each data.csv file contains records for a 10-minute period and is located in a directory corresponding to its date and fixed time.

# Challenge 2

This folder contains the Python ETL (Extract, Transform, Load) script to address the challenge of providing master data for downstream users in Business Intelligence, Machine Learning, Experimentation, and Marketing. The script processes four CSV files: `deposit.csv`, `withdrawal.csv`, `event.csv`, and `user.csv`, and generates master data tables to help answer various analytical questions. Additionally, the repository includes an Entity-Relationship Diagram (ERD) illustrating the data model and sample queries to demonstrate the capabilities of the solution.

## Data Modeling Techniques

The data modeling technique employed for this challenge is a traditional relational database model. This choice was made because it provides a structured and normalized way to organize data, making it suitable for complex analytical queries. The tables are designed to support the following use cases efficiently:

- Tracking user activity
- Identifying user's deposit behavior
- Analyzing login events
- Summarizing currency-related data

### Potential Downsides

While a relational model offers advantages in terms of query flexibility, it may have potential downsides such as increased complexity in schema design and potential performance issues when dealing with large volumes of data

## Entity-Relationship Diagram (ERD)

The ERD illustrates the relationships between the primary entities: `Users`, `Transactions` and `Events`. Users are at the center, with associations to their respective activities and related entities.

## Python ETL Script

The ETL script is provided in the `simple_etl.py` file. It performs the following steps:

1. Extraction: Reads data from the CSV files.
2. Transformation: Applies data transformations as required by the use cases.
3. Load: Stores the transformed data into separate CSV files, one for each table.

## Output Tables

The script generates the following output tables as CSV files:

- `users.csv`
- `events.csv`
- `transactions_sample.csv` (this last is just a sample from the original transactions.csv)

## Sample Queries

Sample queries to answer specific use cases are provided in the `queries.txt` file. These queries demonstrate how to extract valuable insights from the data model.

## Running the ETL Script

To run the ETL script and generate the output tables, follow these steps:

1. Ensure you have Python 3.x installed on your system.
2. Run the simple ETL script:

   ```bash
   python3 simple_etl.py
   ```

The script will extract, transform, and load the data into CSV files. 

## Queries

To execute queries against the generated tables, you can use a SQL client or tool of your choice and connect to your PostgreSQL database. Sample queries are provided in the `queries.sql` file to answer specific use cases.

## Additional Notes
- Remember that you need the initials csv files. (For privacy are not shared)
- DAG.py file is just an example of use of Airflow.
- The provided solutions focus on generating structured data tables. For real-world scenarios, you might want to consider additional factors such as data validation, error handling, and scalability.

For any questions or further assistance, please feel free to reach out.

**Author: Karen Bermudez**


