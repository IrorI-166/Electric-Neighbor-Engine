#config=UTF-8
import json
import re
import csv
import json
import MeCab

data_list = []
EXword_list = []

with open('MOD_Create_Data/Exclusion-words.txt','r',encoding='UTF-8') as l:
    preEXword_list = l.readlines()
    for ex in preEXword_list:
        ex = ex.replace('\n', '')
        EXword_list.append(ex)

with open('MOD_Create_Data/tweet/pre-conversation.json', 'r', encoding='UTF-8') as p:
    pre_learninngdata_list = json.load(p)

data_index = len(pre_learninngdata_list) / 2

keywords = [("集客構築", "販売"), ("いいね", "現金"), ("ワク", "強制"),
            ("いいね", "振"), ("フォロー", "トレード"), ("皆様", "配布"),
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
        elif (not REQ_txt) or (not RES_txt):
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

print("データ成形開始")
print("文章成型フェーズ")
for i in range(int(data_index)):
    REQ_txt = pre_learninngdata_list['REQ'+str(i)+str(i)]
    RES_txt = pre_learninngdata_list['RES'+str(i)+str(i)]

    REQ_txt, RES_txt = txt_shape(REQ_txt, RES_txt)

    pattern = txt_judge(REQ_txt, RES_txt)
    if pattern == 1:
        continue

    with open("MOD_Create_Data/tweet/learninng-data.txt", 'a', encoding='UTF-8') as fp:
        fp.write(f'REQ:{REQ_txt}\nRES:{RES_txt}\n')

###
#コーパス作成フェーズ 
###
print("コーパス作成フェーズ")

Learninngdata_list = []

wakati = MeCab.Tagger("-Owakati")
tagger = MeCab.Tagger()

with open("MOD_Create_Data/tweet/learninng-data.txt", "r", encoding="UTF-8") as fp:
    preLearninngdata_list = fp.readlines()
    for LD in preLearninngdata_list:
        LD = LD.replace('REQ:', '')
        LD = LD.replace('RES:', '')
        LD = LD.replace('\n', '')
        Learninngdata_list.append(LD)

#EOSと改行の削除
def split_EOS(text):
    text = text.replace('EOS\n', '')
    return text

for text in Learninngdata_list:
    text = tagger.parse(text)
    text = split_EOS(text)
    with open("ENE_brain/datas/corpus.txt", "a", encoding="UTF-8") as fp:
        fp.write(text)

###
#単語出現数カウントフェーズ
#Written by Mr.Zeruku
###
print("単語出現数カウントフェーズ")

# corpus.txtとcorpus.jsonを読み込む
with (
    open("ENE_brain/datas/corpus.txt", "r", encoding="UTF-8") as cp,
    open("MOD_Create_Data/temporary.json", "r", encoding="UTF-8") as tsp,
):
    # corpus.txtを読み込んで、タブで区切られた要素をリストとして取得する
    diff = csv.reader(cp, delimiter="	")
    mats = [v for v in diff if v and v[0]]

    # temp.jsonを読み込んで、辞書型に変換する
    # temp.jsonは、このスクリプトで扱いやすい形になっている。
    temp_dict = json.load(tsp)

# temp_dictに、単語ごとの出現回数を追加していく
for mat in mats:
    temp_dict[mat[0]] = temp_dict.get(mat[0], 0) + 1

# 空の配列として呼ぶことで、何回コードを実行しても正常に動作するように変更
corpus_json_dict = []

# temp_dictに含まれる単語ごとの出現回数をcorpus_json_dictに追加する
corpus_json_dict.extend([{"Word": k, "Occurrences": v} for k, v in temp_dict.items()])

# corpus_result.jsonという名前で、結果を保存する
with (
    open("ENE_brain/datas/corpus.json", "w", encoding="UTF-8") as cf,
    open("MOD_Create_Data/temporary.json", "w", encoding="UTF-8") as tf,
):
    json.dump(corpus_json_dict, cf, ensure_ascii=False, indent=4)
    json.dump(temp_dict, tf, ensure_ascii=False, indent=4)

print("成形完了")