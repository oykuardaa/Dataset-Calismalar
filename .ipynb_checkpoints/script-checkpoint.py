
import pandas as pd
import numpy as np

def moving_average(arr, window_size):
    return np.convolve(arr, np.ones(window_size)/window_size, mode='valid')

def lag_feature(arr, lag):
    return np.roll(arr, lag)

def generate_features(sales_df, brand_df, product_df, store_df, min_date, max_date):
    features = []
    
    for date in pd.date_range(min_date, max_date):
        for product_id in product_df['id']:
            for brand_id in brand_df['id']:
                for store_id in store_df['id']:
                    mask = (
                        (sales_df['date'] >= date - pd.DateOffset(days=7)) &
                        (sales_df['date'] <= date) &
                        (sales_df['product'] == product_id) &
                        (brand_df.loc[brand_id, 'name'] == product_df.loc[product_id, 'brand']) &
                        (sales_df['store'] == store_id)
                    )
                    
                    sales_product = sales_df.loc[mask, 'quantity'].sum()
                    MA7_P = moving_average(sales_df.loc[mask, 'quantity'], 7)[-1] if mask.sum() >= 7 else 0
                    LAG7_P = lag_feature(sales_df.loc[mask, 'quantity'], 7)[-1] if mask.sum() >= 7 else 0
                    
                    sales_brand = sales_df.loc[mask, 'quantity'].sum()
                    MA7_B = moving_average(sales_df.loc[mask, 'quantity'], 7)[-1] if mask.sum() >= 7 else 0
                    LAG7_B = lag_feature(sales_df.loc[mask, 'quantity'], 7)[-1] if mask.sum() >= 7 else 0
                    
                    sales_store = sales_df.loc[mask, 'quantity'].sum()
                    MA7_S = moving_average(sales_df.loc[mask, 'quantity'], 7)[-1] if mask.sum() >= 7 else 0
                    LAG7_S = lag_feature(sales_df.loc[mask, 'quantity'], 7)[-1] if mask.sum() >= 7 else 0
                    
                    features.append([product_id, store_id, brand_id, date, sales_product, MA7_P, LAG7_P, sales_brand, MA7_B, LAG7_B, sales_store, MA7_S, LAG7_S])
    
    features_df = pd.DataFrame(features, columns=['product_id', 'store_id', 'brand_id', 'date', 'sales_product', 'MA7_P', 'LAG7_P', 'sales_brand', 'MA7_B', 'LAG7_B', 'sales_store', 'MA7_S', 'LAG7_S'])
    return features_df

# Load data
brand_df = pd.read_csv("brand.csv")
product_df = pd.read_csv("product.csv")
store_df = pd.read_csv("store.csv")
sales_df = pd.read_csv("sales.csv")
sales_df['date'] = pd.to_datetime(sales_df['date'])

# Set the date range
min_date = "2021-01-08"
max_date = "2021-05-30"

# Generate features
features_df = generate_features(sales_df, brand_df, product_df, store_df, min_date, max_date)

# Save output to a CSV file
features_df.to_csv("features.csv", index=False)

features_df.head()
