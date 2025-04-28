# Import required libraries
import time
import pandas as pd
import requests
import os
import logging
from datetime import datetime, timedelta, date
import random
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# Set up logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler("scraper.log"),
#         logging.StreamHandler()
#     ]
# )
# logging.info("Starting web scraping process...")

# 隨機延遲函數
def random_delay():
    time.sleep(random.uniform(5, 10))  # 隨機延遲 5 到 10 秒


def setup_driver():
    """
    Function to set up the Selenium WebDriver with Chrome options.
    """
    # 設定 Chrome Options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 無頭模式 不顯示瀏覽器界面
    chrome_options.add_argument("--no-sandbox") # 避免沙盒
    chrome_options.add_argument("--incognito") # 無痕模式
    chrome_options.add_argument("--disable-dev-shm-usage") # 避免記憶體不足
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 隱藏無頭模式特徵
    chrome_options.add_argument("window-size=1920,1080")  # 模擬普通瀏覽器視窗大小
    # 禁止印出log、隱藏受自動化軟體控制之資訊
    # 禁用Chrome的自動化擴充功能
    # 可以避免某些網站檢測到自動化測試而阻擋訪問
    # 提高爬蟲的穩定性和真實性
    # 這些設定的主要目的是:

    # 讓自動化程式更像真實用戶在使用瀏覽器
    # 避免被網站檢測出是自動化工具
    # 減少不必要的日誌輸出
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging', 'enable-automation'])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # 許多網站會檢測 User-Agent，如果發現是無頭瀏覽器，可能會拒絕訪問。可以通過 chrome_options 設置自訂的 User-Agent。
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36"
    )  # 設定自訂 User-Agent

    # 啟動 Selenium WebDriver
    # 自動下載與配置 ChromeDriver 它會根據你的 Chrome 瀏覽器版本自動匹配合適的 ChromeDriver，免除手動下載與管理
    try:
        service = Service(ChromeDriverManager().install())
        browser = webdriver.Chrome(
            service=service,
            options=chrome_options
        )
    except Exception as e:
        print(f"Error initializing Chrome browser: {e}")
        raise # Keep this to ensure program stops on critical error

    # 禁用 Selenium 的特徵標記
    # 隱藏 Selenium 特徵
    browser.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            """
        },
    )
    return browser    
    

def scrape_cna_news( target_date_str ):
    """
    Function to scrape CNA news website, extract article information,
    and save the data to a CSV file with today's date.
    """
    
    # 設定目標日期
    # target_date_str = '2025-03-26'  # Example date string
    target_date = datetime.strptime(target_date_str, '%Y-%m-%d')
    
    # 示範爬取政治類新聞，若要爬所有的類別，需增加一個迴圈處理每一個類別
    full_url = 'https://www.cna.com.tw/list/aipl.aspx' #政治
    # full_url = 'https://www.cna.com.tw/list/aopl.aspx' #國際
    # full_url = 'https://www.cna.com.tw/list/ahel.aspx' #生活
    
    # Initialize lists to store data
    # 存放資料之變數
    title_list=[]
    date_list=[]
    category_list=[]
    article_link_list =[]
    photo_link_list=[]

    item_id_list=[]
    content_list=[]

    try:
        # Set up the Selenium WebDriver
        browser = setup_driver()        
        # URL of the CNA news website
        browser.get(full_url)
        # 隨機延遲
        random_delay()
        
        
        page = 1
        while True:        
            
            # 滾輪到最下面
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print('滾輪到最下面OK')
        
            # 滾輪到最下面
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print('滾輪到最下面OK')
            
            # Google需搭配新版的Selenium--新版modified on March 8, 2023
            try:
                # 等待元素可見
                element = WebDriverWait(browser, 20).until(EC.visibility_of_element_located((By.ID, "SiteContent_uiViewMoreBtn_Style3")))
                browser.find_element(By.ID,"SiteContent_uiViewMoreBtn_Style3").click()
                print('按更多新聞OK')
                print(f'翻頁{page}次')
                page += 1
            except Exception as ex:
                # 最後一頁沒有更多新聞了，沒有按鈕可按，會拋錯!
                # print('按更多新聞失敗!',ex)
                print('最後一頁沒有更多新聞了，沒有按鈕可按，拋錯!')
                break

            # Here we can control the number of pages to scroll.
            # 可以只翻3次pages
            # if (page >= 3): 
            #     break 
            random_delay()  # 隨機延遲
        # Function to extract data from current page
        # def extract_page_data():
            
               
        print('開始抓新聞列表')    
        
        # Soup靜態網頁分析
        html = browser.page_source
        item_list_soup = BeautifulSoup(html, 'lxml')
        
        # 取得新聞列表內容
        # (1) Soup版本
        # 取得頁面HTML
        items = item_list_soup.select('ul.mainList li a')
        # (2) Selenium版本
        # items = browser.find_elements(By.CSS_SELECTOR, 'ul.mainList li a')

        # 取得新聞列表內容，逐項處理
        serial_no=1
        for item in items:
            
            # 抓日期
            try:
                # (1) Soup版本
                news_time_str = item.find('div', {'class':"date"}).text #抓日期時間字串有包含(時:分)
                # (2) Selenium版本
                # In Selenium, you'd use find_element instead of find
                # news_time_str = item.find_element(By.CSS_SELECTOR, 'div.date').text
            
                # 排除穿插的廣告 其日期有錯
                news_dtime = datetime.strptime(news_time_str, '%Y/%m/%d %H:%M') #轉成datetime格式
            except:
                print('排除這則新聞:',item)
                continue

            # article date
            news_date_str = news_dtime.strftime("%Y-%m-%d")

            # 新聞時間過濾，你若要爬某一天的新聞，必須過濾。若要爬取全部，則將以下兩行指令取消即可。
            # 排除不是目標日期的新聞 兩者日期相比對
            
            if target_date.date() != news_dtime.date():
                # print(f"新聞日期不符合，跳開這一則{item['href']}")
                continue

            # date
            print(news_date_str)

            # title
            # (1) Soup版本
            title = item.find('h2').find('span').text
            # (2) Selenium版本
            # title = item.find_element(By.CSS_SELECTOR, 'h2 span').text
            print(title)
            
            category_list.append('政治')
            date_list.append(news_date_str)
            title_list.append(title)
            item_id_list.append("暫無")
            content_list.append("暫無")
            article_link_list.append("暫無")
            photo_link_list.append("暫無")
        # end of for item in items:
        
        # zip and convert data to datafame
        data = zip(item_id_list, date_list, title_list, category_list, content_list, article_link_list, photo_link_list)
        df_news = pd.DataFrame(list(data), columns=['item_id','date','title','category','content','link','photo_link'])
        
        filename = f"cna-{target_date_str}.csv"
        df_news.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"共取得{len(df_news)}則新聞語料")
        
    except Exception as ex:
        print('抓新聞失敗!',ex)
    finally:
        # 關閉瀏覽器
        browser.quit()
        print('關閉瀏覽器OK')    
        # pass
        
if __name__ == "__main__":
    # 設定目標日期
    # target_date_str = '2025-03-26'  # Example date string
    target_date = datetime.now() - timedelta(days=1)  # 昨天
    target_date_str = target_date.strftime('%Y-%m-%d')
    
    # 抓取新聞資料
    scrape_cna_news(target_date_str)