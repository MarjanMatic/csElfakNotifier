from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import tomllib
import time
import os

def main():
    config = initConfig()
    driver = initDriver()
    login(driver)
    find_last_courses_posts(driver, config["course_ids"])
    time.sleep(1)
    driver.quit()

def initConfig():
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    return config

def initDriver():
    driver = webdriver.Chrome()
    driver.get("https://cs.elfak.ni.ac.rs/nastava/")
    driver.implicitly_wait(10)
    return driver

def login(driver):
    login_link = driver.find_element(By.LINK_TEXT, "Log in")
    login_link.click()

    open_id_button = driver.find_element(By.PARTIAL_LINK_TEXT, "OpenID")
    open_id_button.click()

    microsoft_login(driver)
    # wait for a random element so that we know we're back on the site
    random_element = driver.find_element(By.CLASS_NAME, "aalink")

def microsoft_login(driver):
    enter_login_info(driver, "loginfmt", os.getenv("EMAIL"))
    enter_login_info(driver, "passwd", os.getenv("PASSWORD"))

    dont_stay_signed_in = driver.find_element(By.ID, "idBtn_Back")
    dont_stay_signed_in.click()

def enter_login_info(driver, element_name, credential):
    login_element = driver.find_element(By.NAME, element_name)
    login_element.send_keys(credential)
    login_element.send_keys(Keys.RETURN)
    time.sleep(1.5)

def find_last_courses_posts(driver, course_ids):
    for id in course_ids:
        driver.get(f"https://cs.elfak.ni.ac.rs/nastava/mod/forum/search.php?id={id}&datefrom=1577833200")
        page_content = driver.find_element(By.ID, "page-content")
        results = page_content.find_element(By.TAG_NAME, "h3")
        if results.text.find(":") == -1:
            print("No results")
            continue

        article = driver.find_element(By.TAG_NAME, "article")
        print(article.text)
        time.sleep(1)

load_dotenv()
main()