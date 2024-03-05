"""Google review crawler."""
# import pandas as pd
# import html2text
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs
import json
import re
import requests


url = "https://www.google.com/maps/place/%E5%8F%B0%E5%8C%97101%2F%E4%B8%96%E8%B2%BF/@25.0341222,121.5618325,17z/data=!4m10!1m2!2m1!1z5Y-w5YyXMTAx!3m6!1s0x3442abb6625e6f89:0xf3ab83833fbea1dd!8m2!3d25.0330304!4d121.5627598!15sCgnlj7DljJcxMDGSAQ5zdWJ3YXlfc3RhdGlvbuABAA!16s%2Fm%2F03cz9sm?hl=zh-TW&entry=ttu"


# def parse_description(description_tag):
#     """Parse."""
#     description_text = h.handle(str(description_tag))
#     return description_text


# h = html2text.HTML2Text()
# h.ignore_links = True

def parse_description(description_tag):
    """Parse."""
    soup = bs(str(description_tag), 'html.parser')
    description_text = soup.get_text()
    return description_text


def time(review_date):
    """Format."""
    now = datetime.now()
    time = re.search(r"\D+", review_date)[0].strip()
    if "時" in time:
        review_date = now - timedelta(hours=int(re.search(r"\d+", review_date)[0]))
    elif "天" in time:
        review_date = now - timedelta(days=int(re.search(r"\d+", review_date)[0]))
    elif "週" in time:
        review_date = now - timedelta(weeks=int(re.search(r"\d+", review_date)[0]))
    elif "月" in time:
        review_date = now - relativedelta(months=int(re.search(r"\d+", review_date)[0]))
    else:  # 年
        review_date = now - relativedelta(years=int(re.search(r"\d+", review_date)[0]))
    return review_date


# 下一頁review內容的token(寫進url)
next_page_token = ""

# 設定biz_id(寫進url)
biz_id = re.search(r"1s(0.*?\:.*?)[^a-zA-Z\d\s:]", url)  # 寫成迴圈的時候要改一下

if not biz_id:
    print("Not a valid url.")
biz_id = biz_id.groups()[0]

# print(biz_id)
reviewData = []

while True:

    print('已下載', len(reviewData))
    url = f'https://www.google.com/async/reviewSort?yv=3&async=feature_id:{biz_id},review_source:All%20reviews,sort_by:newestFirst,is_owner:false,filter_text:,associated_topic:,next_page_token:{next_page_token},_pms:s,_fmt:json'
    response = requests.get(url)
    prefix = ")]}'"
    if response.text.startswith(prefix):
        response_text = response.text[len(prefix):]
    # response = response.text.removeprefix(")]}'")
    json_data = json.loads(response_text)["localReviewsProto"]
    review_data = json_data["other_user_review"]
    # breakpoint()

    for result in review_data:
        rating = result['star_rating']['value']
        profile_pic = result['profile_photo_url']
        profile_pic = re.sub('=s(\d+)-', '=s180-', profile_pic)
        reviewer_name = result['author_real_name']
        review_date = result['publish_date']['localized_date']
        share_url = result["share_url"]
        review_id = result["review_id"]
        if result.get('review_text'):
            review_text = parse_description(result['review_text']['full_html'])
        else:
            review_text = ""

        info_dict = {}
        info_dict['author'] = reviewer_name
        info_dict['rating'] = rating
        info_dict["date"] = time(review_date)
        info_dict["text"] = review_text
        info_dict["share_url"] = share_url
        info_dict["review_id"] = review_id

        reviewData.append(info_dict)
        print(info_dict)
    next_page_token = json_data.get('next_page_token', '').strip()
    if not next_page_token:
        break

# reviews_info_header = list(reviewData[0].keys())
# reviews_info_df = pd.DataFrame.from_records(reviewData, columns=reviews_info_header)
# reviews_info_df.to_csv(f'./{alias}_review.csv')
# reviews_info_df.to_csv("./123_review.csv", index=False)
