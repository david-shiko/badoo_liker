from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from time import sleep as time_sleep
from random import uniform as random_uniform
from requests import get as requests_get
from zipfile import ZipFile as zipfile_ZipFile
from io import BytesIO as io_BytesIO
from tqdm import tqdm
from json import loads as json_loads
from json import dumps as json_dumps

# # # config # # #
badoo_domain = r"https://badoo.com"
badoo_matches_url = f'{badoo_domain}/encounters'
badoo_messages_url = f'{badoo_domain}/messenger/open'
badoo_messages_xpath = r'/html/body/div[2]/div[1]/aside/div/div/div/div[1]/div/div[3]/div/a[3]'

vk_domain = r"https://vk.com/"
vk_url = vk_domain + r"im?sel=-91050183"
vk_like_xpath = r'/html/body/div[11]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[2]/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div[1]/button'
vk_disike_xpath = r'/html/body/div[11]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div[1]/div[3]/div[2]/div[4]/div[2]/div[4]/div[2]/div[3]/div/div/div[1]/div[1]/div/div[1]/div/div/div[3]/button'
vk_message_xpath = r'//*[@id="content"]/div/div[1]/div[3]/div[2]/div[3]/div/div/div[2]/div/div[1]/div[last()]'
vk_pop_up_xpath = r''


def download_chromedriver(file_obj):
    try:
        latest_stable_driver_ver_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        latest_stable_driver_ver = requests_get(latest_stable_driver_ver_url).content.decode()
        response = requests_get(f'https://chromedriver.storage.googleapis.com/'
                                f'{latest_stable_driver_ver}/chromedriver_win32.zip')
        total_length = int(response.headers.get('content-length'))
        with tqdm(desc='chromedriver.zip', total=total_length, unit='iB', unit_scale=True, unit_divisor=1024, ) as bar:
            for data in response.iter_content(chunk_size=1024):
                bar.update(file_obj.write(data))  # 'write' returns size of writen bytes
        return file_obj
    except Exception as e:
        raise Exception('Can not automatically download chrome driver. '
                        'You can download it manually, check "https://chromedriver.chromium.org/downloads"')


def extract_zip(downloaded_file_obj):
    try:
        with zipfile_ZipFile(downloaded_file_obj) as zip_obj:
            # Iterate over meta info to find out driver filename (default "chromedriver.exe")
            zip_obj.extractall()
            return [file_info.filename for file_info in zip_obj.infolist()]  # One of names is name of chromedriver
    except Exception as e:
        with open('chromedriver.zip', 'wb') as empty_file_obj:  # Save downloaded zip file to disk
            downloaded_file_obj.seek(0)  # Set pointer to first symbol before reading (and writing)
            empty_file_obj.write(downloaded_file_obj.read())
        raise Exception('Can not to extract zip archive (chromedriver). You can do it manually')


def get_chromedriver():
    confirm_download = input('Can not find "chromedriver.exe" file in the current directory. '
                             'It is requiring for the script working. '
                             'PLease specify path to chromedriver manually '
                             'or press "Enter" to download it automatically')
    possible_driver_paths = [confirm_download]
    if confirm_download == '':
        with io_BytesIO() as memory_file_obj:  # io_BytesIO - convert string to file-like object; b -Binary
            chromedriver_zip = download_chromedriver(memory_file_obj)  # Memory object
            possible_driver_paths.extend(extract_zip(chromedriver_zip))
    for path in possible_driver_paths:  # Try every file from zip archive as chrome_driver path
        try:
            return webdriver.Chrome(executable_path=path)
        except Exception:
            pass


def swipe_badoo_user():
    # Send key to whole page instead of particular element (Skip ads pop up if exists). Why "perform" ?
    webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
    if random_uniform(0, 4) > 1:  # Random value for clicking like to every 4rd user
        webdriver.ActionChains(driver).send_keys(1).perform()  # 1 is like, 2 is dislike
    else:  # click dislike
        webdriver.ActionChains(driver).send_keys(2).perform()  # 1 is like, 2 is dislike


# def swipe_vk_user(i):  # Not in use
#     if 'Есть взаимная симпатия!' in driver.find_element_by_xpath(vk_message_xpath).text:
#         print(driver.find_element_by_xpath(vk_message_xpath).get_attribute("href"))
#     if i % (randint(3, 6)) != 0:  # Click like for every 3-6 user
#         WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, vk_like_xpath)))
#         elem = driver.find_element_by_xpath(vk_like_xpath)
#         elem.click()
#     else:  # click dislike
#         WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, vk_disike_xpath)))
#         elem = driver.find_element_by_xpath(vk_disike_xpath)
#         if elem.text != 'Я больше не хочу никого искать.':
#             elem.click()
#         else:
#             link_xpath = '//*[@id="content"]/div/div[1]/div[3]/div[2]/div[3]/div/div/div[2]/div/div[1]/div[62]/div[2]/ul/li/div[3]/a[1]'
#             link = driver.find_element_by_xpath(link_xpath)
#             print(link.get_attribute('href'))
#             driver.find_element_by_xpath(vk_like_xpath).click()


