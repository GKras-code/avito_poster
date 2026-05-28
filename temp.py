import json
from datetime import datetime
import time
import undetected_chromedriver as uc 
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.support.ui import WebDriverWait
from random import randint, uniform
from selenium.webdriver.common.action_chains import ActionChains
import yandex_gpt
import yandex_gpt_async
import asyncio
import bot_ozon
import sys, traceback
from loguru import logger
from pyvirtualdisplay import Display


def open_file():
    with open('answer_dict_ozon.json', 'r', encoding='utf-8') as file:
        try:
            answer_dict_ozon = json.load(file)
        except json.JSONDecodeError:           
            answer_dict_ozon = {}
        return answer_dict_ozon
    
def save_file(answer_dict_ozon):
    with open('answer_dict_ozon.json', 'w', encoding='utf-8') as file:
        json.dump(answer_dict_ozon, file, ensure_ascii=False, indent=4)

def get_driver():
    cookies = {
        '__Secure-ab-group': '68',
        'xcid': 'cad344aacf79bde3b12e5f3023c85bd0',
        '__Secure-ext_xcid': 'cad344aacf79bde3b12e5f3023c85bd0',
        'guest': 'true',
        'x-o3-language': 'ru',
        'rfuid': 'NjkyNDcyNDUyLDEyNC4wNDM0NzUyNzUxNjA3NCwxMDI4MjM3MjIzLC0xLC05ODc0NjQ3MjQsVzNzaWJtRnRaU0k2SWxCRVJpQldhV1YzWlhJaUxDSmtaWE5qY21sd2RHbHZiaUk2SWxCdmNuUmhZbXhsSUVSdlkzVnRaVzUwSUVadmNtMWhkQ0lzSW0xcGJXVlVlWEJsY3lJNlczc2lkSGx3WlNJNkltRndjR3hwWTJGMGFXOXVMM0JrWmlJc0luTjFabVpwZUdWeklqb2ljR1JtSW4wc2V5SjBlWEJsSWpvaWRHVjRkQzl3WkdZaUxDSnpkV1ptYVhobGN5STZJbkJrWmlKOVhYMHNleUp1WVcxbElqb2lRMmh5YjIxbElGQkVSaUJXYVdWM1pYSWlMQ0prWlhOamNtbHdkR2x2YmlJNklsQnZjblJoWW14bElFUnZZM1Z0Wlc1MElFWnZjbTFoZENJc0ltMXBiV1ZVZVhCbGN5STZXM3NpZEhsd1pTSTZJbUZ3Y0d4cFkyRjBhVzl1TDNCa1ppSXNJbk4xWm1acGVHVnpJam9pY0dSbUluMHNleUowZVhCbElqb2lkR1Y0ZEM5d1pHWWlMQ0p6ZFdabWFYaGxjeUk2SW5Ca1ppSjlYWDBzZXlKdVlXMWxJam9pUTJoeWIyMXBkVzBnVUVSR0lGWnBaWGRsY2lJc0ltUmxjMk55YVhCMGFXOXVJam9pVUc5eWRHRmliR1VnUkc5amRXMWxiblFnUm05eWJXRjBJaXdpYldsdFpWUjVjR1Z6SWpwYmV5SjBlWEJsSWpvaVlYQndiR2xqWVhScGIyNHZjR1JtSWl3aWMzVm1abWw0WlhNaU9pSndaR1lpZlN4N0luUjVjR1VpT2lKMFpYaDBMM0JrWmlJc0luTjFabVpwZUdWeklqb2ljR1JtSW4xZGZTeDdJbTVoYldVaU9pSk5hV055YjNOdlpuUWdSV1JuWlNCUVJFWWdWbWxsZDJWeUlpd2laR1Z6WTNKcGNIUnBiMjRpT2lKUWIzSjBZV0pzWlNCRWIyTjFiV1Z1ZENCR2IzSnRZWFFpTENKdGFXMWxWSGx3WlhNaU9sdDdJblI1Y0dVaU9pSmhjSEJzYVdOaGRHbHZiaTl3WkdZaUxDSnpkV1ptYVhobGN5STZJbkJrWmlKOUxIc2lkSGx3WlNJNkluUmxlSFF2Y0dSbUlpd2ljM1ZtWm1sNFpYTWlPaUp3WkdZaWZWMTlMSHNpYm1GdFpTSTZJbGRsWWt0cGRDQmlkV2xzZEMxcGJpQlFSRVlpTENKa1pYTmpjbWx3ZEdsdmJpSTZJbEJ2Y25SaFlteGxJRVJ2WTNWdFpXNTBJRVp2Y20xaGRDSXNJbTFwYldWVWVYQmxjeUk2VzNzaWRIbHdaU0k2SW1Gd2NHeHBZMkYwYVc5dUwzQmtaaUlzSW5OMVptWnBlR1Z6SWpvaWNHUm1JbjBzZXlKMGVYQmxJam9pZEdWNGRDOXdaR1lpTENKemRXWm1hWGhsY3lJNkluQmtaaUo5WFgxZCxXeUp5ZFNKZCwwLDEsMCwyNCwyMzc0MTU5MzAsOCwyMjcxMjY1MjAsMCwxLDAsLTQ5MTI3NTUyMyxSMjl2WjJ4bElFbHVZeTRnVG1WMGMyTmhjR1VnUjJWamEyOGdWMmx1TXpJZ05TNHdJQ2hYYVc1a2IzZHpJRTVVSURFd0xqQTdJRmRwYmpZME95QjROalFwSUVGd2NHeGxWMlZpUzJsMEx6VXpOeTR6TmlBb1MwaFVUVXdzSUd4cGEyVWdSMlZqYTI4cElFTm9jbTl0WlM4eE16QXVNQzR3TGpBZ1UyRm1ZWEpwTHpVek55NHpOaUF5TURBek1ERXdOeUJOYjNwcGJHeGgsZXlKamFISnZiV1VpT25zaVlYQndJanA3SW1selNXNXpkR0ZzYkdWa0lqcG1ZV3h6WlN3aVNXNXpkR0ZzYkZOMFlYUmxJanA3SWtSSlUwRkNURVZFSWpvaVpHbHpZV0pzWldRaUxDSkpUbE5VUVV4TVJVUWlPaUpwYm5OMFlXeHNaV1FpTENKT1QxUmZTVTVUVkVGTVRFVkVJam9pYm05MFgybHVjM1JoYkd4bFpDSjlMQ0pTZFc1dWFXNW5VM1JoZEdVaU9uc2lRMEZPVGs5VVgxSlZUaUk2SW1OaGJtNXZkRjl5ZFc0aUxDSlNSVUZFV1Y5VVQxOVNWVTRpT2lKeVpXRmtlVjkwYjE5eWRXNGlMQ0pTVlU1T1NVNUhJam9pY25WdWJtbHVaeUo5ZlgxOSw2NSwtMTI4NTU1MTMsMSwxLC0xLDE2OTk5NTQ4ODcsMTY5OTk1NDg4NywtMTQ2MTUxODEyLDEy',
        '__Secure-ETC': '88ba8c5784d1057fb01ca2ab611f76f9',
        'ADDRESSBOOKBAR_WEB_CLARIFICATION': '1729764847',
        '__Secure-user-id': '163293383',
        'is_adult_confirmed': '',
        'is_alco_adult_confirmed': '',
        'abt_data': '7.Wnzn6w3pTxg_Sd3oZcMnCVUtkq3L8tC51pboO6MFOLfcpM47pdGe_a1vvBvdy9XVfxSwF7HGSCSs7YRf7c3k5OSDu8ywxFLQEvdHsQsaa9S3Dml_3wYiFNttnfOxX08_jWEyyv8L74N6XlDvFBxawZCDVKvTs5aMLU5BPpykvOIB0sW6q2-89-hR6HZ_BywtsrXgYPtEw1g0bbtO5bNwjZNDD991PR0SBQqTKhXkPpAFRjNc-iTzttaoSbDywVV4xOkY3xP-CUmAjQ8lamQ4_W5RudFw0OoVTXOtVfrTt0jUYK6JoB71ZHqjMkZLnEechWfZFSIH6wh9uv6oD3EBMWgCMzADxlelJFGmvBXtIVHDn65vDxfVlFyCbgmThubDh_hoG0-BB69D-NnaFXDbK_wojRrHLKMq9nWDF6cCGTWXmM_YELuhMBiUKJaCgAfusZW0KsFK98Aj7FkOMbkfSBM-tv86yTgOkqQiAsi2XDRQyFxPlQJIneORqm8ozN7NBH9Jw5sMDbo64If-g-DyKmLHn4ynL3oGGs6mlqHfGAdOMHOUkpIVSA',
        'TS015d2969': '0187c00a1864d2c44e00ecdefb32518e265289f15f576c1a61152d6fec589a608931154248c023f591df6599751e42efd84fd93d6b',
        'bacntid': '4421855',
        'sc_company_id': '629749',
        '__Secure-access-token': '6.163293383.B4vPUPQiS-e4nDmpmfmPkA.68.AQK0P_Twu7l1GrmG-Tus14726uIgzTv9lBcykjA96r1OAzltgstqcTKzKwBAUjNc2CdTcOnvL7WK1mXz0UKOnOI.20240503112008.20241024125851.a935nUh7ZalpbKTiRPxoXAv9j_cQu52B9vz4LQtcxlY.1fdcf4bd5d7f994e8',
        '__Secure-refresh-token': '6.163293383.B4vPUPQiS-e4nDmpmfmPkA.68.AQK0P_Twu7l1GrmG-Tus14726uIgzTv9lBcykjA96r1OAzltgstqcTKzKwBAUjNc2CdTcOnvL7WK1mXz0UKOnOI.20240503112008.20241024125851.5GYUp-CG4yeKnMyH_T9CL29pdGbCRE0GJPUDzcoYLc4.1fd7e7171ba1fa1ff'
    }        
    
    chrome_binary_path = "/usr/bin/google-chrome"             # ДЛЯ УБУНТУ
    driver = uc.Chrome(executable_path=chrome_binary_path)    # ДЛЯ УБУНТУ
    
    driver.implicitly_wait(5)
    
    driver.get(url='https://seller.ozon.ru/app/reviews')
    for name, value in cookies.items():
        driver.add_cookie({'name': name, 'value': value})    
    driver.get(url='https://seller.ozon.ru/app/reviews')
    time.sleep(randint(5,10))   
    return driver

