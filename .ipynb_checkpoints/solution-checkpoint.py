import pandas as pd
import numpy as np
import argparse

def main():
    parser = argparse.ArgumentParser(description='Ürün özelliklerini hesapla.')
    parser.add_argument('--min-date', type=str, default='2021-01-08', help='Başlangıç tarihi, format: YYYY-AA-GG')
    parser.add_argument('--max-date', type=str, default='2021-05-30', help='Bitiş tarihi, format: YYYY-AA-GG')
    args = parser.parse_args()

    # Veri setlerini yükle
    brand_df = pd.read_csv('brand.csv')
    product_df = pd.read_csv('product.csv')
    store_df = pd.read_csv('store.csv')
    sales_df = pd.read_csv('sales.csv')

    # Tarihi datetime türüne çevir
    sales_df['date'] = pd.to_datetime(sales_df['date'])

    # Tarih aralığına göre satış verisini filtrele
    mask = (sales_df['date'] >= args.min_date) & (sales_df['date'] <= args.max_date)
    sales_df = sales_df[mask]

    # Ürün seviyesinde özellikleri hesapla
    product_df['MA7_P'] = product_df.groupby('id')['quantity'].rolling(window=7).mean().reset_index(level=0, drop=True)
    product_df['LAG7_P'] = product_df.groupby('id')['quantity'].shift(7)

    # Marka seviyesinde özellikleri hesapla
    sales_df['brand'] = sales_df['product'].map(product_df.set_index('id')['brand'])
    brand_df['id'] = brand_df['id'].astype(str)
    sales_df['brand'] = sales_df['brand'].astype(str)
    sales_df = sales_df.merge(brand_df, left_on='brand', right_on='id')
    sales_df['MA7_B'] = sales_df.groupby('brand')['quantity'].rolling(window=7).mean().reset_index(level=0, drop=True)
    sales_df['LAG7_B'] = sales_df.groupby('brand')['quantity'].shift(7)

    # Mağaza seviyesinde özellikleri hesapla
    sales_df['MA7_S'] = sales_df.groupby('store')['quantity'].rolling(window=7).mean().reset_index(level=0, drop=True)
    sales_df['LAG7_S'] = sales_df.groupby('store')['quantity'].shift(7)

    # Veri çerçevelerini birleştir
    result_df = sales_df.merge(product_df, left_on='product', right_on='id')
    result_df = result_df.merge(store_df, left_on='store', right_on='id')

    # Sütunları seç ve yeniden düzenle
    columns = ['id_x', 'id_y', 'id', 'date', 'quantity', 'MA7_P', 'LAG7_P', 'MA7_B', 'LAG7_B', 'MA7_S', 'LAG7_S']
    result_df = result_df[columns]
    result_df.columns = ['product_id', 'store_id', 'brand_id', 'date', 'sales_product', 'MA7_P', 'LAG7_P', 'sales_brand', 'MA7_B', 'LAG7_B', 'sales_store', 'MA7_S', 'LAG7_S']

    # Veriyi sırala
    result_df = result_df.sort_values(by=['product_id', 'brand_id', 'store_id', 'date'])

    # Sonucu bir CSV dosyasına kaydet
    result_df.to_csv('features.csv', index=False)

if __name__ == '__main__':
    main()











