from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import logging
from datetime import datetime, timedelta
from time import sleep

logging.basicConfig(filename='/home/ryan/fileshare/klavan_bot_logs.log', level=logging.DEBUG)

FAILED_UPLOADS = {}

class Bot(object):
    def __init__(self, video_path: str, video_title: str, video_desc: str, video_id: str) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.driver = webdriver.Chrome('chromedriver', options=chrome_options)
        self.video_path = video_path
        self.video_title = video_title
        self.video_desc = video_desc
        self.video_id = video_id

        self.too_many_upload_attempts = False

        # temp success flag
        self.success = False

        self.start_upload()


    def start_upload(self):
        try:
            self.driver.get('https://www.instagram.com/tv/upload')
            
            sleep(6)

            at_login = str(self.driver.current_url).find('login') != -1
            if at_login:
                self.do_login()
                sleep(10)
            else:
                raise Exception('Selenium did not go to login page')
            
            at_upload_page = str(self.driver.current_url).find('upload') != -1
            if not at_upload_page:
                raise Exception('Selenium did not go to upload page')
                
            
            # upload video
            upload_vid = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/form/div/div[1]/label/input')
            upload_vid.send_keys(self.video_path)

            # input video title and description
            title = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/form/div/div[2]/div[4]/div/div/input')
            title.send_keys(self.video_title)
            desc = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/form/div/div[2]/div[5]/div/div/textarea')
            desc.send_keys(self.video_desc)

            # finish and post
            sleep(15)
            post_button = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/form/div/div[2]/div[9]/button')
            post_button.click()

            # wait for upload to finish then close
            sleep(300)
            self.tearDown()

            # write new video to uploaded list
            with open('uploaded_videos.csv', 'a') as uploaded_vids:
                uploaded_vids.write(self.video_id + '\n')

            # remove from failed uploads if successfully uploaded video
            if self.video_id in FAILED_UPLOADS.keys():
                FAILED_UPLOADS.pop(self.video_id)

            self.success = True

            today = datetime.today() - timedelta(hours=4)
            date = today.strftime('%m/%d/%Y')
            time = today.strftime('%I:%M%p')
            logging.info(f"[{date} {time}] Successfully uploaded video '{self.video_title}' ({self.video_id})!")
        except Exception as ex:
            today = datetime.today() - timedelta(hours=4)
            date = today.strftime('%m/%d/%Y')
            time = today.strftime('%I:%M%p')
            logging.error(f'[{date} {time}] While uploading video {self.video_title} ({self.video_id}), an error occurred: {str(ex)}')

            if self.video_id in FAILED_UPLOADS.keys():
                FAILED_UPLOADS[self.video_id] += 1
            else:
                FAILED_UPLOADS[self.video_id] = 1

            # check if video has been attempted more than 4 times
            if FAILED_UPLOADS[self.video_id] == 4:
                logging.error(f'[{date} {time}] Failed to upload video {self.video_title} ({self.video_id}) 4 times')
                self.too_many_upload_attempts = True


    def failed_4_times(self) -> bool:
        return self.too_many_upload_attempts


    def do_login(self) -> None:
        try:
            with open('/passcodes/insta_creds.key', 'r') as creds_file:
                username = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
                username.send_keys(creds_file.readline().strip())

                password = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
                password.send_keys(creds_file.readline().strip())

                password.submit()

                sleep(16)

                not_now = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button')
                not_now.click()
        except NoSuchElementException as ex:
            today = datetime.today() - timedelta(hours=4)
            date = today.strftime('%m/%d/%Y')
            time = today.strftime('%I:%M%p')
            logging.error(f'[{date} {time}] While uploading video {self.video_title} ({self.video_id}), an error occurred: {str(ex)}')


    def tearDown(self) -> None:
        self.driver.close()
