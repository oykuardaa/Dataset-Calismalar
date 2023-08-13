import pandas as pd
import argparse
import numpy as np

# Komut satırı argümanları
parser = argparse.ArgumentParser(description="Ürün özellikleri oluştur.")
parser.add_argument("--min-date", type=str, default="2021-01-08", help="Başlangıç tarihi, format: 'YYYY-MM-DD'")
parser.add_argument("--max-date", type=str, default="2021-05-30", help="Bitiş tarihi, format: 'YYYY-MM-DD'")
args = parser.parse_args()

# Veriyi yükleme
brand_df = pd.read_csv("brand.csv")
product_df = pd.read_csv("product.csv")
store_df = pd.read_csv("store.csv")
sales_df = pd.read_csv("sales.csv")

# brand adı ve id'si için sözlük oluşturma
brand_name_to_id = dict(zip(brand_df["name"], brand_df["id"]))

# product_df'e marka adlarının karşılık geldiği brand_id'leri ekleme
product_df["brand_id"] = product_df["brand"].map(brand_name_to_id)

# store adı ve id'si için sözlük oluşturma
store_name_to_id = dict(zip(store_df["name"], store_df["id"]))

# sales_df veri çerçevesine store adlarına karşılık gelen store_id'leri eklemek
sales_df["store_id"] = sales_df["store"].map(store_name_to_id)

# Verileri birleştirme
sales_df = sales_df.merge(product_df, left_on="product", right_on="id")
sales_df = sales_df.merge(store_df, left_on="store", right_on="id", suffixes=("", "_store"))
sales_df = sales_df.merge(brand_df, left_on="brand_id", right_on="id", suffixes=("", "_brand"))

# Tarih sütununu tarih formatına çevirme
sales_df["date"] = pd.to_datetime(sales_df["date"])

# Tarih aralığına göre veriyi filtreleme
filtered_sales_df = sales_df[(sales_df["date"] >= pd.to_datetime(args.min_date)) & (sales_df["date"] <= pd.to_datetime(args.max_date))]

# Ürün özelliklerini hesaplama
filtered_sales_df["MA7_P"] = filtered_sales_df.groupby("product")["quantity"].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
filtered_sales_df["LAG7_P"] = filtered_sales_df.groupby("product")["quantity"].transform(lambda x: x.shift(7))

# Marka ve mağaza özelliklerini hesaplama
filtered_sales_df["MA7_B"] = filtered_sales_df.groupby(["brand_id", "store_id"])["quantity"].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
filtered_sales_df["LAG7_B"] = filtered_sales_df.groupby(["brand_id", "store_id"])["quantity"].transform(lambda x: x.shift(7))

filtered_sales_df["MA7_S"] = filtered_sales_df.groupby("store_id")["quantity"].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
filtered_sales_df["LAG7_S"] = filtered_sales_df.groupby("store_id")["quantity"].transform(lambda x: x.shift(7))

# Sütunları seçme ve yeniden düzenleme
output_columns = [
    "product", "store_id", "brand_id", "date", "quantity",
    "MA7_P", "LAG7_P", "MA7_B", "LAG7_B", "MA7_S", "LAG7_S"
]
output_df = filtered_sales_df[output_columns]

# Çıktıyı sıralama
output_df = output_df.sort_values(by=["product", "brand_id", "store_id", "date"])

# Çıktıyı CSV olarak yazma
output_df.to_csv("features.csv", index=False)