def sort_new (driver):
    elements = driver.find_elements(By.CSS_SELECTOR, '[class^="data-content-module_label_"]') # Меняем сортировку на новые    
    print(f"Найдено элементов: {len(elements)}")
    print(elements[13].text)
    time.sleep(randint(5,15))
    elements[13].click()  

def scroll_to_element(driver, element):    
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(1)  

async def find_review (driver):
    review_list_dict = []
    elements = driver.find_elements(By.CSS_SELECTOR, '[class^="index_review_"]') # Ищем первый отзыв с комментарием, если его нет, мотаем вниз  
    elements_rating = driver.find_elements(By.CSS_SELECTOR, '[class^="text-view-module_textView_"]')
    count = 1      
    for element in elements:
        scroll_to_element(driver, element)
        
        try:
            rating = elements_rating[1+3*count].text
        except:
            rating = '5'
        count += 1
        if 'Комментарий' in element.text or 'Достоинства' in element.text or 'Недостатки' in element.text:      
            if rating != '5':
                continue
            await asyncio.sleep(randint(1,5))                
            try:  
                element.click()
            except Exception:
                continue
            await asyncio.sleep(randint(1,5))           
            rev = review_dict (driver)

            if rev:
                review_list_dict.append(rev)
                print(element.text)
            print(f'Rating {rating} Отзывов без ответа: {len(review_list_dict)}')  
         
    return review_list_dict

