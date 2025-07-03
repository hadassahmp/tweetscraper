# main.py
import time
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def twitter_scraper():
    """
    A Selenium-based scraper to log into Twitter, navigate to a politician's profile,
    scroll down to load tweets, and extract tweet information.

    The script prompts the user for their Twitter credentials and the target profile URL.
    Tweet data (author, timestamp, text, and image URLs) is saved to a CSV file.
    """
    # --- 1. User Input ---
    # Prompt the user for their Twitter login credentials and target profile
    email = input("Enter your Twitter email: ")
    username = input("Enter your Twitter username: ")
    password = input("Enter your Twitter password: ")
    profile_url = input("Enter the full URL of the Twitter profile you want to scrape: ")

    # --- 2. Initialize Selenium WebDriver ---
    # Using Chrome as the browser. You will need to have chromedriver installed.
    # You can download it from: https://chromedriver.chromium.org/downloads
    driver = webdriver.Chrome()
    driver.get("https://twitter.com/login")

    try:
        # --- 3. Login to Twitter ---
        print("Logging in...")
        
        # Wait for the email input field to be present and enter the email
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "text"))
        )
        email_input.send_keys(email)
        email_input.send_keys(Keys.RETURN)
        
        # Handle the "Enter your phone number or username" page if it appears
        try:
            username_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.NAME, "text"))
            )
            username_input.send_keys(username)
            username_input.send_keys(Keys.RETURN)
        except:
            # If this fails, it's likely because Twitter went straight to password
            print("Username entry step skipped.")
            pass

        # Wait for the password input field and enter the password
        password_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "password"))
        )
        password_input.send_keys(password)
        password_input.send_keys(Keys.RETURN)
        print("Login successful!")

        # --- 4. Navigate to the Target Profile ---
        print(f"Navigating to profile: {profile_url}")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//a[@data-testid="AppTabBar_Home_Link"]'))
        )
        driver.get(profile_url)
        
        # --- 5. Scroll and Scrape Tweets ---
        print("Scrolling and scraping tweets...")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@data-testid="primaryColumn"]'))
        )

        tweets_data = []
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        # Scroll a few times to load a good number of tweets
        for _ in range(5): # Adjust the range to scroll more or less
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # Wait for tweets to load
            
            # Break if we're not loading new tweets
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Find all tweet articles on the page
        tweets = driver.find_elements(By.XPATH, '//article[@data-testid="tweet"]')
        print(f"Found {len(tweets)} tweets.")

        # --- 6. Extract Information from Each Tweet ---
        for tweet in tweets:
            try:
                # Extract author name
                author = tweet.find_element(By.XPATH, './/div[@data-testid="User-Names"]//span').text

                # Extract timestamp
                timestamp = tweet.find_element(By.XPATH, './/time').get_attribute('datetime')

                # Extract tweet text
                tweet_text_element = tweet.find_element(By.XPATH, './/div[@data-testid="tweetText"]')
                tweet_text = tweet_text_element.text
                
                # Extract image URLs if any
                images = []
                image_elements = tweet.find_elements(By.XPATH, './/div[@data-testid="tweetPhoto"]//img')
                for img in image_elements:
                    images.append(img.get_attribute('src'))

                tweets_data.append({
                    "author": author,
                    "timestamp": timestamp,
                    "text": tweet_text,
                    "images": ", ".join(images) # Join multiple image URLs
                })

            except Exception as e:
                print(f"Error scraping a tweet: {e}")
                continue # Move to the next tweet

    finally:
        # --- 7. Save to CSV and Quit ---
        if tweets_data:
            # Define CSV file name based on the profile
            profile_name = profile_url.split("/")[-1]
            filename = f'{profile_name}_tweets.csv'

            print(f"Saving tweets to {filename}")
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=["author", "timestamp", "text", "images"])
                writer.writeheader()
                writer.writerows(tweets_data)
            print("Scraping complete!")

        # Close the browser
        driver.quit()

if __name__ == "__main__":
    twitter_scraper()