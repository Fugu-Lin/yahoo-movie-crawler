# yahoo-movie-crawler
"爬蟲並上傳至Firebase"

## Setup
1. Clone this repository:
  ```
  git clone https://github.com/Fugu-Lin/yahoo-movie-crawler.git
  ```
2. Install Package
  ```
  pip install -r requirements.txt
  ```
## models 說明
* Firebase_Operation.py
  * FirebaseOperation()[class]
    * update           # 更新資料至collection->document
    * create           # 新增資料至collection->document
    * setSubCollection # 新增資料至collection->document->collection->document
    * deleteCollection # 批次刪除collection的資料
    * retrieveAllDocument # 取出collection底下的所有document  

* Yahoo_Movie_Crawler.py
  * MovieCrawler.py[class]
    * getAllMovie # 取得Yahoo電影中的資料
      * 參數說明
        * url  # 爬蟲網址
        * area # 爬取時刻表的地區，如["宜蘭", "新竹"] 等
        * existMovieList # firebase內，已儲存於歷史資料中的電影，避免二次爬取，可增進效能


 ## 如何執行
  ```
  python example.py
  ```
  即可自動執行並上傳資料至你的firebase
  
  ![image](https://user-images.githubusercontent.com/53990453/170728961-9c7b1860-e31d-4ab8-9ee0-3716f9f56f7f.png)

