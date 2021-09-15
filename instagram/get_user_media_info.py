from pylab import rcParams
import requests
import pandas as pd
import matplotlib.pyplot as plt

pd.set_option('display.max_rows', None)

# アクセス情報
business_account_id = '<user_business_account_id>'
token = '<your_token>'
username = '<username>'
media_fields = 'timestamp,like_count,comments_count,caption'

# メディア情報を取得する
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


#データの可視化

df_concat = None
df_concat = pd.DataFrame(result[0])

if len != 1:
    for i,g in enumerate(result):
        df_concat = pd.concat([pd.DataFrame(result[i]), df_concat])

df_concat_sort = df_concat.sort_values('timestamp').drop_duplicates('id').reset_index(drop='true')

df_concat_sort.set_index('timestamp')
rcParams['figure.figsize'] = 20,10

fig, ax = plt.subplots(1, 1)
plt.plot(df_concat_sort['timestamp'].str[:10], df_concat_sort['like_count'],label='like_count')
plt.plot(df_concat_sort['timestamp'].str[:10], df_concat_sort['comments_count'],label='comments_count')
ax.legend()

for idx,label in enumerate(ax.get_xticklabels()):
    if idx % 2 == 0:
        label.set_visible(False)
plt.xticks(rotation=45)
fig.subplots_adjust(left=0.2)

# グラフ出力
plt.show()

# DataFrame出力
display(df_concat_sort)
