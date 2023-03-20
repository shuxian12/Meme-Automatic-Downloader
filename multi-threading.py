import requests
from bs4 import BeautifulSoup
import os
from urllib.request import urlretrieve
import threading
import time
from fake_useragent import UserAgent

picture_URL_list = []
page_URL_list = []
url_thread = []
download_thread = []
gLock = threading.Lock()    # 初始化鎖
ua = UserAgent()


# 提取圖片的URL
def get_url():
    # 鎖住
    gLock.acquire()
    # 使用完後要釋放
    if len(page_URL_list) == 0:
        gLock.release()
    else:
        page_url = page_URL_list.pop()
        gLock.release()
        user_agent = ua.random
        headers = {'user-agent': user_agent}
        response = requests.get(page_url, headers=headers)
        soup = BeautifulSoup(response.content, 'lxml')
        img_list = soup.find_all('img', class_='img-fluid lazy')
        time.sleep(0.5)

        for image in img_list:
            src = image['data-src']
            if not src.startswith('http'):
                src = 'http:' + src
            # 爬到url就開thread去下載
            download_thread.append(threading.Thread(target=download, args=(src,)))
            download_thread[len(download_thread) - 1].start()

        # print(src)


def download(picture_url):
    if not os.path.isdir('images'):
        os.mkdir('images')
    spilt = picture_url.split('/')
    filename = spilt.pop()
    gLock.acquire()
    print('%s is downloading.' % filename)
    gLock.release()
    path = os.path.join('images', filename)
    urlretrieve(picture_url, filename=path)


page = 200    # 要處理的頁數
gif_page_url = 'https://memes.tw/gif-post?page='
base_page_url = 'https://memes.tw/wtf?page='
need = input("which kind of image do you like, 梗圖(΄◞ิ౪◟ิ‵) or 動圖(☞ﾟ∀ﾟ)ﾟ∀ﾟ)☞???\nYour answer: ")
choose = input("How many images do you want to download, 預設為4000張? default or choose: ")
if choose == "choose":
    page = int(input("Number of images: 20(張) * 請輸入頁數(MAX 250): "))
if need == '梗圖':
    for i in range(1, page):
        url = base_page_url + str(i)
        page_URL_list.append(url)
        # print(url)
elif need == '動圖':
    for i in range(1, page):
        url = gif_page_url + str(i)
        page_URL_list.append(url)
        # print(url)
else:
    print('Your command is not accepted.')

for x in range(len(page_URL_list)):
    url_thread.append(threading.Thread(target=get_url()))
    url_thread[len(url_thread)-1].start()

# 等待所有thread執行完畢
for z in range(len(download_thread)):
    download_thread[z].join()

print("done")
