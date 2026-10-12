import pandas as pd
import numpy as np
import gc # Garbage collector to free up memory
import os

def downcast_dtypes(df):
    """
    Reduces memory usage by converting 64-bit integers and floats 
    to 16-bit or 32-bit depending on the maximum value.
    """
    start_mem = df.memory_usage().sum() / 1024**2
    for col in df.columns:
        col_type = df[col].dtype
        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                else:
                    df[col] = df[col].astype(np.float32)
    
    end_mem = df.memory_usage().sum() / 1024**2
    print(f"  -> Memory reduced from {start_mem:.2f} MB to {end_mem:.2f} MB")
    return df

if __name__ == "__main__":
    print("Step 1: Loading wide-format sales data...")
    # Using 'data/' because pipeline.py is in the root folder
    sales = pd.read_csv('data/sales_train_evaluation.csv')

    print("Step 2: Melting data (Wide to Long transformation)...")
    id_vars = ['id', 'item_id', 'dept_id', 'cat_id', 'store_id', 'state_id']
    sales_melted = pd.melt(sales, 
                           id_vars=id_vars, 
                           var_name='d', 
                           value_name='sales')

    print("Step 3: Downcasting sales data to save RAM...")
    sales_melted = downcast_dtypes(sales_melted)

    # Delete original wide dataframe to free up RAM
    del sales
    gc.collect()

    print("Step 4: Loading calendar and pricing data...")
    calendar = pd.read_csv('data/calendar.csv')
    prices = pd.read_csv('data/sell_prices.csv')

    print("Step 5: Downcasting calendar and pricing data...")
    calendar = downcast_dtypes(calendar)
    prices = downcast_dtypes(prices)

    print("Step 6: Merging calendar data...")
    calendar_cols = ['d', 'date', 'wm_yr_wk', 'event_name_1', 'snap_CA', 'snap_TX', 'snap_WI']
    sales_melted = sales_melted.merge(calendar[calendar_cols], on='d', how='left')

    print("Step 7: Merging pricing data...")
    sales_final = sales_melted.merge(prices, on=['store_id', 'item_id', 'wm_yr_wk'], how='left')

    del sales_melted
    gc.collect()

    print("Step 8: Saving processed analytical dataset as Pickle...")
    sales_final.to_pickle('data/processed_pricing_data.pkl')

    print("Pipeline Complete! Processed data saved to data/processed_pricing_data.pkl")