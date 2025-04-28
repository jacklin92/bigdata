# Import required libraries
import schedule
import time
from datetime import datetime, timedelta, date

from scrape_cna_news import scrape_cna_news 

def daily_scraping_tasks():
    """
    Function to run daily scraping tasks.
    """
    try:
    
        tic = time.time()
        current_time = datetime.now().strftime("%H:%M:%S")
        print('Start to process news data at {} ...'.format(current_time))
        # Crawl yesterday's news. Set target_date as yesterday.

        target_date = date.today()- timedelta(days=1)  #是昨天
        target_date = datetime.now() - timedelta(days=1) # 取得昨天日期
        target_date_str = target_date.strftime('%Y-%m-%d')
        
        # target_date_str = '2025-03-26'

        # 爬取新聞
        scrape_cna_news(target_date_str)
        
        # ----------------------------
        # 呼叫斷詞函數
        # tokenize_ckiplab()
        # 計算熱門關鍵字
        # calculate_topk_keyword()
        
        # process_chen_shih_chung()
        # process_taipei_mayor_election()
        # process_political_PK()
        # export data to database
        # export_to_mariadb()
        
        current_time = datetime.now().strftime("%H:%M:%S")
        print('完工時間:{}'.format(current_time))
        toc = time.time()
        min = int((toc-tic)//60)
        sec = int((toc-tic)%60)
        print(f"Total elapsed time: {min} minutes {sec} seconds")   
        
    except Exception as e:
        print(f"Error during daily scraping tasks: {e}")    


def run_scheduler(schedule_time=None):
    """
    Function to keep the scheduler running and execute pending tasks.
    """
    # Schedule the scraping task to run at 8:00 AM every day
    
    # You can also add additional schedules if needed
    # Schedule each task at a specific time or interval
    # schedule.every().day.at("08:00").do(task1)  # Runs every day at 08:00 AM
    # schedule.every(3).hours.do(task2)           # Runs every 3 hours
    # schedule.every().monday.at("10:30").do(task3)  # Runs every Monday at 10:30 AM

    schedule_time = '16:16'  # Taipei time 格式必須為:00:00 (凌晨零時)  23:40(晚上)
    schedule.every().day.at(schedule_time).do(daily_scraping_tasks)
    print('排程任務開始...'.format(schedule_time))
    while True:
        schedule.run_pending()
        
        next_run = schedule.idle_seconds()  # Get time until next task 
        hours = int(next_run // 60*60 ) # Convert seconds to hours
        minutes = int(next_run // 60) % 60  # Get minutes (remainder after dividing hours)
        print(f'等待下次啟動任務，小睡休息: {hours}小時{minutes}分鐘')
        # 睡覺一段時間，不必一直檢查有沒有工作要做，不要讓CPU負擔，節省能源
        # 醒來若發現還有懸置pending的工作要做，會立即做
        # time.sleep(60)  # Check every minute
        time.sleep(next_run)

# Run the scheduler
if __name__ == "__main__":
    run_scheduler()