def scroll (driver):
    try:
        scroll_elements = driver.find_elements(By.CSS_SELECTOR, '[class^="button-module_text_"]') # если отзывов много и не влезают на страницу, жмем кнопку - Показать еще 
       
        stop = False 
        for scroll_element in scroll_elements:
            if scroll_element.text == 'Показать еще':
              
                scroll_element.click()
                return True
          
        return False
    except Exception as err:
        return False

def review_dict (driver):
    elements = driver.find_elements(By.CSS_SELECTOR, '[class^="index_container_"]')
    time.sleep(1)   
    review = {}
    review['text'] = ''

    for element in elements:        
        if ('Опубликован') in element.text:
            actions = ActionChains(driver)            
            actions.send_keys(Keys.ESCAPE).perform()
            return False
        if 'Обработанный' in element.text:
            continue
        if len(element.text.split('\n')) > 10:        
            continue
        if 'Товар' in element.text:
            data = element.text.split('\n')
            if len(data) > 1 and data[1] != '':
                review['product'] = data[1]
        if 'Покупатель' in element.text:
            data = element.text.split('\n')
            if len(data) > 1 and data[1] != 'Пользователь предпочёл скрыть свои данные':
                review['username'] = data[1]
            else:
                review['username'] = ''
            if review['username'] == 'Сергей Ю.' or review['username'] == 'Наталья':
                pass
        if 'Достоинства' in element.text:
            data = element.text.split('\n')
            if len(data) > 1 and data[1] != '':
                review['text'] += data[0] + ': ' + data[1] + '. '
        if 'Недостатки' in element.text:
            data = element.text.split('\n')
            if len(data) > 1 and data[1] != '':
                review['text'] += data[0] + ': ' + data[1] + '. '
        if 'Комментарий' in element.text:
            data = element.text.split('\n')
            if len(data) > 1 and data[1] != '':
                review['text'] += data[0] + ': ' + data[1] + '. '   
            print(element.text.replace('\n',' '))    
    
    answer_dict_ozon = open_file()
    for k in answer_dict_ozon:
        if len(review['text'])>10 and review['text'] in k and answer_dict_ozon[k]['post'] == "True":
            answer_text = answer_dict_ozon[k]['answer']            
            inputs = driver.find_elements(By.CSS_SELECTOR, '[class^="index_textarea_"]')          
            inputs[0].send_keys(answer_text)
            send = driver.find_elements(By.CSS_SELECTOR, '[class^="custom-button_text_"]') 
            print('Запостили ответ!!!')
            send[0].click()
            answer_dict_ozon[k]['post'] = "Posted"
            save_file(answer_dict_ozon)            

    print(review)    
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()
    return review

