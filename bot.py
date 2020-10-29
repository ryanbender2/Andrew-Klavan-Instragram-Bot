from datetime import datetime, timedelta
from pytube import YouTube
from csv import reader
from threading import Thread
from time import sleep
from random import randint
import ssl
from smtplib import SMTP_SSL
import instagram
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

EMAIL_PASS = open("C:\\MSI\\email_pass.key", 'r').readline()
EMAIL_SERVER = SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
EMAIL_SERVER.login('ak.insta.contact@gmail.com', EMAIL_PASS)

LINK = 'https://www.youtube.com/c/AndrewKlavan/videos'

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])


def email(subject: str, body: str) -> None:
    message = f'Subject: {subject}\n\n{body}'
    EMAIL_SERVER.sendmail('ak.insta.contact@gmail.com', 'ryan.bender.general@gmail.com', message)


class VideoHandler(Thread):
    """Update the list of videos that's been
        loaded to instagram.

    """
    _generated_filename: str
    _video_id: str
    _video_path: str
    _video_desc: str
    _video_title: str
    _successfully_uploaded = False

    def __init__(self, video_title:str, video_id: str) -> None:
        super().__init__()

        self._video_id = video_id
        self._video_title = video_title

        date = datetime.today().strftime('%m-%d-%Y')
        self._generated_filename = f'temp{randint(10000, 99999)}_{date}'


    def download_video(self, new_filename: str) -> None:
        yt = YouTube('https://www.youtube.com/watch?v=' + self._video_id)
        filepath = yt.streams.first().download('C:\\Users\\ryanb\\OneDrive\\Documents\\' +
                'GitHub\\Andrew-Klavan-Instragram-Bot\\temp_video_storage\\', new_filename)
        self._video_path = filepath
        self._video_desc = yt.description
    

    def upload_to_instagram(self) -> None:
        instagram.Bot(self._video_path, self._video_title, self._video_desc, self._video_id)


    def run(self) -> None:
        self.download_video(self._generated_filename)
        self.upload_to_instagram()


def do_search(driver: webdriver.Chrome) -> list:
    videos = []
    for ele in driver.find_elements_by_id('video-title')[:3]:
        videos.append((ele.text, str(ele.get_attribute('href')).split('=')[1]))
    return videos


def loop() -> None:
    global CHROME_OPTIONS
    global LINK

    while (True):
        driver = webdriver.Chrome('chromedriver.exe', options=CHROME_OPTIONS)
        driver.get(LINK)

        uploaded_videos = [i[0] for i in reader(open('uploaded_videos.csv', 'r'))]
        video_search = do_search(driver=driver)
        
        new_videos = False
        new_videos_to_do = []

        for item in video_search:
            if item[1] not in uploaded_videos:
                new_videos = True
                new_videos_to_do.append(item)

        if new_videos:
            print('new videos to upload!')

            for video in new_videos_to_do:
                new_video = VideoHandler(video[0], video[1])
                new_video.start()

                sleep(5)
        else:
            print('no new videos!')
            sleep(600) # 600 -> 10 minutes

        driver.close()


def main():
    today = datetime.today()
    date = today.strftime('%m/%d/%Y')
    time = today.strftime('%I:%M %p')
    subject = 'Klavan Bot | INFO'
    mess = f'Dear Maker,\n\nOn {date} at {time}, I was started and have begun running my rounds.\n\nLove,\nBot'
    # email(subject, mess)
    print(subject)

    while (True):
        try:
            loop()
        except Exception as ex:
            print("something failed, server restarting..." + str(ex))
            sleep(5)
            

def testing():
    # some = _youtube.search(channel_id='UCyhEZKz-LOwgktptEOh6_Iw', published_after=one_day_ago, order_by='date')
    # print(some)
    pass

if __name__ == "__main__":
    main()
    # testing()