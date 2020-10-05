from datetime import datetime, timedelta
from youtube_api import YouTubeDataAPI
from instabot import Bot
from csv import reader
from threading import Thread
from time import sleep
import logging

YOUTUBE = YouTubeDataAPI(open("C:\\MSI\\bot_key.key", 'r').readline())


class VideoHandler(Thread):
    """Update the list of videos that's been
        loaded to instagram.

    """
    _video_id: str

    def __init__(self, video_id: str) -> None:
        self._video_id = video_id

    def run(self) -> None:
        one_day_ago = datetime.today() - timedelta(days=5)
        video_search = [i['video_id'] for i in YOUTUBE.search(channel_id='UCyhEZKz-LOwgktptEOh6_Iw', published_after=one_day_ago, order_by='date')]
        uploaded_videos = [i[0] for i in reader(open('uploaded_videos.csv', 'r'))]

        with open('uploaded_videos.csv', 'a') as file:
            for video in video_search:
                if video not in uploaded_videos:
                    file.write(video + '\n')


def main():
    while (True):
        ten_minutes_ago = datetime.today() - timedelta(minutes=10)
        uploaded_videos = [i[0] for i in reader(open('uploaded_videos.csv', 'r'))]
        video_search = [i['video_id'] for i in YOUTUBE.search(channel_id='UCyhEZKz-LOwgktptEOh6_Iw', published_after=ten_minutes_ago, order_by='date')]
        
        if not video_search:
            print("no new videos")
            sleep(10) # 600 -> 10 minutes
        else:
            for vid in video_search:
                if vid not in uploaded_videos:
                    VideoHandler(vid)
            

if __name__ == "__main__":
    main()