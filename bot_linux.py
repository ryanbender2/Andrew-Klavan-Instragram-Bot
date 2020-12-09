from datetime import datetime
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

LINK = 'https://www.youtube.com/c/AndrewKlavan/videos'
EMAIL_PASS = open("/passcodes/email_pass.key", 'r').readline()

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])


def email(subject: str, body: str) -> None:
    global EMAIL_PASS
    try:
        email_server = SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
        email_server.login('ak.insta.contact@gmail.com', EMAIL_PASS)

        logging.info(f'Sending an email -- {subject}')

        message = f'Subject: {subject}\n\n{body}'
        email_server.sendmail('ak.insta.contact@gmail.com', 'ryan.bender.general@gmail.com', message)
    except Exception as ex:
        logging.exception(f'Email failed to send: {body}\n{str(ex)}')


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


    def run(self) -> None:
        try:
            self.download_video(self._generated_filename)
            self.upload_to_instagram()
        except KeyError as ex:
            logging.exception(f"For video {self._video_title}, downloading failed: {str(ex)}\n'{self._video_title}' will not upload")


def do_search(driver: webdriver.Chrome) -> list:
    """Get the video title, ID, and lenght in minutes of the
        three latest videos from Klavan.

    Args:
        driver (webdriver.Chrome): chrome driver

    Returns:
        list: 3 tuples of latest videos info
                (example item: ("LOL: CNN's Chris Cuomo PRAISES Biden For the Most BIZARRE Reason", 'nTOWt4COAnM', 7))
    """
    v_info = driver.find_elements_by_id('video-title')[:3]
    video_lenghts = [i for i in driver.find_elements_by_tag_name('span') if str(i.get_attribute('class')) == 'style-scope ytd-thumbnail-overlay-time-status-renderer'][:3]
    return [(v_info[i].text, str(v_info[i].get_attribute('href')).split('=')[1], int(video_lenghts[i].text.split(':')[0])) for i in range(3)]


def loop() -> None:
    global CHROME_OPTIONS
    global LINK

    max_video_lenght = 30 # in minutes, this sets the max lenght a video can be to be uploaded

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
            if item[1] not in uploaded_videos: # item[1] is the video id (str)
                if item[2] <= max_video_lenght: # item[2] is the video lenght
                    new_videos = True
                    new_videos_to_do.append(item)
                else:
                    # add video to the uploaded list because
                    # the video is too long for upload
                    logging.info(f'The video {item[0]} is not being uploaded because it is too long with' \
                        + f' the lenght being {item[2]} minutes and the max being {max_video_lenght} minutes')
                    with open('uploaded_videos.csv', 'a') as uploaded_vids:
                        uploaded_vids.write(item[1] + '\n')


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
    today = datetime.today()
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
