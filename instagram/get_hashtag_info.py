import requests
import pandas as pd
pd.set_option('display.max_rows', None)
import json

def main():
    # アクセス情報
    business_account_id = '<user_business_account_id>'
    token = '<your_token>'

    #インプット情報
    fields = 'id,media_type,media_url,permalink,like_count,comments_count,caption,timestamp'
    search_type = "top_media" #検索タイプ recent_media or top_media

    # 検索キーワード指定
    query = "<keyword>"
    print('ハッシュタグ:' +  query)

    # ハッシュIDの取得
    hash_id = hashtag_id(business_account_id,query,token)

    # ハッシュタグ 検索結果取得
    result = hashtag_info(hash_id,search_type,business_account_id,query,token,fields)

    # データの結合、重複排除
    df_concat = None
    df_concat = pd.DataFrame(result[0])
    if len(result) != 1:
        for i,g in enumerate(result):
            df_concat = pd.concat([pd.DataFrame(result[i]), df_concat], sort=True)
    df_concat_sort = df_concat.sort_values('timestamp').drop_duplicates('id').reset_index(drop='true')
    
    # 結果出力
    display(df_concat_sort)


# ハッシュIDの取得
def hashtag_id(business_account_id,query,token):
    id_search_url = "https://graph.facebook.com/ig_hashtag_search?user_id={business_account_id}&q={query}&access_token={token}".format(business_account_id=business_account_id,query=query,token=token)

    response = requests.get(id_search_url)
    
    return response.json()['data'][0]['id']

# ハッシュタグ情報の取得
def hashtag_info(hash_id,search_type,business_account_id,query,token,fields):
    all_response = []
    count = 0
    count_limit = 3

    request_url = "https://graph.facebook.com/{hash_id}/{search_type}?user_id={business_account_id}&q={query}&access_token={token}&fields={fields}".format(hash_id=hash_id,search_type=search_type,business_account_id=business_account_id,query=query,token=token,fields=fields)
    
    response = requests.get(request_url)
    result = response.json()
    all_response.append(result['data'])

    # 25件以上データがある場合は取得
    if 'next' in result['paging'].keys():
        next_url = result['paging']['next']
        
        while next_url is not None:
            request_url = next_url
            response = requests.get(request_url)
            result = response.json()
            all_response.append(result['data'])
            if 'next' in result['paging'].keys() and count < count_limit :
                next_url = result['paging']['next']
                count = count + 1
            else:
                next_url = None
    
    return all_response


if __name__ == "__main__":
    main()
