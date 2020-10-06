from datetime import datetime, timedelta
from youtube_api import YouTubeDataAPI
from pytube import YouTube
from csv import reader
from threading import Thread
from time import sleep
from random import randint
import ssl
from smtplib import SMTP_SSL
import logging

EMAIL_PASS = open("C:\\MSI\\email_pass.key", 'r').readline()
EMAIL_SERVER = SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context())
EMAIL_SERVER.login('ak.insta.contact@gmail.com', EMAIL_PASS)

def email(subject: str, body: str) -> None:
    message = f'Subject: {subject}\n\n{body}'
    EMAIL_SERVER.sendmail('ak.insta.contact@gmail.com', 'ryan.bender.general@gmail.com', message)


class VideoHandler(Thread):
    """Update the list of videos that's been
        loaded to instagram.

    """
    _video_id: str
    _video_path: str

    def __init__(self, video_id: str) -> None:
        super().__init__()

        self._video_id = video_id

        date = datetime.today().strftime('%m-%d-%Y')
        filename = f'temp{randint(10000, 99999)}_{date}'
        self._download_video(filename)

    def _download_video(self, new_filename: str) -> None:
        yt = YouTube('https://www.youtube.com/watch?v=' + self._video_id)
        filepath = yt.streams.first().download('C:\\Users\\ryanb\\OneDrive\\Documents\\' +
                'GitHub\\Andrew-Klavan-Instragram-Bot\\temp_video_storage\\', new_filename)
        self._video_path = filepath

    def run(self) -> None:
        # with open('uploaded_videos.csv', 'a') as file:
        #     for video in video_search:
        #         if video not in uploaded_videos:
        #             file.write(video + '\n')
        print(self._video_id)
        print(self._video_path)


def main():
    youtube = YouTubeDataAPI(open("C:\\MSI\\bot_key.key", 'r').readline())

    while (True):
        ten_minutes_ago = datetime.today() - timedelta(minutes=10)
        uploaded_videos = [i[0] for i in reader(open('uploaded_videos.csv', 'r'))]
        video_search = [i['video_id'] for i in youtube.search(channel_id='UCyhEZKz-LOwgktptEOh6_Iw', published_after=ten_minutes_ago, order_by='date')]
        
        if not video_search:
            print("no new videos")
            sleep(10) # 600 -> 10 minutes
        else:
            for vid in video_search:
                if vid not in uploaded_videos:
                    VideoHandler(vid)
            

def testing():
    # some = _youtube.search(channel_id='UCyhEZKz-LOwgktptEOh6_Iw', published_after=one_day_ago, order_by='date')
    # print(some)
    pass


if __name__ == "__main__":
    # today = datetime.today()
    # date = today.strftime('%m/%d/%Y')
    # time = today.strftime('%I:%M %p')
    # subject = 'Klavan Bot | INFO'
    # mess = f'Dear Maker,\n\nOn {date} at {time}, I was started and have begun running my rounds.\n\nLove,\nBot'
    # email(subject, mess)

    # main()
    testing()