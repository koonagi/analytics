import requests
import pandas as pd
pd.set_option('display.max_rows', None)

# アクセス情報
business_account_id = '<user_business_account_id>'
token = '<your_token>'
username = '<username>'
fields = 'name,username,biography,follows_count,followers_count,media_count'

# ユーザー情報を取得する
def user_info(business_account_id,token,username,fields):
    request_url = "https://graph.facebook.com/v11.0/{business_account_id}?fields=business_discovery.username({username}){{{fields}}}&access_token={token}".format(business_account_id=business_account_id,username=username,fields=fields,token=token)
#     print(request_url)
    response = requests.get(request_url)
    return response.json()['business_discovery']

print(user_info(business_account_id,token,username,fields))
