import requests, json
from datetime import datetime, timedelta, timezone

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import WebDriverException
from time import sleep
from csv import reader
import AdvancedHTMLParser

# yt_key = None
# with open("C:\\MSI\\bot_key.key", 'r') as key_file:
#     yt_key = key_file.readline()

# time = datetime.now(timezone.utc).astimezone() - timedelta(hours=40)

# parameters = {
#     'key': '',
#     'part': 'snippet',
#     'channelId': 'UCyhEZKz-LOwgktptEOh6_Iw',
#     'maxResults': '5',
#     'order': 'date',
#     'publishedAfter': time.isoformat()
# }
# resp = requests.get('https://www.googleapis.com/youtube/v3/search', params=parameters)

# with open('testing.json', 'r') as file:
#     parsed = json.loads(''.join(file.readlines()))


#     print(json.dumps(parsed, indent=4, sort_keys=True))

def do_search(driver: webdriver.Chrome) -> list:
    videos = []
    for ele in driver.find_elements_by_id('video-title')[:3]:
        videos.append((ele.text, str(ele.get_attribute('href')).split('=')[1]))
    return videos

link = 'https://www.youtube.com/c/AndrewKlavan/videos'

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

# /html/body/ytd-app/div/ytd-page-manager/ytd-browse/ytd-two-column-browse-results-renderer/div[1]/ytd-section-list-renderer/div[2]/ytd-item-section-renderer[1]/div[3]/ytd-shelf-renderer/div[1]/div[2]/yt-horizontal-list-renderer/div[2]/div/ytd-grid-video-renderer[1]/div[1]/ytd-thumbnail/a/div[1]/ytd-thumbnail-overlay-time-status-renderer
# overlay-style="LIVE"


driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
driver.get(link)

uploaded_videos = [i[0] for i in reader(open('uploaded_videos.csv', 'r'))]
video_search = do_search(driver=driver)

new_videos = False
new_videos_to_do = []
for item in video_search:
    if item[1] not in uploaded_videos:
        new_videos = True
        new_videos_to_do.append(item)

if new_videos:
    # write new videos to uploaded list
    with open('uploaded_videos.csv', 'a') as uploaded_vids:
        for i in new_videos_to_do:
            uploaded_vids.write(i[1] + '\n')
    
    print('new videos to upload!')
    for i in new_videos_to_do:
        print(i)
else:
    print('no new videos!')




driver.close()