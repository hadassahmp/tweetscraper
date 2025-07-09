# scrape_tweets.py

import os
from bs4 import BeautifulSoup
import csv

class TweetScraper:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, "html.parser")

    def extract(self):
        data = {}
        
        # Display name
        display_name_tag = self.soup.find("div", attrs={"data-testid": "User-Name"})
        display_name = None
        if display_name_tag:
            span = display_name_tag.find("span")
            if span:
                display_name = span.get_text(strip=True)
        data["display_name"] = display_name

        # Username
        handle_tag = self.soup.find("a", href=True, role="link")
        username = None
        if handle_tag:
            handle_span = handle_tag.find("span")
            if handle_span:
                username = handle_span.get_text(strip=True)
            else:
                username = handle_tag.get_text(strip=True)
        data["username"] = username

        # Verified
        verified = False
        verified_icon = self.soup.find("svg", attrs={"data-testid": "icon-verified"})
        if verified_icon:
            verified = True
        data["verified"] = verified

        # Profile picture
        profile_img_tag = self.soup.find("img", class_="css-9pa8cd")
        profile_image_url = None
        if profile_img_tag:
            profile_image_url = profile_img_tag.get("src")
        data["profile_image_url"] = profile_image_url

        # Tweet text
        tweet_text_tag = self.soup.find("div", attrs={"data-testid": "tweetText"})
        tweet_text = None
        if tweet_text_tag:
            tweet_text = tweet_text_tag.get_text(separator=" ", strip=True)
        data["text"] = tweet_text

        # Timestamp
        time_tag = self.soup.find("time")
        timestamp = None
        if time_tag:
            timestamp = time_tag.get("datetime")
        data["datetime"] = timestamp

        # Tweet URL
        tweet_link_tag = self.soup.find("a", href=True, attrs={"href": lambda href: href and "/status/" in href})
        tweet_url = None
        if tweet_link_tag:
            tweet_url = "https://twitter.com" + tweet_link_tag["href"]
        data["tweet_url"] = tweet_url

        # Images
        image_tags = self.soup.find_all("img", alt="Image")
        image_urls = [img.get("src") for img in image_tags if img.get("src")]
        data["image_urls"] = ", ".join(image_urls)

        # Engagement
        def get_count(selector):
            btn = self.soup.find("button", attrs={"data-testid": selector})
            if btn:
                span = btn.find("span", class_="css-1jxf684")
                if span:
                    return span.get_text(strip=True)
            return None

        data["replies"] = get_count("reply")
        data["retweets"] = get_count("retweet")
        data["likes"] = get_count("like")

        views_link = self.soup.find("a", href=True, attrs={"href": lambda href: href and "analytics" in href})
        views = None
        if views_link:
            views_span = views_link.find("span", class_="css-1jxf684")
            if views_span:
                views = views_span.get_text(strip=True)
        data["views"] = views

        return data


def main():
    all_data = []
    folder = "tweets_html"
    files = [f for f in os.listdir(folder) if f.endswith(".html")]
    for file in files:
        with open(os.path.join(folder, file), encoding="utf-8") as f:
            html = f.read()
            scraper = TweetScraper(html)
            tweet_data = scraper.extract()
            all_data.append(tweet_data)
    
    # Save to CSV
    if all_data:
        keys = list(all_data[0].keys())
        with open("tweets_scraped.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_data)
        print("Saved extracted data to tweets_scraped.csv")

if __name__ == "__main__":
    main()
