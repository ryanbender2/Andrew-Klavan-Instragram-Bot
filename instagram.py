from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep


class Bot(object):
    def __init__(self, video_path: str, video_title: str, video_desc: str, video_id: str) -> None:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        self.driver = webdriver.Chrome('chromedriver.exe', options=chrome_options)
        self.video_path = video_path
        self.video_title = video_title
        self.video_desc = video_desc
        self.video_id = video_id

        self.start_upload()


    def start_upload(self):
        try:
            self.driver.get('https://www.instagram.com/tv/upload')
            
            sleep(3)

            at_login = str(self.driver.current_url).find('login') != -1
            if at_login:
                self.do_login()
                sleep(5)
            
            at_upload_page = str(self.driver.current_url).find('upload') != -1
            if not at_upload_page:
                # sleep(10)
                # retry
                print('not at upload page')
                
            
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

            print("successfully uploaded video")
        except:
            pass


    def do_login(self) -> None:
        try:
            with open('C:\MSI\insta_creds.key', 'r') as creds_file:
                username = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[1]/div/label/input')
                username.send_keys(creds_file.readline().strip())

                password = self.driver.find_element_by_xpath('//*[@id="loginForm"]/div/div[2]/div/label/input')
                password.send_keys(creds_file.readline().strip())

                password.submit()

                sleep(8)

                not_now = self.driver.find_element_by_xpath('//*[@id="react-root"]/section/main/div/div/div/div/button')
                not_now.click()


        except NoSuchElementException as ex:
            print('element not found')


    def tearDown(self) -> None:
        self.driver.close()