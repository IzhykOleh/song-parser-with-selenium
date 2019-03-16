from bs4 import BeautifulSoup
from urllib import request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import time
import os 
import re
import string

what_to_parse = ['В', 'Г', 'Ґ', 'Д', 'Е', 'Є', 'Ж', 'З', 'И', 'І', 'Ї']#, 'Й', 'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф', 'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ь', 'Ю', 'Я']
URL = ['http://www.minus.lviv.ua/minus/artist_alphabet/{}/'.format(ch) for ch in what_to_parse]
main_URL = 'http://www.minus.lviv.ua/minus/'
PATH_to_chromedriver = 'E:/music from lv minus/chromedriver_win32/chromedriver.exe'
username = 'need sign in to site'
password = 'password'

options = webdriver.ChromeOptions() 
options.add_experimental_option("prefs", {
  "download.default_directory": r"E:\music from lv minus\music"})
options.add_argument("download.prompt_for_download=False")

def wait_on_click(driver, x_path):
    try:
        e = driver.find_elements_by_xpath(x_path)
    except NoSuchElementException:
        print('button was not found, (wait_on_click method)')
        
    try:
        el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, x_path)))
        return el
    except TimeoutException:
        return False

def wait_on_div(driver, x_path):
    try:
        els = WebDriverWait(driver, 10).until(EC.visibility_of_all_elements_located((By.XPATH, x_path)))
        return els
    except TimeoutException:
        return False

def login_(driver, username, password):
    u = driver.find_element_by_xpath('//*[@id="id_username"]')
    p = driver.find_element_by_xpath('//*[@id="id_password"]')

    u.send_keys(username)
    p.send_keys(password)

    driver.find_element_by_xpath('//*[@id="submit_login"]').click()

def every_downloads_chrome(driver):
    if not driver.current_url.startswith("chrome://downloads"): 
        driver.get("chrome://downloads/")      
    result = driver.execute_script("""
        var item = downloads.Manager.get().items_[0];
        if (item.state === "COMPLETE")
            return item.file_url;
        """)
    return result
        

def song_rename(song_name):
    music_dir = os.path.join(os.getcwd(), 'music')
    mas = [os.path.join(music_dir, f) for f in os.listdir(music_dir)]
    filename = max(mas, key=os.path.getctime)
    extens = re.search(r'\.(.*)' , filename)
    if extens == None:
        song_new_name = os.path.join(music_dir, song_name)
    else:
        song_new_name = os.path.join(music_dir, song_name+'.'+extens.group(1))
    try:
        os.rename(filename, song_new_name)
    except FileExistsError:
        print("File exists")
    except FileNotFoundError:
        print('File not found: ', song_name)
    except PermissionError:
        print('Permission error: ', song_name)

def dawnload_song(driver, btn):
    btn.click()
    time.sleep(2)
    try:
        WebDriverWait(driver, 120, 1).until(every_downloads_chrome)
    except TimeoutException:
        return False
        

def get_song_name(driver):
    h_xpath = '//*[@id="content"]/div/div[1]/h5[@class="min_rec"]'
    try:
        h_el = driver.find_element_by_xpath(h_xpath)
    except NoSuchElementException:
        print('song_name not found (get_song_name_method)')
        return False
    song_name = h_el.get_attribute('innerHTML')
    song_name = " ".join([re.sub(r'\W', '', i) for i in song_name.split()])
    return song_name

def run(driver, link):
    main_window = driver.current_window_handle
    ActionChains(driver).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
    try:
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    except TimeoutException:
        print('try click again')
        try:
            ActionChains(driver).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        except TimeoutException:
            print('cannot click')
            return None
    driver.switch_to.window(driver.window_handles[1])
    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="content"]/div/div[1]/h5[@class="min_rec"]')))
    except TimeoutException:
        print('not found song name (run method)')
    song_name = get_song_name(driver)
    if song_name == False:
        song_name = "incorrect name"
    btn = wait_on_click(driver, '//*[@id="download"]')
    status = dawnload_song(driver, btn)
    if status == False:
        print('This is song is not downloaded: ', song_name)
    song_rename(song_name)                        
    driver.close()
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(1))
    driver.switch_to.window(main_window)

def main(start=1):
    driver = webdriver.Chrome(executable_path=PATH_to_chromedriver, chrome_options=options)
    driver.get(main_URL)

    login_(driver, username, password)
    time.sleep(2)

    flag = True
    
    for url_ in URL:
        driver.get(url_)
        
        try:
            ul = driver.find_element_by_xpath('//*[@id="minus_catalogue"]/ul')
            if ul:
                length = len(driver.find_elements_by_xpath('//*[@id="minus_catalogue"]/ul[@class="authors"]/li/a'))
                total_count = 0
                try:
                    if flag == True:
                        start_ = start
                    else:
                        start_ = 1
                    for counter in range(start_, length+1):
                        x_path = '//*[@id="minus_catalogue"]/ul/li[{}]/a'.format(counter)
                        el_ = wait_on_click(driver, x_path)
                        if el_== False:
                            el_ = wait_on_click(driver, x_path)
                            print('try click again')
                        if el_:
                            el_.click()
                            
                            
                        
                        
                        xpath = "//*[@id='minus_catalogue']/ul/li[{}]/div[@class = 'info rec open']/ul/li/a[@class='dynamic']".format(counter)
                        v = wait_on_div(driver, xpath)
                        if v == False:
                            v = wait_on_div(driver, xpath)
                            print('try get visible again')
                        if v:
                            total_count+=1
                            print("Good job \n")
                            a_s = driver.find_elements_by_xpath(xpath)
                            for link in a_s:
                                run(driver, link)
                    
                except NoSuchElementException:
                    print('End of links')
                print('Total count: ', total_count)
                print('All elements:', length)

            ul2 = driver.find_element_by_xpath('//*[@id="folk"]/ul')
            if ul2:
                length = len(driver.find_elements_by_xpath('//*[@id="folk"]/ul/li'))
                try:

                    for counter in range(1, length+1):
                        xpath = "//*[@id='folk']/ul/li[{}]/a".format(counter)
                        link = wait_on_click(driver, xpath)
                        run(driver, link)                            
                    
                except NoSuchElementException:
                    print('End of links')
                print('All elements:', length)
            
        except NoSuchElementException:
            print("Didn't find anything by xpath")

        flag=False
    
if __name__ == "__main__":
    main(31)
