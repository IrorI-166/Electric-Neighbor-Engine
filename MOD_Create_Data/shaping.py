#config=UTF-8
import json
import re

data_list = []
EXword_list = []

with open('./MOD_Create_Data/Exclusion-words.txt','r',encoding='UTF-8') as l:
    preEXword_list = l.readlines()
    for ex in preEXword_list:
        ex = ex.replace('\n', '')
        EXword_list.append(ex)

with open('./MOD_Create_Data/tweet/pre-conversation.json', 'r', encoding='UTF-8') as p:
    pre_learninngdata_list = json.load(p)

data_index = len(pre_learninngdata_list) / 2

keywords = [("集客構築", "販売"), ("いいね", "現金"), ("ワク", "強制"),
            ("いいね", "振込"), ("フォロー", "トレード"), ("皆様", "配布"),
            ("ア ","ナ ", "ル "), ("大喜利", "お題"), ("募集","@"), ("募集","＠")
            ]

def txt_judge(REQ_txt, RES_txt):
    for word in EXword_list:
        if (word in REQ_txt) or (word in RES_txt):
            pattern = 1
            return pattern
        elif any(all(word in s for word in keyword) for keyword in keywords for s in [REQ_txt, RES_txt]):
            pattern = 1
            return pattern
        else:
            pattern = 0
    return pattern

def txt_shape(REQ_txt, RES_txt):
    REQ_txt = REQ_txt.replace('\n','')
    REQ_txt = re.sub('@[0-9a-zA-Z_]{1,15} ', '', REQ_txt)
    REQ_txt = re.sub('https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', REQ_txt)
    RES_txt = RES_txt.replace('\n','')
    RES_txt = re.sub('@[0-9a-zA-Z_]{1,15} ', '', RES_txt)
    RES_txt = re.sub('https?://[\w/:%#\$&\?\(\)~\.=\+\-]+', '', RES_txt)
    return REQ_txt, RES_txt

for i in range(int(data_index)):
    REQ_txt = pre_learninngdata_list['REQ'+str(i)+str(i)]
    RES_txt = pre_learninngdata_list['RES'+str(i)+str(i)]
    pattern = txt_judge(REQ_txt, RES_txt)
    if pattern == 1:
        continue
    
    REQ_txt, RES_txt = txt_shape(REQ_txt, RES_txt)
    with open("./MOD_Create_Data/tweet/learninng-data.txt", 'a', encoding='UTF-8') as fp:
        fp.write(f'REQ:{REQ_txt}\nRES:{RES_txt}\n')

print("成形完了")