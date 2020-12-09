from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement

LINK = 'https://www.youtube.com/c/AndrewKlavan/videos'

CHROME_OPTIONS = Options()
CHROME_OPTIONS.add_argument("--headless")
CHROME_OPTIONS.add_argument("--no-sandbox")
CHROME_OPTIONS.add_experimental_option('excludeSwitches', ['enable-logging'])

while True:
    driver = webdriver.Chrome('chromedriver.exe', options=CHROME_OPTIONS)
    driver.get(LINK)

    v_info = driver.find_elements_by_id('video-title')[:3]
    video_lenghts = [i for i in driver.find_elements_by_tag_name('span') if str(i.get_attribute('class')) == 'style-scope ytd-thumbnail-overlay-time-status-renderer'][:3]
    videos = [(v_info[i].text, str(v_info[i].get_attribute('href')).split('=')[1], int(video_lenghts[i].text.split(':')[0])) for i in range(3)]
    # for ele in :
    #     videos.append([ele.text, str(ele.get_attribute('href')).split('=')[1]])


    # for i in range(3):
    #     videos[i].append(int(video_lenghts[i].text.split(':')[0]))

    print(videos)

    driver.close()

    sleep(5)



# for ele in driver.find_elements_by_class_name('style-scope ytd-thumbnail-overlay-time-status-renderer'):
#     # ele = WebElement(ele)
#     print(ele.tag_name)

# style-scope ytd-thumbnail-overlay-time-status-renderer
# print(videos)