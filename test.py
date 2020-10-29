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

today = datetime.today() - timedelta(hours=4)
time = today.strftime('%I:%M%p')
print(time)