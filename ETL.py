import yfinance as yf
import numpy as np
import pandas as pd
import datetime as dt
import os

# ==========================================
# 1. SETUP
# ==========================================
# Ticker mapping: Yahoo Ticker -> Filename
ticker_map = {'AAPL': 'AAPL', 'TSLA': 'TSLA', 'MSFT': 'MSFT', 'GC=F': 'GOLD', 'SPY': 'SPY', 'AMZN': 'AMZN'}

# Current date string
today = dt.datetime.now().strftime('%Y-%m-%d') 

# ==========================================
# 2. INCREMENTAL DOWNLOAD LOOP
# ==========================================
for ticker, filename in ticker_map.items(): 
    file_path = f"{filename}.csv"
    
    if os.path.exists(file_path): 
        existing_df = pd.read_csv(file_path)
        existing_df['Date'] = pd.to_datetime(existing_df['Date']) 
        last_date = existing_df['Date'].max()
        
        # Start fetch 1 day after the last recorded date
        start_fetch = (last_date + dt.timedelta(days=1)).strftime('%Y-%m-%d')
        
        if start_fetch >= today: 
            print(f"✅ {filename.upper()} is already up to date.")
            continue   

        print(f"🚀 Fetching {ticker} delta starting from {start_fetch}")
        new_data = yf.download(ticker, start=start_fetch, end=today, auto_adjust=False)
        
        if new_data is not None and not new_data.empty:
            try:
                # Cleaning yfinance multi-index columns if they exist
                if isinstance(new_data.columns, pd.MultiIndex):
                    new_data.columns = new_data.columns.get_level_values(0)
                
                new_data = new_data.reset_index()
                new_data['Ticker'] = ticker
                
                # Merge and clean duplicates
                updated_df = pd.concat([existing_df, new_data]).drop_duplicates(subset=['Date'])
                updated_df.to_csv(file_path, index=False)
                print(f"✔️ {filename}.csv updated.")
            except Exception as e:
                print(f"⚠️ Error processing {ticker}: {e}")
                
    else:
        # Initial download if file doesn't exist (First time setup)
        print(f"📥 Initial download for {ticker} -> {filename}.csv")
        df = yf.download(ticker, start="2020-01-01", auto_adjust=False)
        
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        df = df.reset_index()
        df['Ticker'] = ticker
        df.to_csv(file_path, index=False)

# ==========================================
# 3. MASTER PROCESSING FUNCTION
# ==========================================
def create_master_files(cols=['Date', 'Adj Close']):
    """
    Part A: Stacks all stocks into 'all_stocks_raw.csv' (Long format).
    Part B: Pivots data into 'portfolio_prices.csv' (Wide format for Dashboard).
    """
    
    # --- PART A: RAW DATA STACKING ---
    all_data_list = []
    for filename in ticker_map.values():
        file_path = f"{filename}.csv"
        if os.path.exists(file_path):
            all_data_list.append(pd.read_csv(file_path))
    
    if all_data_list:
        raw_master_df = pd.concat(all_data_list, ignore_index=True)
        raw_master_df.to_csv('all_stocks_raw.csv', index=False)
        print("📦 'all_stocks_raw.csv' created.")

    # --- PART B: PRICE PIVOTING ---
    main_df = None
    for filename in ticker_map.values():
        file_path = f'{filename}.csv'
        if os.path.exists(file_path):
            # Load only Date and Adj Close
            df_temp = pd.read_csv(file_path, index_col='Date', parse_dates=True, usecols=cols)
            df_temp = df_temp.rename(columns={'Adj Close': filename})
            
            if main_df is None:
                main_df = df_temp
            else:
                main_df = main_df.join(df_temp, how='outer')

    if main_df is not None:
        # Clean and format
        df_final = main_df.dropna(how='all').sort_index()
        df_final.index.names = ['Date']
        df_final.columns = [col.lower() for col in df_final.columns]
        
        # Save the final Dashboard file
        df_final.to_csv('portfolio_prices.csv')
        print("🏠 'portfolio_prices.csv' updated for the Dashboard.")
        return df_final

# ==========================================
# 4. EXECUTION
# ==========================================
if __name__ == "__main__":
    print("🏁 Starting CSV-only ETL Process...")
    create_master_files()
    print("🚀 ETL Pipeline Finished successfully.")