async def review():
    while True:
        print('START',datetime.now())
        display = Display(visible=0, size=(800, 600))   # ДЛЯ УБУНТУ
        display.start()                                 # ДЛЯ УБУНТУ
        driver = get_driver()        
        await asyncio.sleep(randint(5,15))       
        for k in range(8):
            scrl = scroll(driver) 
            await asyncio.sleep(randint(1,4))
        review_list_dict = await find_review (driver)
        print(len(review_list_dict),review_list_dict)
        await asyncio.sleep(randint(5,10))
        answer_dict_ozon = open_file()        
        for k in review_list_dict:
            try:
                username = k['username']
                if username =='':
                    pass
                elif ' ' in username:
                    username = username.split(' ')[0]
                    username = f'Имя: {username}'
                else:
                    username = f'Имя: {username}'
                product = k['product']
                text = k['text']
                key = f'{username} {product} {text}'
                if key not in answer_dict_ozon:
                    answer_dict_ozon[key] = {}
                    answer_dict_ozon[key]['post'] = 'False'
                    answer = await yandex_gpt_async.answer_generate(key)
                    #answer = yandex_gpt.answer_generate(key)
                    answer_dict_ozon[key]['answer'] = answer
                    await bot_ozon.send_message_with_buttons('181205987',f'OZON\n\nПродукт: {product}\nОтзыв: {text}\n\nОтвет: {answer}')
                    await asyncio.sleep(0.1)
                    await bot_ozon.send_message_with_buttons('678429834',f'OZON\n\nПродукт: {product}\nОтзыв: {text}\n\nОтвет: {answer}')
                    await asyncio.sleep(0.1)
                    await bot_ozon.send_message_with_buttons('5235480144',f'OZON\n\nПродукт: {product}\nОтзыв: {text}\n\nОтвет: {answer}')
                    await asyncio.sleep(0.1)
                    save_file(answer_dict_ozon)
            
            except Exception as errrr:
                print(errrr)
                continue
        save_file(answer_dict_ozon)
        try:
            driver.quit()
            display.stop()           # ДЛЯ УБУНТУ
        except OSError as e:
            print(f"Ошибка при закрытии браузера: {e}")  
        print('FINISH', datetime.now())      
        await asyncio.sleep(randint(2000,4000))

