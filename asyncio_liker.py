import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from getpass import getuser
from time import sleep
from random import randint

badoo_domain = r"https://badoo.com/"
badoo_url = badoo_domain + r"encounters"
badoo_like_xpath = r'/html/body/div[2]/div[1]/main/div[1]/div/div[1]/section/div/div[2]/div/div[2]/div[1]/div'
badoo_disike_xpath = r'/html/body/div[2]/div[1]/main/div[1]/div/div[1]/section/div/div[2]/div/div[2]/div[2]/div[1]'
badoo_pop_up_xpath = r'/html/body/aside/section'
badoo_messages_xpath = r'/html/body/div[2]/div[1]/aside/div/div/div/div[1]/div/div[3]/div/a[3]'

vk_domain = r"https://vk.com/"
vk_url = vk_domain + r"im?sel=-91050183"
vk_like_xpath = r'/html/body/div[11]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[2]/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div[1]/button/span/img'
vk_disike_xpath = r'/html/body/div[11]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[2]/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div[3]/button/span/img'
vk_pop_up_xpath = r''
vk_last_message_xpath = r'//*[@id="content"]/div/div[1]/div[3]/div[2]/div[3]/div/div/div[2]/div/div[1]/div[last()]'
vk_show_more_users_xpath = r'/html/body/div[11]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[2]/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div[1]'


def get_new_tab(url):
    driver.execute_script(f"window.open('{url}');")
    for tab in driver.window_handles:
        if driver.current_url != url:
            driver.switch_to.window(tab)
    driver.get(url)
    return tab


def skip_pop_up(xpath):
    try:
        WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, xpath)))
        webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    except Exception:
        pass


def swipe_badoo_user(tab, i):
    driver.switch_to.window(tab)
    if i % (randint(5, 8)) != 0:  # Click like for every 3rd user
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, badoo_like_xpath)))
        driver.find_element_by_xpath(badoo_like_xpath).click()
    else:  # click dislike
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, badoo_disike_xpath)))
        driver.find_element_by_xpath(badoo_disike_xpath).click()


def swipe_vk_user(previous_tab, liker_tab):
    driver.switch_to.window(liker_tab)
    flag = 'like' if randint(0, 10) % 3 != 0 else 'dislike'  # 33% chance for dislike
    # No need to wait dislike button, he is not always there and leads to exception
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, vk_like_xpath)))
    if flag == 'dislike':  # Dislike first, if dislike button is no presense - go top like
        elem = driver.find_element_by_xpath(vk_disike_xpath)
        if elem.get_attribute("alt") == '👎':
            elem.click()
        else:
            print('\nAHTUNG 2!\n')
            flag = 'like'
    if flag == 'like':  # click dislike
        elem = driver.find_element_by_xpath(vk_like_xpath)
        if elem.get_attribute("alt") == '❤':
            elem.click()
        else:
            print('\nAHTUNG 1!\n')
    # driver.switch_to.window(previous_tab)


def write_badoo_message():
    driver.get('https://badoo.com/messenger/open')
    users_css_selector = r'.contacts__item.js-contacts-item'
    user_last_message_xpath = './div/div[2]/span[1]'
    message_area_xpath = '//*[@id="t"]'
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, users_css_selector)))
    users = driver.find_elements_by_css_selector(users_css_selector)
    counter = 0
    for user in users[1:]:  # First is you
        WebDriverWait(user, 10).until(EC.presence_of_element_located((By.XPATH, user_last_message_xpath)))
        if 'симпатия' in user.find_element_by_xpath(user_last_message_xpath).text:
            user.click()
            sleep(2)
            WebDriverWait(user, 10).until(EC.presence_of_element_located((By.XPATH, message_area_xpath)))
            message_area = user.find_element_by_xpath(message_area_xpath)
            message_area.send_keys(f'Привет. Как насчет тусить?')
            message_area.send_keys(Keys.ENTER)
            counter += 1
    print(f'Sent messages: {counter}')


async def start_badoo_liker(count):
    tab = get_new_tab(badoo_url)
    for i in range(count):
        if i % 100 == 0:
            print(i)
        skip_pop_up(badoo_pop_up_xpath)
        swipe_badoo_user(tab, i)
        await asyncio.sleep(randint(95, 175) / 100)


async def start_vk_liker(count):
    previous_tab = driver.current_url  # Tab to return after action
    liker_tab = get_new_tab(vk_url)
    for i in range(count):
        last_message = driver.find_element_by_xpath(vk_last_message_xpath)
        if 'Есть взаимная симпатия!' in last_message.text:
            links1, links2 = last_message.find_elements_by_css_selector("a"), last_message.find_elements_by_css_selector(".a")
            print(links1, links2)
            print(type(links1, links2))
            # print(type(last_message.get_attribute('href')))
            if '1. Оценить еще кого-то.' in last_message.text:
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, vk_show_more_users_xpath)))
                driver.find_element_by_xpath(vk_show_more_users_xpath).click()
                # elem.click()
        elif '1. Продолжить просмотр анкет' in last_message.text:
            WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.XPATH, vk_show_more_users_xpath)))
            driver.find_element_by_xpath(vk_show_more_users_xpath).click()
        elif 'Слишком много лайков' in last_message.text:
            return
        # skip_pop_up()
        swipe_vk_user(previous_tab, liker_tab)
        await asyncio.sleep(randint(225, 375) / 100)


async def main(tasks):
    await asyncio.gather(*tasks)  # Believe me


def do_opt(opt, count):
    if opt == '1':
        asyncio.run(main((start_badoo_liker(count),)))  # Must be a tuple only
    elif opt == '2':
        asyncio.run(main((start_vk_liker(count),)))  # Must be a tuple only
    elif opt == '3':
        asyncio.run(main((start_vk_liker(count[0]), start_badoo_liker(count[1]))))
    else:
        write_badoo_message()


def get_count(opt):
    get_count = lambda liker: int(input(f'Give me count for {liker} swipes\n'))
    if opt == '1':
        return get_count('badoo')
    elif opt == '2':
        return get_count('vk')
    elif opt == '3':
        return get_count('badoo'), get_count('vk')
    else:
        return


if __name__ == '__main__':
    driver_path = fr"C:\Users\{getuser()}\Desktop\selenium_files\chromedriver_v_83.exe"
    profile_path = fr'C:\Users\{getuser()}\AppData\Local\Google\Chrome\User Data'
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={profile_path}")
    while True:
        opt = input('Type 1 for badoo, 2 for vk, 3 for both, 4 for badoo message\n')
        count = get_count(opt)
        driver = webdriver.Chrome(executable_path=driver_path, options=options) if 'driver' not in globals() else driver
        do_opt(opt, count)
        if input('Done! Start again? (press Enter)\n') != '':
            break
