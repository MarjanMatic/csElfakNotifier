from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import time
import os

def main():
    driver = initialize()
    login(driver)
    time.sleep(5)
    driver.quit()

def initialize():
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
    time.sleep(1)


load_dotenv()
main()