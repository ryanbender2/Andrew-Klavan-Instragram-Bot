from datetime import datetime, timedelta
import logging
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
from selenium.common.exceptions import WebDriverException

logging.basicConfig(filename='/home/ryan/fileshare/klavan_bot_logs.log',
                    level=logging.INFO,
                    datefmt='%m/%d/%Y %I:%M %p',
                    format='[%(asctime)s %(filename)s %(funcName)s():%(lineno)s] %(levelname)s: %(message)s')


setup_email = False
while not setup_email:
    try:
        EMAIL_PASS = open("/passcodes/email_pass.key", 'r').readline()
        EMAIL_SERVER = SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
        EMAIL_SERVER.login('ak.insta.contact@gmail.com', EMAIL_PASS)
        setup_email = True
    except:
        logging.exception(f'Failed at setting up server...probably no internet connection, trying again in 10 minutes')
        sleep(600)

LINK = 'https://www.youtube.com/c/AndrewKlavan/videos'

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])


def email(subject: str, body: str) -> None:
    logging.info(f'Sending an email -- {subject}')

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

        logging.info(f'Starting on new video {video_title}')

        self._video_id = video_id
        self._video_title = video_title

        date = datetime.today().strftime('%m-%d-%Y')
        self._generated_filename = f'temp{randint(1000, 99999)}_{self._video_id}_{date}'


    def download_video(self, new_filename: str) -> None:
        logging.info(f'Downloading video from https://www.youtube.com/watch?v={self._video_id} to {new_filename}')
        yt = YouTube('https://www.youtube.com/watch?v=' + self._video_id)
        filepath = yt.streams.first().download('/Andrew-Klavan-Instragram-Bot/temp_video_storage/', new_filename)
        self._video_path = filepath
        self._video_desc = yt.description
    

    def upload_to_instagram(self) -> None:
        logging.info(f'Passing video ({self._video_title}) to instagram bot')
        insta = instagram.Bot(self._video_path, self._video_title, self._video_desc, self._video_id)
        if insta.failed_4_times():
            logging.error(f'Critical error: attepted to upload video {self._video_title} 4 times and failed')
            subject = 'Klavan Bot | VIDEO UPLOAD ERROR'
            message = f"The video '{self._video_title}' ({self._video_id}) has been attempted to" + \
                    " be uploaded 4 times.\n\nLove,\nBot"
            email(subject, message)
        
        # temp success email
        if insta.success:
            logging.info(f'Successfully upload {self._video_title}')
            sub = 'Andrew Bot | YAY'
            mess = f"We did it!! The video '{self._video_title}' was uploaded!\n\nLove,\nBot"
            email(sub,  mess)

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
        try:
            driver = webdriver.Chrome('chromedriver', options=CHROME_OPTIONS)
            driver.get(LINK)
        except WebDriverException as ex:
            logging.exception(f'Web driver could not connect to the internet, trying again in 10 minutes\n{str(ex)}')
            sleep(600)
            continue

        uploaded_videos = [i[0] for i in reader(open('uploaded_videos.csv', 'r'))]
        video_search = do_search(driver=driver)
        
        new_videos = False
        new_videos_to_do = []

        for item in video_search:
            if item[1] not in uploaded_videos:
                new_videos = True
                new_videos_to_do.append(item)

        if new_videos:
            for video in new_videos_to_do:
                logging.info(f'New video: {video[0]} ({video[1]})')

                new_video = VideoHandler(video[0], video[1])
                new_video.start()

                sleep(10)

            sleep(600) # 600 -> 10 minutes
        else:
            sleep(600) # 600 -> 10 minutes

        driver.close()


def main():
    today = datetime.today() - timedelta(hours=4)
    date = today.strftime('%m/%d/%Y')
    time = today.strftime('%I:%M%p')
    subject = 'Klavan Bot | Server Starting'
    mess = f'Dear Maker,\n\nOn {date} at {time}, I was started and have begun running my rounds.\n\nLove,\nBot'
    email(subject, mess)
    logging.info(f'Server starting...')

    while (True):
        try:
            loop()
        except Exception as ex:
            logging.exception(f'Server failed: {str(ex)}server restarting...')
            sleep(300)


if __name__ == "__main__":
    main()
