import requests
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials 
import gspread
import json
import datetime as dt
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import os
from google.oauth2 import service_account


# ユーザー情報を返す関数
def user_info(business_account_id,token,username,fields):
    request_url = "https://graph.facebook.com/v11.0/{business_account_id}?fields=business_discovery.username({username}){{{fields}}}&access_token={token}".format(business_account_id=business_account_id,username=username,fields=fields,token=token)
    response = requests.get(request_url)
    return response.json()['business_discovery']
    

# MAIN
def lambda_handler(event, context):
    # アクセス情報
    business_account_id = '<user_business_account_id>'
    token = '<your_token>'
    username = '<username>'
    fields = 'name,username,biography,follows_count,followers_count,media_count'
    
    # GCP関連
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    service_account_info = json.loads(os.environ['token'])
    credentials = service_account.Credentials.from_service_account_info(service_account_info, scopes=scope)
    gc = gspread.authorize(credentials)
    
    spreadsheet_key = '<your_spreadsheet_key>'
    sheet_name = 'user_info'
    workbook = gc.open_by_key(spreadsheet_key)
    worksheet = workbook.worksheet(sheet_name)

    # ユーザー情報を取得する
    result = user_info(business_account_id,token,username,fields)
    
    # 日時の挿入
    today = dt.date.today().strftime('%Y%m%d')
    result['date'] = today
    df_tmp = pd.DataFrame(result,index=['0',])
    df = df_tmp[['date','followers_count','follows_count','media_count']]

    # 既に入力済みの日付かどうかチェック
    date_list = worksheet.col_values(1)
    print('date_list:' + str(date_list))
    
    # 入力済みの日付出ない場合、値を追記
    if today not in date_list:
        workbook.values_append(sheet_name,{'valueInputOption': 'USER_ENTERED'},
                     {'values': df.values.tolist()}
                     )
        print('#DATA ADD')
        print('Datetime:' + today)
        print('---------')
    else:
        print('Nothing To Do')