async def main():
    try:        
        task1 = asyncio.create_task(review())
        task2 = asyncio.create_task(bot_ozon.main())
        await asyncio.gather(task1, task2)
    except Exception as err:
        exception_traceback = traceback.format_exc()
        logger.error(exception_traceback)   

if __name__ == '__main__':
    asyncio.run(main())





import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import threading
from pyvirtualdisplay import Display
from loguru import logger
import sys, traceback
import json
import platform
#logger.add("debug.log", format="{time} - {level} - {function} - {message}", level="DEBUG", backtrace=False, rotation="20 MB")
#logger.add("debug_error.log", format="{time} - {level} - {function} - {message}", level="ERROR", backtrace=False, rotation="20 MB")
# Настройка логгера

load_dotenv()

# # # # sudo apt update
# # # # sudo apt install -y wget
# # # # wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# # # # sudo dpkg -i google-chrome-stable_current_amd64.deb
# # # # sudo apt-get install -f

# # # # sudo apt update
# # # # sudo apt install xvfb

# # # # pip install pyvirtualdisplay undetected-chromedriver

# Проверяем операционную систему
current_os = platform.system()
logger.debug(f'Система {current_os}')


def extract_plate_number(line):
    match = re.search(r"\b[А-ЯA-Z]{1}\d{1,4}[А-ЯA-Z]{1,2}/\d{1,3}\b", line)
    return match.group(0) if match else None

def extract_and_format_plate_number(line):
    match = re.search(r"\b([А-ЯA-Z]{1})\s*(\d{1,4})\s*([А-ЯA-Z]{1,2})\s*(\d{1,3})\b", line)
    if match:
        # Форматируем номер в нужный формат
        return f"{match.group(1)}{match.group(2)}{match.group(3)}/{match.group(4)}"
    return None

