from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from time import sleep

logging.basicConfig(filename='/home/ryan/fileshare/klavan_bot_logs.log',
                    level=logging.INFO,
                    datefmt='%m/%d/%Y %I:%M %p',
                    format='[%(asctime)s %(filename)s %(funcName)s():%(lineno)s] %(levelname)s: %(message)s')

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
        self.video_desc = video_desc + "\n\n#theandrewklavanshow #andrewklavan #andrewklavanshow"
        self.video_id = video_id

        self.too_many_upload_attempts = False

        self.start_upload()


    def click_button(self, xpath: str, button_desc: str) -> bool:
        """Click an element.

        Make sure to confirm the button has been loaded
        before using this to click an element.

        Args:
            xpath (str): xpath to button
            button_desc (str): for error messages

        Returns:
            bool: true if click was successful, false if element could not be found
        """
        try:
            element = self.driver.find_element_by_xpath(xpath)
            element.click()
            return True
        except NoSuchElementException as ex:
            logging.exception(f'when clicking the button at operation {button_desc}, the xpath could not be located and was not clicked')
            return False


    def start_upload(self):
        try:
            logging.info(f"'{self.video_id}' Starting upload")
            self.driver.get('https://www.instagram.com/tv/upload')
            
            sleep(6)

            logging.info(f"'{self.video_id}' At login page")
            at_login = str(self.driver.current_url).find('login') != -1
            if at_login:
                self.do_login()
            else:
                raise Exception('Selenium did not go to login page')
            
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="react-root"]/section/main/div/form/div/div[1]/label/input'))
            )
            
            logging.info(f"'{self.video_id}' At upload page")
            at_upload_page = str(self.driver.current_url).find('upload') != -1
            if not at_upload_page:
                raise Exception('Selenium did not go to upload page')
            
            # upload video
            logging.info(f"'{self.video_id}' Entering video into form")
            upload_vid = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/form/div/div[1]/label/input')
            upload_vid.send_keys(self.video_path)

            # input video title and description
            logging.info(f"'{self.video_id}' Entering title into form")
            title = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/form/div/div[2]/div[4]/div/div/input')
            title.send_keys(self.video_title)
            logging.info(f"'{self.video_id}' Entering description into form")
            desc = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/form/div/div[2]/div[5]/div/div/textarea')
            desc.send_keys(self.video_desc)

            # finish and post
            sleep(3)
            logging.info(f"'{self.video_id}' submitting video")
            button_desc = 'posting video'
            click_result = self.click_button('//*[@id="react-root"]/section/main/div/form/div/div[2]/div[10]/button', button_desc)
            if not click_result: raise NoSuchElementException(f'button for operation {button_desc} was not clicked')

            # wait for upload to finish then close
            logging.info(f"'{self.video_id}' Waiting 5 minutes then closing down session")
            sleep(300)
            self.tearDown()

            # write new video to uploaded list
            logging.info(f"'{self.video_id}' Adding video to uploaded videos list")
            with open('uploaded_videos.csv', 'a') as uploaded_vids:
                uploaded_vids.write(self.video_id + '\n')

            # remove from failed uploads if successfully uploaded video
            if self.video_id in FAILED_UPLOADS.keys():
                FAILED_UPLOADS.pop(self.video_id)

            self.success = True

            logging.info(f"Successfully uploaded video '{self.video_title}' ({self.video_id})!")
        except Exception as ex:
            logging.exception(f'While uploading video {self.video_title} ({self.video_id}), an error occurred: {str(ex)}')

            if self.video_id in FAILED_UPLOADS.keys():
                FAILED_UPLOADS[self.video_id] += 1
            else:
                FAILED_UPLOADS[self.video_id] = 1

            # check if video has been attempted more than 4 times
            if FAILED_UPLOADS[self.video_id] == 4:
                self.too_many_upload_attempts = True


    def failed_4_times(self) -> bool:
        return self.too_many_upload_attempts


    def do_login(self) -> None:
        with open('/passcodes/insta_creds.key', 'r') as creds_file:
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="loginForm"]/div/div[1]/div/label/input'))
            )

            username = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
            username.send_keys(creds_file.readline().strip())

            password = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
            password.send_keys(creds_file.readline().strip())

            password.submit()

            WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="react-root"]/section/main/div/div/div/div/button'))
            )

            button_desc = 'not now button for saving password after logging in'
            click_result = self.click_button('//*[@id="react-root"]/section/main/div/div/div/div/button', button_desc)
            if not click_result: raise NoSuchElementException(f'button for operation {button_desc} was not clicked')


    def tearDown(self) -> None:
        self.driver.close()

