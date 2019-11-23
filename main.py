from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.expected_conditions import presence_of_element_located, presence_of_all_elements_located
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from requests.exceptions import ConnectionError
from re import sub
from requests import get
from pytesseract import image_to_string, pytesseract
from PIL import Image
from collections import deque
from os.path import exists
from os import makedirs

from time import sleep



working_directory = "C:/Users/David/Downloads/axfc downloads/" # all downloads and files are here
pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"  #unused
download_jobs = deque() # contains 2-tuples of url to archive file and name of that file
job_num = 3321  #folders in working_directory are created according to this number. each folder will hold 1 file

def solve_captcha():
    """broken implementation. supposed to identify captcha text and enter it into the textbox"""
    try:
        captcha_textbox = driver.find_element_by_name("cpt")
        captcha_image_url = driver.find_element_by_xpath("//div[@class='imgbox_f']/img").get_attribute("src")
        r = get(captcha_image_url, verify=False)  #consider working around certificate errors
        with open(working_directory + "captcha.png", "wb") as image:
            image.write(r.content)

    except NoSuchElementException:
        return


def page_has_captcha():
    try:
        driver.find_element_by_xpath("//div[@class='imgbox_f']/img")
    except NoSuchElementException:
        return False
    return True


def page_has_password():
    try:
        driver.find_element_by_xpath("//input[@name='keyword']")
    except NoSuchElementException:
        return False
    return True


def navigate_axfc_and_add_download_to_queue(url):
    """if page has a password or captcha, logs the url and does nothing, otherwise:
    adds a tuple, where the first element is the download link, and the second is the filename, to the download queue"""
    driver.get(url)
    if page_has_password():
        log(url, "downloads with passwords.txt")
        return
    elif page_has_captcha():
        log(url, "downloads with captchas.txt")
        return
    try:
        filename = wait.until(presence_of_all_elements_located((By.XPATH, "//div[@class='comme']/p")))[-1].text
    except TimeoutException:
        filename = "could not identify name.zip"
    download_generation_button = wait.until(presence_of_element_located((By.XPATH, "//input[@class='button'][@type='submit']")))
    download_generation_button.click()
    generate_link = wait.until(presence_of_element_located((By.PARTIAL_LINK_TEXT, "＜ダウンロードする | click here to start download. ＞")))
    generate_link.click()
    download_link = wait.until(presence_of_element_located((By.PARTIAL_LINK_TEXT,"こちら")))
    download_jobs.append((download_link.get_attribute("href"), filename))


def change_download_server(link, server_name):
    """replaces the server in an axfc link (link) with another server (servername)"""
    return sub("^http://[a-z]*", "http://" + server_name, link)


def log(url, file):
    """writes string to file"""
    with open(working_directory + file, "a", encoding="UTF-8") as file:
        file.write(url + "\n")


server_list = ["moonstone", "taurus", "cancer"]


def download(url, tries=5):
    """given an axfc url like https://www.axfc.net/u/3511859, attempts to download the corresponding file to a job_number folder in the working directory, while logging appropriately"""
    if tries == 0:
        log(url, "404 downloads.txt")
        return
    try:
        navigate_axfc_and_add_download_to_queue(url)
    except TimeoutException:
        return
    if not download_jobs:
        return
    link, filename = download_jobs.pop()
    link = change_download_server(link, server_list[tries % len(server_list)])
    try:
        r = get(link, stream=True)
    except ConnectionError:
        download(url, tries - 1)
        return

    if r.status_code == 200:
        print(link)
        path = working_directory + str(job_num) + "/"
        if not exists(path):
            makedirs(path)
        try:
            fd = open(path + filename, 'wb')
        except OSError:
            fd = open(path + "could not identify name.zip", 'wb')

        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
        fd.close()
        log(url, "completed downloads.txt")
        return
    download(url, tries - 1)





def gen_download_links_from_file(file_name):
    """get urls from text file"""
    with open (working_directory + file_name, "r", encoding="UTF-8") as file:
        for line in file.readlines():
            yield line.strip()
#solve_captcha()
# captcha link https://www.axfc.net/u/3511859
# broken link http://www.axfc.net/u/2724850vvvvvv
# password link http://www.axfc.net/u/118138


driver = webdriver.Firefox(executable_path=r"C:\Programs\gecko driver\geckodriver.exe")
wait = WebDriverWait(driver, 60)
for link in gen_download_links_from_file("link list.txt"):
    download(link)
    job_num += 1