def get_driver(url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-gpu')

    if current_os == "Linux":  # Для Ubuntu
        logger.debug(f'запускаю дисплей')
        display = Display(visible=0, size=(1920, 1080))
        display.start()

        logger.debug(f'запускаю драйвер')
        chrome_binary_path = "/usr/bin/google-chrome"
        driver = uc.Chrome(options=options, executable_path=chrome_binary_path)
    elif current_os == "Windows":  # Для Windows
        driver = uc.Chrome(options=options)

    logger.debug(f'driver.get(url)')
    driver.get(url)
    logger.debug(f'Открываю сайт {url}')
    time.sleep(1)
    driver.implicitly_wait(45)
    actions = ActionChains(driver)
    actions.send_keys(Keys.ESCAPE).perform()

    if current_os == "Linux":  # Для Ubuntu
        return driver, display
    elif current_os == "Windows":  # Для Windows
        return driver


async def parse(name=None, id=None):
    if name:
        name = f"*{name.replace(' ','')}*"
        input_text = name
    login = os.getenv('WLN_LOGIN')
    password = os.getenv('WLN_PASSWORD')
    url = os.getenv('WLN_URL')
    blocked = None
    last_time = None

    if current_os == "Linux":  # Для Ubuntu    
        driver, display = await asyncio.to_thread(get_driver, url)          
    elif current_os == "Windows":  # Для Windows
        driver = await asyncio.to_thread(get_driver, url)

    try:
        # Ждем, пока форма с атрибутом data-add-classes="css.LoginForm" станет доступной
        login_form = await asyncio.to_thread(
            WebDriverWait(driver, 30).until,
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-add-classes="css.LoginForm"]'))
        )
        logger.debug("Форма входа найдена")

        # Находим поля для ввода логина и пароля
        username_field = driver.find_element(By.CSS_SELECTOR, '[name="avl_username"]')
        password_field = driver.find_element(By.CSS_SELECTOR, '[name="avl_password"]')

        # Вводим логин и пароль
        username_field.send_keys(login)
        password_field.send_keys(password)
        logger.debug("Логин и пароль введены")

        # Нажмем ентер
        password_field.send_keys(Keys.RETURN)
        logger.debug("Вход выполнен успешно")

        # Ждем, пока исчезнет оверлей (если он есть)
        await asyncio.to_thread(
            WebDriverWait(driver, 15).until,
            EC.invisibility_of_element_located((By.CLASS_NAME, "Overlay_oJm6"))
        )
        logger.debug("Оверлей исчез")

        # Ждем, пока блок с id="menu_avl_unit" станет доступным
        menu_block = await asyncio.to_thread(
            WebDriverWait(driver, 15).until,
            EC.element_to_be_clickable((By.ID, "menu_avl_unit"))
        )
        logger.debug("Блок menu_avl_unit найден")

        # Кликаем по блоку, чтобы раскрыть его
        menu_block.click()
        logger.debug("Блок menu_avl_unit раскрыт")

        

           
        if id:
            input_text = id
            try:
                # Ждем, пока выпадающий список с классом "wui-select" станет доступным
                dropdown = await asyncio.to_thread(
                    WebDriverWait(driver, 15).until,
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[id="items_search_filter_avl_unit"]'))
                )
                logger.debug("Выпадающий список найден")

                # Кликаем по выпадающему списку, чтобы открыть его
                dropdown.click()
                logger.debug("Выпадающий список открыт")

                # Ждем, пока опции внутри выпадающего списка станут доступными
                options = await asyncio.to_thread(
                    WebDriverWait(driver, 15).until,
                    lambda d: dropdown.find_elements(By.TAG_NAME, "option")
                )

                # Перебираем опции и выбираем нужные
                for option in options:
                    value = option.get_attribute("value")
                    value_text = option.text.strip()
                    if value in ["sys_unique_id", "sys_unique_id2"]:
                        option.click()
                        logger.debug(f"Выбрана опция с value={value}")
                    if value_text == "Уникальный ID":
                        option.click()
                        logger.debug(f"Выбрана опция с value={value}")
                        break

                #options[3].click()
                #logger.debug(f"Выбрана опция с value={value}")

            except TimeoutException:
                logger.debug("Выпадающий список или опции не найдены")
                print("Выпадающий список или опции не найдены")
            except Exception as e:
                exception_traceback = traceback.format_exc()
                print(exception_traceback)
                logger.error(f'Ошибка при выборе опции: {e}')


        # Ждем, пока поле ввода с id="items_search_text_avl_unit" станет доступным
        search_field = await asyncio.to_thread(
            WebDriverWait(driver, 15).until,
            EC.element_to_be_clickable((By.ID, "items_search_text_avl_unit"))
        )
        logger.debug("Поле ввода items_search_text_avl_unit найдено")
        
        search_field.click()
        # Очищаем поле ввода перед вводом текста
        await asyncio.sleep(1)
        search_field.clear()

        # Вводим текст "sear" в поле и нажимаем Enter
        await asyncio.sleep(1)
        search_field.send_keys(input_text)
        search_field.send_keys(Keys.RETURN)
        logger.debug(f"Текст {input_text} введен и нажата клавиша Enter")

        # Ждем, пока элемент с id="7" станет доступным (если он есть)
        try:
            element7 = await asyncio.to_thread(
                WebDriverWait(driver, 15).until,
                EC.presence_of_element_located((By.ID, "7"))
            )
            logger.debug("Элемент с id=7 найден")
            print(f"Текст элемента с id=7: {element7.text}")
            if element7.text == "":
                blocked = 'Активен'
            else:
                blocked = f'Деактивирован: {element7.text}'

            element10 = driver.find_element(By.ID, "10")
            print(f"Текст элемента с id=10: {element10.text}")
            last_time = element10.text
        except TimeoutException:
            logger.debug("Элемент с id=7 не найден")
            print("Элемент с id=7 не найден")

    except Exception as e:
        exception_traceback = traceback.format_exc()
        print(exception_traceback)
        logger.error(f'Ошибка при выполнении входа: {e}')
    finally:
        try:
            # Закрываем драйвер в любом случае
            await asyncio.to_thread(driver.quit)
            if current_os == "Linux":  # Для Ubuntu    
                await asyncio.to_thread(display.stop)  # ДЛЯ УБУНТУ
        except Exception:
            pass

    return blocked, last_time

# Запуск асинхронной функции
name = 'М693НК/159'
id = '866854052616086'
#asyncio.run(parse(id=id))