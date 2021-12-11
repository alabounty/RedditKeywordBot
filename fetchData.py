#TODO
#Create data structure for keyword, count, and timestamp then graph results
#

import requests
import time
from datetime import datetime, timezone

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}

keywords = {
    "nvidia": ["nvidia", "Nvidia","NVDA","NVIDIA"]
}

muted_users = ["AutoModerator"]


def send_notification(title: str, body: str):
    print("--- Message ---")
    print("Title:", title)
    print(body)
    print("-" * 30)


def fetch_comment_data_periodically(subreddit: str, interval: int, limit: int = 100, timeframe: str="hour"):
    keywordCounts = {}

    while True:
        print(datetime.now().strftime("%x - %X: Fetching Comments for"), subreddit)
        #Grab comments from the subreddit
        comments = get_comments(subreddit, limit)
        print(comments)
        #Find keyword matches
        if comments: 
          for comment, body in comments:
              matches = scan_comment_for_keywords(body, comment, keywords)
              if not matches:
                  continue
              if comment["author"] in muted_users:
                  continue

              utc = datetime.utcfromtimestamp(
                  comment["created_utc"]).replace(tzinfo=timezone.utc)
              local_time = utc.astimezone(tz=None)
              #match_text = ", ".join([m["kind"] for m in matches])
              
              #Count matches for each keyword
              for match in matches:
                keyword_match=match["kind"]
                if keyword_match in keywordCounts:
                  keywordCounts[keyword_match] += 1
                else:
                  keywordCounts[keyword_match] = 1
              #Parse and format the results
              comment_text = "Author: " + comment["author"]
              comment_text += "\nPermalink: " + comment["permalink"]
              comment_text += "\nCreated: " + \
                  local_time.strftime("%d %b, %H:%M:%S")
              comment_text += "\nBody: " + comment["body"]
              #send_notification("Match for '%s'" % match_text, comment_text)
        for key, value in keywordCounts.items():
          print(datetime.now().strftime("%x - %X:"), key,":",value)
        time.sleep(interval)


def get_comments(subreddit: str, limit: int = 100, timeframe: str="hour"):
    base_url = f'https://www.reddit.com/r/{subreddit}/comments.json?limit={limit}&t={timeframe}'
    res = requests.get(base_url, headers)
    if (res.status_code == 429):
      return
    comments = res.json()["data"]["children"]
    results = []
    for c in comments:
        comment = c["data"]
        results.append((comment, comment["body"]))
    return results
    


def scan_comment_for_keywords(comment: str, comment_obj: dict, keywords: dict):
    matches = []
    for k, phrases in keywords.items():
        for p in phrases:
            if p in comment.lower():
                matches.append({"kind": k, "comment": comment_obj})
                break
    return matches


if __name__ == "__main__":
    fetch_comment_data_periodically("python")