def scroll_down_users_elem(users_parent_elem):
    """
    Logic of func:
    To load all users you need to reach bottom of element with users. Possible way to do it:
        1. Get location of first element.
        2. Focus on this element.
        3. Press page down button multiple times.
    :return:
    """
    shift_elem_old_location = None
    shift_elem = users_parent_elem.find_element_by_class_name(name='contacts__item.js-contacts-item')
    shift_elem.click()
    while shift_elem_old_location != shift_elem.location:
        shift_elem_old_location = shift_elem.location
        webdriver.ActionChains(driver).send_keys(Keys.PAGE_DOWN).perform()
        time_sleep(1)  # Wait browser to update location
    pass


def badoo_send_message(text):
    sent_messages_counter = 0
    login(cookie_filename='cookies_badoo_(keep_this_file_save_!_).txt', url=badoo_messages_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator=(By.CLASS_NAME, 'contacts__users')))
    users_parent_elem = driver.find_element_by_class_name(name='contacts__users')  # To exclude itself from list
    scroll_down_users_elem(users_parent_elem=users_parent_elem)
    users = users_parent_elem.find_elements_by_class_name(name='contacts__item.js-contacts-item')
    for user in users:
        try:
            # Sort by a default message after a match (no need to open a dialog)
            if any(word in user.text for word in ('симпатия', 'хочет общаться')):
                user.click()  # Open a chat with a user
                time_sleep(1)  # No wait because of old element whit same id will be trigger (?)
                driver.find_element_by_id(id_='t').send_keys(text, Keys.ENTER)
                # Skip pop up AFTER sending a message after pressing an "ENTER" key)
                time_sleep(1)
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                sent_messages_counter += 1
        except Exception as e:
            print(e)
    print(f'Sent messages: {sent_messages_counter}')


def start_badoo_liker(count):
    login('cookies_badoo_(keep_this_file_save_!_).txt', url=badoo_matches_url)
    for i in tqdm(iterable=range(int(count)), desc='swipes done', unit='swipe'):  # tqdm for progress bar
        try:
            swipe_badoo_user()
            time_sleep(random_uniform(1.0, 2.0))
        except Exception as e:
            print(e)


def login(cookie_filename, url):
    while True:
        try:
            driver.get(url)
            with open(cookie_filename, 'r') as cookie_file_obj:  # First try to load cookie
                for cookie in json_loads(cookie_file_obj.read()):
                    driver.add_cookie(cookie)
            driver.get(url)  # reload page with a new cookie (no refresh because of possible redirect by cookies)
            # throw error if no "sign out" icon
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'sidebar-info__signout')))
            with open(cookie_filename, 'w') as cookie_file_obj:  # save cookie after a correct login
                cookie_file_obj.write(json_dumps(driver.get_cookies()))
            return
        except FileNotFoundError as e:
            print('Can not to find "cookies_badoo_(keep_this_file_save_!_).txt" file'
                  f'Error: {e}')
            print('it seems you are not logged in, for the program to work, you need to log in to the site.\n'
                  'Waiting until you are logged in...'
                  f'Error: {e}')
        except TimeoutException as e:
            print('it seems you are not logged in, for the program to work, you need to log in to the site.\n'
                  'Waiting until you are logged in...'
                  f'Error: {e}')


# def start_vk_liker(count):  # Not in use
#     print(vk_url)
#     driver.get(vk_url)
#     for i in range(int(count)):
#         try:
#             swipe_vk_user(i)
#             time_sleep(randint(175, 325) / 100)
#         except Exception as e:
#             print(e)


if __name__ == '__main__':
    #input(os.getcwd())
    qu_1 = 'PLease give me a count of swipes\n'
    qu_2 = 'PLease specify the text to send for\n'
    opt = input('Please select 1 for swipes, 2 for send messages to all new matches\n')
    func, arg = (start_badoo_liker, input(qu_1),) if opt == '1' else (badoo_send_message, input(qu_2),)
    try:
        driver = webdriver.Chrome(executable_path='chromedriver.exe')
    except WebDriverException:
        driver = get_chromedriver()
    except Exception as e:
        raise Exception('No "chromedriver.exe" is supplied, can not go on, quiting ...')  # Error if no correct driver
    func(arg)
    driver.quit()
    print('Done!')
