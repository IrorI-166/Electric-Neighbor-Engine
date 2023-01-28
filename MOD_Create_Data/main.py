from copyreg import pickle
from dataclasses import fields
from pprint import pprint
from datetime import datetime
import requests
import os
import json
import time

lowpre_json_dict = {}
highpre_json_dict = {}
json_dict = {}

dict_count = 0
for_index_count = 0

with open('MOD_Create_Data\Exclusion-words.txt','r',encoding='UTF-8') as l:
    word_list = l.read()

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
os.environ['BEARER_TOKEN'] = 'AAAAAAAAAAAAAAAAAAAAADWDfwEAAAAAiMXwuka0tCR3KLnqV7ylR6jdYTM%3DA8roriDF6VYrQ2Pr9Lsl4JR9BLlcKeDhsfY2EIBoZmZAZhVycC'
bearer_token = os.environ.get("BEARER_TOKEN")


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    json_response = response.json()
    return json_response


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))

def set_rules(delete):
    # You can adjust the rules if needed
    rules = [
        {"value": "-交換 -応募 です。 lang:ja -is:retweet -is:quote -emoji"}
    ]
    payload = {"add": rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))

def getTweetsFromConversation(conversation_id):
    global for_index_count
    global dict_count

    response = requests.get(
        f"https://api.twitter.com/2/tweets/search/recent?query=conversation_id:{conversation_id}&tweet.fields=author_id,conversation_id,created_at,in_reply_to_user_id,referenced_tweets&expansions=author_id,in_reply_to_user_id,referenced_tweets.id&user.fields=name,username", auth=bearer_oauth,
    )
    print(response.status_code)

    if response.status_code == 429:
        pass
    elif response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )

    json_response = json.loads(response.text)


    if json_response['meta']['result_count'] <= 1:
        return
    else:
        print("--------------- conversation tree ----------------")
        try:
            for tweet in json_response['includes']['tweets']:
                try:
                    tweet['referenced_tweets']
                except:
                    mother_tweet = tweet['text']
                    mother_tweet_id = tweet['id']
                    mother_tweet_author_id = tweet['author_id']
                    break
        except:
            pass

        try:
            print(f"Mother Tweet: {mother_tweet}")
            count = 0
        except:
            return

        for tweet in json_response['data']:
            if (
                tweet['referenced_tweets'][0]['type'] == 'replied_to' and
                tweet['referenced_tweets'][0]['id'] == mother_tweet_id and
                not tweet['author_id'] == mother_tweet_author_id
                ):
                count += 1
                print(f"{count}: {tweet['text']}")

                c_tweet = tweet['text'].strip()
                for word in word_list:
                    if word in c_tweet:
                        continue
                    if word in mother_tweet:
                        continue
                    if 'フォロー' and 'RT' in mother_tweet:
                        continue
                    elif '譲' and '求' in mother_tweet:
                        continue
                
                lowpre_json_dict = {'REQ'+str(for_index_count)+str(dict_count):mother_tweet, 'RES'+str(for_index_count)+str(dict_count):c_tweet}
                highpre_json_dict.update(lowpre_json_dict)
                lowpre_json_dict.clear()
                dict_count += 1
                for_index_count += 1
            json_dict.update(highpre_json_dict)

def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream?tweet.fields=conversation_id", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
        
    for response_line in response.iter_lines():
        try:
            json_response = json.loads(response_line)
        except:
            continue

        print("---------------------- response ---------------------")
        pprint(json_response)
        if json_response['data']['text'][0] == "@":
            getTweetsFromConversation(json_response['data']['conversation_id'])

def main():
    try:
        rules = get_rules()
        delete = delete_all_rules(rules)
        set = set_rules(delete)
        get_stream(set)
    
    finally:
        with open('./MOD_Create_Data/tweet/pre-conversation.json', 'w', encoding='UTF-8') as f:
            json.dump(json_dict, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()