import os
import sys
import pandas as pd
import argparse
from datetime import datetime
import pathlib

# # Setup Django environment
# # Alternative 1: Use absolute path construction
# current_dir = os.path.abspath('')
# parent_dir = os.path.dirname(current_dir)
# sys.path.insert(0, parent_dir)

# # Alternative 2: Use pathlib for more modern path handling
# parent_path = pathlib.Path().absolute().parent
# sys.path.insert(0, str(parent_path))

# 新增：將上一層目錄加入 sys.path
parent_path = pathlib.Path().absolute().parent
sys.path.insert(0, str(parent_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_configs.settings')
import django
django.setup()
# 重要：設定環境變數以允許在 Jupyter 的異步環境中執行同步操作
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# Now we can import Django models
from app_user_keyword_db.models import NewsData

# Read CSV file
csv_file_path = '../app_user_keyword/dataset/cna_news_200_preprocessed.csv'
# csv_file_path = '../app_user_keyword/dataset/cna_news_preprocessed_12weeks.csv'
df = pd.read_csv(csv_file_path, sep='|')

# Process each row and create a NewsData object
for idx, row in df.iterrows():
    try:
        # Create or update NewsData object
        # This method tries to fetch an object with the given kwargs, 
        # and if it exists, updates the fields. If it doesn't exist, creates a new one.

        news_data, created = NewsData.objects.update_or_create(
            # Fields to look up the object查詢使用的欄位
            # 這些欄位的組合必須是唯一的，否則會導致錯誤
            # 這裡假設 item_id 是唯一的識別碼 通常是使用主鍵或唯一索引
            item_id=row['item_id'],
            # Fields to update or create with
            # 這些欄位是要更新或創建的欄位
            defaults={
                'date': datetime.strptime(row['date'], '%Y-%m-%d').date(),# Convert date string to datetime object
                'category': row['category'],
                'title': row['title'],
                'content': row['content'],
                'sentiment': row['sentiment'],
                #'summary': row['summary'],
                'top_key_freq': row['top_key_freq'],
                'tokens': row['tokens'],
                'tokens_v2': row['tokens_v2'],
                'entities': row['entities'],
                'token_pos': row['token_pos'],
                'link': row['link'],
                'photo_link': row['photo_link'] if row['photo_link'] != "" and not pd.isna(row['photo_link']) else None,
            }
        )
        if created:
            print(f"Created new NewsData object with item_id: {row['item_id']}")
        else:
            print(f"Updated existing NewsData object with item_id: {row['item_id']}")
    except Exception as e:
        print(f"Error at row {idx}: {e}")
        print(row)
        
