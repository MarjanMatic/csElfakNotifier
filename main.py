from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import tomllib
import json
import time
import os

def main():
    config = initConfig()
    driver = initDriver()

    handle_privacy_error(driver)
    login(driver)

    if os.path.isfile("./last_check.json") == False:
        create_last_check_file(driver, config["course_ids"])
    else:
        with open("last_check.json", "r") as f:
            last_check = json.load(f)
        last_check = notify_new_courses_posts(driver, last_check)
        with open("last_check.json", "w") as f:
            json.dump(last_check, f)

    time.sleep(1)
    driver.quit()

def handle_privacy_error(driver):
    if driver.title == "Privacy error":
        driver.find_element(By.ID, "details-button").click()
        proceed_link = driver.find_element(By.ID, "final-paragraph").find_element(By.TAG_NAME, "a")
        proceed_link.click()


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

def create_last_check_file(driver, course_ids):
    checkJson = find_last_courses_posts(driver, course_ids)
    with open("last_check.json", "w") as f:
        json.dump(checkJson, f)

def has_search_results(driver) -> bool:
    page_content = driver.find_element(By.ID, "page-content")
    result = page_content.find_element(By.TAG_NAME, "h3").text
    return result.find(":") != -1

def find_last_courses_posts(driver, course_ids):
    checkJson = {
        "timestamp": int(time.time()),
        "courses": {}
    }

    for id in course_ids:
        driver.get(f"https://cs.elfak.ni.ac.rs/nastava/mod/forum/search.php?id={id}&datefrom=1577833200")

        checkJson["courses"][id] = None
        if has_search_results(driver):
            article = driver.find_element(By.TAG_NAME, "article")
            permalink = article.find_element(By.PARTIAL_LINK_TEXT, "Permalink")
            checkJson["courses"][id] = permalink.get_attribute("href")
        
        time.sleep(1)

    return checkJson

def notify_new_courses_posts(driver, last_check):
    new_timestamp = int(time.time())
    for id in last_check["courses"]:
        driver.get(f"https://cs.elfak.ni.ac.rs/nastava/mod/forum/search.php?id={id}&datefrom={last_check["timestamp"]}")

        if has_search_results(driver):
            articles = driver.find_elements(By.TAG_NAME, "article")
            new_href = notify_new_posts(articles, last_check["courses"][id])
            last_check["courses"][id] = new_href
        
        time.sleep(1)

    last_check["timestamp"] = new_timestamp
    print(last_check)
    return last_check

def notify_new_posts(articles, last_href):
    article_stack = find_which_posts_are_new(articles, last_href)
    new_href = last_href
    while len(article_stack) > 0:
        (article, new_href) = article_stack.pop()
        print(article.text)
    
    return new_href


def find_which_posts_are_new(articles, last_href):
    article_stack = []
    for article in articles:
        permalink = article.find_element(By.PARTIAL_LINK_TEXT, "Permalink")
        href = permalink.get_attribute("href")
        if href == last_href:
            break

        article_stack.append((article, href))
    
    return article_stack

load_dotenv()
main()