# get_html.py

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from secrets import EMAIL, USERNAME, PASSWORD

def save_tweets_for_profile(driver, profile_url, profile_name):
    # Go to profile page
    print(f"Navigating to profile: {profile_url}")
    driver.get(profile_url)

    # Wait for tweets to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//div[@data-testid="primaryColumn"]'))
    )

    last_height = driver.execute_script("return document.body.scrollHeight")

    # scroll to load tweets
    for _ in range(5):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
    print(f"Found {len(tweets)} tweets on {profile_name}")

    # Folder per account
    folder = os.path.join("tweets_html", profile_name)
    os.makedirs(folder, exist_ok=True)

    for idx, tweet in enumerate(tweets):
        try:
            html = tweet.get_attribute("outerHTML")
            filepath = os.path.join(folder, f"tweet_{idx}.html")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
        except Exception as e:
            print(f"Error saving tweet {idx}: {e}")
            continue

    print(f"Saved HTML for {len(tweets)} tweets in: {folder}")


def save_tweet_htmls():
    # Read list of accounts from accounts.txt
    with open("accounts.txt", encoding="utf-8") as f:
        accounts = [line.strip() for line in f if line.strip()]
        print(accounts)

    driver = webdriver.Chrome()
    driver.get("https://twitter.com/login")

    try:
        print("Logging in...")

        # email step
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        email_input.send_keys(EMAIL)
        email_input.send_keys(Keys.RETURN)

        # sometimes Twitter asks for username again
        try:
            username_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_input.send_keys(USERNAME)
            username_input.send_keys(Keys.RETURN)
        except:
            print("Username step skipped.")

        # password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(PASSWORD)
        password_input.send_keys(Keys.RETURN)
        print("Login successful!")

        # Loop through accounts
        for account in accounts:
            print("Starting to scrape account:", account)
            profile_url = f"https://twitter.com/{account}"
            save_tweets_for_profile(driver, profile_url, account)

    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    save_tweet_htmls()
