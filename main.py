from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv
import tomllib
import json
import time
import os

LAST_CHECK_FILENAME = "last_check.json"

def main():
    config = initConfig()
    driver = initDriver()

    login(driver)

    last_check, created = get_last_check_json(driver, config["course_ids"])
    if not created:
        new_check = notify_new_courses_posts(driver, last_check)
        with open(LAST_CHECK_FILENAME, "w") as f:
            json.dump(new_check, f)

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
    handle_privacy_error(driver)
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

def get_last_check_json(driver, course_ids) -> tuple[bool, dict]:
    if os.path.isfile(LAST_CHECK_FILENAME) == False:
        last_check = create_last_check_file(driver, course_ids)
        return last_check, True
    else:
        with open(LAST_CHECK_FILENAME, "r") as f:
            last_check = json.load(f)
        return last_check, False

def new_check_create():
    return {
        "timestamp": int(time.time()),
        "courses": {}
    }

def create_last_check_file(driver, course_ids):
    check_json = new_check_create()
    for id in course_ids:
        check_json["courses"][id] = None
    
    with open(LAST_CHECK_FILENAME, "w") as f:
        json.dump(check_json, f)
    return check_json

def has_search_results(driver) -> bool:
    page_content = driver.find_element(By.ID, "page-content")
    result = page_content.find_element(By.TAG_NAME, "h3").text
    return result.find(":") != -1

def search_course_forum(driver, id, timestamp):
    driver.get(f"https://cs.elfak.ni.ac.rs/nastava/mod/forum/search.php?id={id}&datefrom={timestamp}")

def notify_new_courses_posts(driver, last_check):
    new_check = new_check_create()
    for id in last_check["courses"]:
        search_course_forum(driver, id, last_check["timestamp"])
        if has_search_results(driver):
            articles = driver.find_elements(By.TAG_NAME, "article")
            new_href = notify_new_posts(articles, last_check["courses"][id])
            new_check["courses"][id] = new_href
        else:
            new_check["courses"][id] = None
        
        time.sleep(1)

    return new_check

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