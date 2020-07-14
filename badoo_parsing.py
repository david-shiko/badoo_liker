from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

driver_path = r"C:\Users\dsb32\Desktop\selenium_files\chromedriver_v_83.exe"
profile_path = r"user-data-dir=C:\Users\dsb32\AppData\Local\Google\Chrome\User Data"

domain = r"https://badoo.com/"
url = domain + r"encounters"
like_xpath = r'/html/body/div[2]/div[1]/main/div[1]/div/div[1]/section/div/div[2]/div/div[2]/div[1]/div'
dislike_xpath = r'/html/body/div[2]/div[1]/main/div[1]/div/div[1]/section/div/div[2]/div/div[2]/div[2]/div[1]'
pop_up_xpath = r'/html/body/aside/section'

options = webdriver.ChromeOptions()
options.add_argument(profile_path)
# options.add_argument('--headless')
driver = webdriver.Chrome(executable_path=driver_path, options=options)

driver.get(url)
for i in range(100):
    try:
        try:  # Skip pop up window if there
            cond = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, pop_up_xpath)))  # 1 - delay
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
        except Exception as e:
            pass
        if not i % 3 == 0:  # Click like for every 3rd user
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, like_xpath)))
            like_button = driver.find_element_by_xpath(like_xpath).click()
        else:  # click dislike
            WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, dislike_xpath)))  # 1 - delay
            dislike_button = driver.find_element_by_xpath(dislike_xpath).click()
    except Exception as e:
        print(e)

print('Done!')
