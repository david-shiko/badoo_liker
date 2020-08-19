import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep
from random import randint


opt = int(input('1 for badoo, 2 for vk, 3 for badoo messages\n'))
count = int(input('Give me a count of swipes\n'))

driver_path = r"C:\Users\dsb32\Desktop\selenium_files\chromedriver_v_83.exe"
profile_path = r"user-data-dir=C:\Users\dsb32\AppData\Local\Google\Chrome\User Data"

badoo_domain = r"https://badoo.com/"
badoo_url = badoo_domain + r"encounters"
badoo_like_xpath = r'/html/body/div[2]/div[1]/main/div[1]/div/div[1]/section/div/div[2]/div/div[2]/div[1]/div'
badoo_disike_xpath = r'/html/body/div[2]/div[1]/main/div[1]/div/div[1]/section/div/div[2]/div/div[2]/div[2]/div[1]'
badoo_pop_up_xpath = r'/html/body/aside/section'
badoo_messages_xpath = r'/html/body/div[2]/div[1]/aside/div/div/div/div[1]/div/div[3]/div/a[3]'

vk_domain = r"https://vk.com/"
vk_url = vk_domain + r"im?sel=-91050183"
vk_like_xpath = r'/html/body/div[11]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[2]/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div[1]/button'
vk_disike_xpath = r'/html/body/div[11]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[2]/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div[3]/button'
vk_message_xpath = r'//*[@id="content"]/div/div[1]/div[3]/div[2]/div[3]/div/div/div[2]/div/div[1]/div[last()]'
vk_pop_up_xpath = r''

options = webdriver.ChromeOptions()
options.add_argument(profile_path)
driver = webdriver.Chrome(executable_path=driver_path, options=options)


def skip_pop_up(element):
    try:
        WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, element)))
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except Exception as e:
        pass


def swipe_badoo_user(i):
    if i % (randint(5, 8)) != 0:  # Click like for every 3rd user
        WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, badoo_like_xpath)))
        driver.find_element_by_xpath(badoo_like_xpath).click()
    else:  # click dislike
        WebDriverWait(driver, 0.5).until(EC.presence_of_element_located((By.XPATH, badoo_disike_xpath)))
        driver.find_element_by_xpath(badoo_disike_xpath).click()


def swipe_vk_user(i):
    if 'Есть взаимная симпатия!' in driver.find_element_by_xpath(vk_message_xpath).text:
        print(driver.find_element_by_xpath(vk_message_xpath).get_attribute("href"))
    if i % (randint(3, 6)) != 0:  # Click like for every 3-6 user
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, vk_like_xpath)))
        elem = driver.find_element_by_xpath(vk_like_xpath)
        elem.click()
    else:  # click dislike
        WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, vk_disike_xpath)))
        elem = driver.find_element_by_xpath(vk_disike_xpath)
        if elem.text != 'Я больше не хочу никого искать.':
            elem.click()
        else:
            link_xpath = '//*[@id="content"]/div/div[1]/div[3]/div[2]/div[3]/div/div/div[2]/div/div[1]/div[62]/div[2]/ul/li/div[3]/a[1]'
            link = driver.find_element_by_xpath(link_xpath)
            print(link.get_attribute('href'))
            driver.find_element_by_xpath(vk_like_xpath).click()


def write_badoo_message():
    driver.get('https://badoo.com/messenger/open')
    users_css_selector = r'.contacts__item.js-contacts-item'
    user_last_message_xpath = './div/div[2]/span[1]'
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, users_css_selector)))
    users = driver.find_elements_by_css_selector(users_css_selector)
    counter = 0
    for user in users[1:]:  # First is you
        sleep(1)
        WebDriverWait(user, 10).until(EC.presence_of_element_located((By.XPATH, user_last_message_xpath)))
        if 'симпатия' in user.find_element_by_xpath(user_last_message_xpath).text:
            print(f"curent user id: {user.get_property('id')}")
            sleep(1)
            user.click()
            WebDriverWait(user, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="t"]')))
            message_area = user.find_element_by_xpath('//*[@id="t"]')
            message_area.send_keys(f'Привет. Хочешь потусить?')
            message_area.send_keys(Keys.ENTER)
            counter += 1
    print(f'Sent messages: {counter}')


def start_badoo_liker():
    driver.get(badoo_url)
    for i in range(count):
        if i % 100 == 0:
            print(i)
        try:
            skip_pop_up(badoo_pop_up_xpath)
            sleep(randint(95, 175) / 100)
            swipe_badoo_user(i)
        except Exception as e:
            print(e)


def start_vk_liker():
    print(vk_url)
    driver.get(vk_url)
    for i in range(count):
        try:
            # skip_pop_up()
            swipe_vk_user(i)
            sleep(randint(175, 325) / 100)
        except Exception as e:
            print(e)


start_badoo_liker() if opt == 1 else start_vk_liker() if opt == 2 else write_badoo_message()
print('Done!')

