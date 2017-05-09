# coding: utf-8 

# オプションについて 前から順に、日本語記事のファイル（何個でも）、英語記事のファイル１個、辞書ファイル、出力ファイル
#例：python main.py 2015_raw/J201501.txt 2015_raw/J201502.txt 2015/2015_2.txt /share/tool/MT/corpus/YOMIURI/sample.dic feb_text.txt




import sys
import mojimoji
from pyknp import Juman
import nltk
import json
import os.path

juman = Juman()

argvs = sys.argv
argc = len(argvs)



import codecs


#g = codecs.open(argvs[2], 'w', 'utf8', 'ignore')



def ja_categolize(line, dic):    #日本語のデータを、日付、ID、タイトル、内容、タイトルのbag of word、内容のbag of wordに分類。
    if u"＼Ｃ０＼" in line:
        date = mojimoji.zen_to_han(line[4:12])
        year = int(date[0:4])
        month = int(date[4:6])
        day = int(date[6:8])
        ID = line[4:]
        dic["year"] = year
        dic["month"] = month
        dic["day"] = day
        dic["id"] = ID

        return dic
    elif u"＼Ｔ１＼" in line:
        title = line[4:].strip()
        dic["raw_title"] = title
        title = make_ja_bag(title)
        dic["title"] = title
        return dic
    elif u"＼Ｔ２＼" in line:
        content = line[5:]
        if "raw_content" in dic:
            dic["raw_content"] = dic["raw_content"] + content 
        else:
            dic["raw_content"] = content
        content = make_ja_bag(content.strip())
        if "content" in dic:
            dic["content"].update(content)
        else:
            dic["content"] = content
        return dic
    else:
        return dic
def make_ja_bag(sentence):    #日本語のbag of word生成
    bag_of_words = {}
    result = juman.analysis(sentence)
    for mrph in result.mrph_list():
        if mrph.hinsi == u"形容詞" or mrph.hinsi == u"連体詞" or mrph.hinsi == u"副詞" or mrph.hinsi == u"感動詞" or mrph.hinsi == u"名詞" or mrph.hinsi == u"動詞" or mrph.hinsi == u"未定義語":
            if bag_of_words.get(mrph.midasi) == None:
                bag_of_words[mrph.midasi] = 1
            else:
                bag_of_words[mrph.midasi] = bag_of_words[mrph.midasi]+1
#            a.append(mrph.midasi.encode('utf-8'))
    return bag_of_words
def en_categolize(line, dic, i):#英語のデータを、日付、ID、タイトル、内容、タイトルのbag of word、内容のbag of wordに分類。
    if i % 3 == 0:
        year = int(line[0:4])
        month = int(line[4:6])
        day = int(line[6:8])
        ID = line
        dic["year"] = year
        dic["month"] = month
        dic["day"] = day
        dic["id"] = ID
        return dic
    elif i % 3 == 1:
        dic["raw_title"] = line
        title, proper_name_title, numeral_title  = make_en_bag(line)
        dic["title"] = title
        dic["proper_name_title"] = proper_name_title
        dic["numeral_title"] = numeral_title
        return dic
    elif i % 3 == 2:
        dic["raw_content"] = line
        content, proper_name_content, numeral_content = make_en_bag(line)
        dic["content"] = content
        dic["proper_name_content"] = proper_name_content
        dic["numeral_content"] = numeral_content
        return dic
def make_en_bag(sentence):    #英語のbag of wordの生成、内容語、固有名詞、数詞に関して三種類を作成
    bag_of_words = {}
    proper_name = {}
    numeral = {}
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    for word in tagged:
        if word[1] == "CD" or word[1] == "FW" or word[1] == "JJ" or word[1] == "JJR" or word[1] == "JJS" or word[1] == "LS" or word[1] == "NN" or word[1] == "NNS" or word[1] == "NNP" or word[1] == "NNPS" or word[1] == "PP" or word[1] == "PP$" or word[1] == "RB" or word[1] == "RBR" or word[1] == "RBS" or word[1] == "VB" or word[1] == "VBD" or word[1] == "VBG" or word[1] == "VBN" or word[1] == "VBP" or word[1] == "VBZ":
            if bag_of_words.get(word[0]) == None:
                bag_of_words[word[0]] = 1
            else:
                bag_of_words[word[0]] = bag_of_words[word[0]]+1
            if word[1] == "NNP" or word[1] == "NNPS":
                if proper_name.get(word[0]) == None:
                    proper_name[word[0]] = 1
                else:
                    proper_name[word[0]] = proper_name[word[0]] + 1
            elif word[1] == "CD":
                if numeral.get(word[0]) == None:
                    numeral[word[0]] = 1
                else:
                    numeral[word[0]] = numeral[word[0]] + 1
    return bag_of_words, proper_name, numeral
