import requests
import pandas as pd
pd.set_option('display.max_rows', None)

"""
1.アクセス情報/パラメータ
"""
business_account_id = '<user_business_account_id>'
token = '<your_token>'
username = '<username>'

media_fields = 'timestamp,permalink,media_type'
folderpath = './image/'


"""
2.メディア情報取得
"""

def user_media_info(business_account_id,token,username,media_fields):
    all_response = []
    request_url = "https://graph.facebook.com/v11.0/{business_account_id}?fields=business_discovery.username({username}){{media{{{media_fields}}}}}&access_token={token}".format(business_account_id=business_account_id,username=username,media_fields=media_fields,token=token)
 #     print(request_url)
    response = requests.get(request_url)
    result = response.json()['business_discovery']
    
    all_response.append(result['media']['data'])
    
    # 過去分がある場合は過去分全て取得する(1度に取得できる件数は25件)
    if 'after' in result['media']['paging']['cursors'].keys():
        next_token = result['media']['paging']['cursors']['after']
        while next_token is not None:
            request_url = "https://graph.facebook.com/v11.0/{business_account_id}?fields=business_discovery.username({username}){{media.after({next_token}){{{media_fields}}}}}&access_token={token}".format(business_account_id=business_account_id,username=username,media_fields=media_fields,token=token,next_token=next_token)
#             print(request_url)
            response = requests.get(request_url)
            result = response.json()['business_discovery']
            all_response.append(result['media']['data'])
            if 'after' in result['media']['paging']['cursors'].keys():
                next_token = result['media']['paging']['cursors']['after']
            else:
                next_token = None
    
    return all_response

result = user_media_info(business_account_id,token,username,media_fields)
df_concat = None
df_concat = pd.DataFrame(result[0])

# Resultの結果を一つのDataframeに結合する
if len != 1:
    for i,g in enumerate(result):
        df_concat = pd.concat([pd.DataFrame(result[i]), df_concat])

df_concat_sort = df_concat.sort_values('timestamp').drop_duplicates('id').reset_index(drop='true')
df_concat_sort[:3]


"""
3.インスタから画像を取得
"""

def make_image_url(permalinks):
    """
    イメージ取得用URL作成
    """
    image_url_list = []
    for permalink in permalinks:
        permalink = permalink + 'media/?size=l'
        # Permalinkはリダイレクトされるため、リダイレクトURLの取得
        headers = {'User-Agent': ''}
        redirect_url = requests.get(permalink,headers=headers).url
        
        # Image URLを取得できないコンテンツは空文字を入れる
        if permalink != redirect_url:
            image_url_list.append(redirect_url)
        else:
            image_url_list.append('')
        
    return image_url_list

def get_image(folderpath,image_urls,timestamp,id):
    """
    画像イメージの保存
    """   
    for (image_url,timestamp,id) in zip(image_urls,timestamp,id):  
        
        # Image URLが取得できていないコンテンツは除外
        if image_url != '':
            # 画像データの取得
            file_name = '{}{}_{}.jpg'.format(folderpath,timestamp[:10],id)
            response = requests.get(image_url)
            image = response.content
            with open(file_name, "wb") as f:
                f.write(image)


# イメージ取得用URL作成
df_concat_sort['image_url'] = make_image_url(df_concat_sort['permalink'])

# 画像イメージの保存
get_image(folderpath,df_concat_sort['image_url'],df_concat_sort['timestamp'],df_concat_sort['id'])

