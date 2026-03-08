import yfinance as yf# it connects to yahoo finance to pull stock data
import numpy as np # The Math Engine
import pandas as pd # handles the data in a table format (DataFrame)
import datetime as dt # to manage time ranges (e.g., "the last 5 years")
import os # save the results to folders on your computer.

# Create a dictionary to map Yahoo Tickers (keys) to our specific CSV filenames (values)
ticker_map = {'AAPL': 'AAPL', 'TSLA': 'TSLA', 'MSFT': 'MSFT', 'GC=F': 'GOLD', 'SPY': 'SPY', 'AMZN': 'AMZN'}

# Get current system time and turn it into a clean string format like '2026-02-20'
today = dt.datetime.now().strftime('%Y-%m-%d') 

# Start a loop that pulls both the 'key' (ticker) and 'value' (filename) for each pair
for ticker, filename in ticker_map.items(): 
    
    # Create the full filename string by adding '.csv' to the end of our name (e.g., 'GOLD.csv')
    file_path = f"{filename}.csv"
    
    # Ask the Operating System: "Does a file with this name already sit in my folder?"
    if os.path.exists(file_path): 
        
        # Load the existing CSV data into a Pandas table (DataFrame)
        existing_df = pd.read_csv(file_path)
        
        # Convert the 'Date' column from plain text to specialized 'DateTime' objects for math
        existing_df['Date'] = pd.to_datetime(existing_df['Date']) 
        
        # Find the most recent (maximum) date currently stored in our file
        last_date = existing_df['Date'].max()
        
        # Add 1 day to the last date to find where the new download should start, then format it as text
        start_fetch = (last_date + dt.timedelta(days=1)).strftime('%Y-%m-%d')
        
        # Logic Check: If our next start date is today or later, we don't need to do anything
        if start_fetch >= today: 
            # Tell the user the data is already fresh
            print(f"✅ {filename.upper()} is already up to date.")
            # Skip all code below this line and jump immediately to the next stock in the loop
            continue   

        # If we reached this line, it means we NEED data. Print a message to show progress.
        print(f"🚀 Fetching {ticker} delta for {filename}.csv starting from {start_fetch}")
        
        # Ask the yfinance API to give us data from our 'start_fetch' date up until 'today'
        new_data = yf.download(ticker, start=start_fetch, end=today, auto_adjust=False)
        
        # Safety Check: Only proceed if the API actually found and returned rows of data
        if new_data is not None and not new_data.empty:
            try:

                # Fix the column names by removing the 'MultiIndex' layer (the double-header row)
                new_data.columns = new_data.columns.get_level_values(0)
                
                # Move the Date from being the index (side label) into a normal data column
                new_data = new_data.reset_index()
                
                # Add a new column to identify which stock this data belongs to
                new_data['Ticker'] = ticker
                
                # Glue the old data and new data together, then delete any rows where the Date is identical
                updated_df = pd.concat([existing_df, new_data]).drop_duplicates(subset=['Date'])
                
                # Save the final, updated table back to the CSV file, overwriting the old version
                updated_df.to_csv(file_path, index=False)

            except Exception as e:
                print(f"⚠️ Error processing {ticker}: {e}")
                
    # This block runs ONLY if the file_path was NOT found (first time running the code)
    else:
        # Inform the user that we are building a new database from scratch
        print(f"📥 Initial download for {ticker} -> {filename}.csv")
        
        # Download the entire history from 2020 until today
        df = yf.download(ticker, start="2020-01-01", auto_adjust=False)
        
        # Repeat the cleaning steps: Fix columns, reset index, and add the ticker label
        df.columns = df.columns.get_level_values(0)
        df = df.reset_index()
        df['Ticker'] = ticker
        
        # Create the new CSV file and save all the data into it

        df.to_csv(file_path, index=False)