def make_dict():#辞書ファイルをキーを英単語にした辞書にする。日本語はリスト型で一英単語に対し、複数の日本単語が対応する。
    f = codecs.open(argvs[argc-2], 'r', 'utf8', 'ignore')
    text = f.readlines()
    word_dict = {}
    for line in text:
        line = line.strip()
        l = line.find("\t")
        if word_dict.get(line[0:l]) == None:
            word_dict[line[0:l]] = [line[l+1:]]
        else:
            word_dict[line[0:l]].append(line[l+1:])
    f.close()
    return word_dict
def search_best_sent(ja_art, en_art, word_dict):#記事の探索
    g = codecs.open(argvs[argc-1], 'w', 'utf8', 'ignore')
    for i in range(len(en_art)):
        print(len(en_art), i)
        en_year = en_art[i]["year"]
        en_month = en_art[i]["month"]
        en_day = en_art[i]["day"]
        en_title = en_art[i]["title"]
        en_proper_name_title = en_art[i].get("proper_name_title")
        en_numeral_title = en_art[i].get("numeral_title")
        en_content = en_art[i]["content"]
        en_proper_name_content = en_art[i].get("proper_name_content")
        en_numeral_content = en_art[i].get("numeral_content")
        en_raw_title = en_art[i]["raw_title"]
        en_raw_content = en_art[i]["raw_content"]
        en_id = en_art[i]["id"]
        best_sent = []
        ex_best_sent = []
        x = 0
        k = len(en_content)
        for j in range(len(ja_art)):
            ti_score = 0
            unk_ti_word = 0
            pro_ti_score = 0
            unk_pro_ti_word = 0
            num_ti_score = 0
            co_score = 0
            unk_co_word = 0
            pro_co_score = 0
            unk_pro_co_word = 0
            num_co_score = 0
            ja_year = ja_art[j].get("year")
            ja_month = ja_art[j].get("month")
            ja_day = ja_art[j].get("day")
            ja_id = ja_art[j].get("id")
            ja_title = ja_art[j].get("title")
            ja_content = ja_art[j].get("content")
            if ja_year < en_year or ja_year == en_year and ja_month < en_month < ja_month+3 or ja_year == en_year and ja_month == en_month and ja_day <= en_day:
                for en_title_word in en_title.keys(): #タイトルについて
                    dict_return = word_dict.get(en_title_word)#タイトル内の英単語に対応する日単語が存在すると＋１、固有名詞、数詞についても同様
                    if ja_title == None:
                        pass
                    elif not dict_return == None:
                        for word in dict_return:
                            if not ja_title.get(word) == None:
                                ti_score += 1
                                break
                    else:
                        unk_ti_word += 1        
                if not en_proper_name_title == {}:
                    for proper_name in en_proper_name_title.keys():
                        dict_return = word_dict.get(proper_name)
                        if ja_title == None:
                            pass
                        elif not dict_return == None:
                            for word in dict_return:
                                if not ja_title.get(word) == None:
                                    pro_ti_score += 1
                                    break
                        else:
                            unk_pro_ti_word += 1
                if not en_numeral_title == {}:
                    for numeral in en_numeral_title.keys():
                        numeral = mojimoji.han_to_zen(numeral)
                        if ja_title == None:
                            pass
                        elif not ja_title.get(numeral) == None:
                            num_ti_score += 1

                for en_content_word in en_content.keys():#内容について
                    dict_return = word_dict.get(en_content_word)#タイトルと同じ方式でスコアをつける
                    if ja_content == None:
                        pass
                    elif not dict_return == None:
                        for word in dict_return:
                            if not ja_content.get(word) == None: 
                                co_score += 1
                                break
                    else:
                        unk_co_word += 1
                if not en_proper_name_content == {}:
                    for proper_name in en_proper_name_content:
                        dict_return = word_dict.get(proper_name)
                        if ja_content == None:
                            pass
                        elif not dict_return == None:
                            for word in dict_return:
                                if not ja_content.get(word) == None:
                                    pro_co_score += 1
                                    break
                        else:
                            unk_pro_co_word += 1
                if not en_numeral_content == {}:
                    for numeral in en_numeral_content.keys():
                        dict_return = mojimoji.han_to_zen(numeral)
                        if ja_content == None:
                            pass
                        elif not ja_content.get(numeral) == None:
                            num_co_score += 1

            else:
                break
            co_score = (float(co_score)/(len(en_content)-unk_co_word))*100#スコア＝（対応した単語の数）/（（記事内の単語の数）ー（辞書に存在しなかった未知語））
            if not len(en_numeral_content) + len(en_proper_name_content) == 0:
                ex_co_score = (float(pro_co_score+num_co_score)/(len(en_numeral_content)+len(en_proper_name_content)-unk_pro_co_word))*100 #名詞、数詞に関するスコア＝（（対応した数詞、固有名詞の数）/（（記事内の数詞、固有名詞の数）ー（辞書に存在しなかった未知語）） 
            else:
                ex_co_score = 0
            if len(ex_best_sent) < 20 and not ex_co_score == 0:#名詞、数詞に関するスコアのtop20を決定、そこに入らなかったものの中からスコアでtop20を決定し表示
                a = []
                a.append(ex_co_score)
                a.append(ja_art[j]["raw_title"])
                a.append(ja_art[j]["raw_content"])
                a.append(ja_id)
                ex_best_sent.append(a)
                ex_best_sent.sort(key=lambda x:x[0])
            elif len(ex_best_sent) == 20 and ex_best_sent[0][0] < ex_co_score:
                a = []
                a.append(ex_co_score)
                a.append(ja_art[j]["raw_title"])
                a.append(ja_art[j]["raw_content"])
                a.append(ja_id)
                del ex_best_sent[0]
                ex_best_sent.append(a)
                ex_best_sent.sort(key=lambda x:x[0])

            elif len(best_sent) < 20:
                a = []
                a.append(co_score)
                a.append(ja_art[j]["raw_title"])
                a.append(ja_art[j]["raw_content"])
                a.append(ja_id)
                best_sent.append(a)
                best_sent.sort(key=lambda x:x[0])
            elif len(best_sent) == 20 and best_sent[0][0] < co_score:
                a = []
                a.append(co_score)
                a.append(ja_art[j]["raw_title"])
                a.append(ja_art[j]["raw_content"])
                a.append(ja_id)
                del best_sent[0]
                best_sent.append(a)
                best_sent.sort(key=lambda x:x[0])
        if len(best_sent) > 0 or ex_best_sent > 0:
            g.write("#")
            g.write(en_id)
            g.write("\n")
            g.write(en_raw_title)
            g.write("\n")
            g.write(en_raw_content)
            g.write("\n")
            g.write("\n")
            for pair in reversed(ex_best_sent):
                g.write("#")
                g.write(pair[3])
                g.write("ex_score:"+str(pair[0]))
                g.write("\n")
                g.write("\n")
                g.write(pair[1])
                g.write("\n")
                g.write("\n")
                g.write(pair[2])
                g.write("\n")
                g.write("\n")
            for pair in reversed(best_sent):
                g.write("#")
                g.write(pair[3])
                g.write("score:"+str(pair[0]))
                g.write("\n")
                g.write("\n")
                g.write(pair[1])
                g.write("\n")
                g.write("\n")
                g.write(pair[2])
                g.write("\n")
                g.write("\n")
def prepro_ja():
    list_ja_article = []
    article = {}
    for i in range(argc-4):
        if not os.path.exists(argvs[i+1][:-4]+".json"):
            f = codecs.open(argvs[i+1], 'r', 'utf8', 'ignore')
            g = open(argvs[i+1][:-4]+".json", "w")
            text = f.readlines()
            j = 0
            for line in text:
                if u"＼Ｃ０＼" in line:
                    if not article == {}:
                        list_ja_article.append(article)
                    j += 1
#                    if j == 7:
 #                       break
                    article = {}
                article = ja_categolize(line, article)
            list_ja_article.append(article)
            article = {}
            json.dump(list_ja_article, g)
            f.close()
            g.close()
                        
def prepro_en():
    if not os.path.exists(argvs[argc-3][:-4]+".json"):
        f = codecs.open(argvs[argc-3], 'r', 'utf8', 'ignore')
        g = open(argvs[argc-3][:-4]+".json", "w")
        text = f.readlines()
        e = 0
        list_en_article = []
        article = {}
        
        for i in range(len(text)):
            e += 1
            if i % 3 == 0:
                list_en_article.append(article)
                article = {}
            article = en_categolize(text[i], article, i)
        list_en_article.append(article)
        del list_en_article[0]
        json.dump(list_en_article, g)
        f.close()
def main():    
    prepro_ja()
    prepro_en()
    word_dict = make_dict()
    list_ja_article = []
    for i in range(argc-4):
        f = open(argvs[i+1][:-4]+".json")
        list_ja_article.extend(json.load(f))
        f.close()
    f = open(argvs[argc-3][:-4]+".json")
    list_en_article = json.load(f)
    search_best_sent(list_ja_article, list_en_article, word_dict)

main()

