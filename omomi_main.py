# coding: utf-8 
# オプションについて 前から順に、日本語記事のファイル（何個でも）、英語記事のファイル１個、辞書ファイル、出力ファイル

#例：python main.py 2015_raw/J201501.txt 2015_raw/J201502.txt 2015/2015_2.txt /share/tool/MT/corpus/YOMIURI/sample.dic feb_text.txt




import sys
import mojimoji
from pyknp import Juman
import nltk


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
            dic["content"] = content + dic["content"]
        else:
            dic["content"] = content
        return dic
    else:
        return dic
def make_ja_bag(sentence):    #日本語のbag of word生成
    a = []
    result = juman.analysis(sentence)
    for mrph in result.mrph_list():
        if mrph.hinsi == u"形容詞" or mrph.hinsi == u"連体詞" or mrph.hinsi == u"副詞" or mrph.hinsi == u"感動詞" or mrph.hinsi == u"名詞" or mrph.hinsi == u"動詞" or mrph.hinsi == u"未定義語":
            a.append(mrph.midasi.encode('utf-8'))
    bag_of_word = tuple(a)
    return bag_of_word
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
        title, koyu_title, num_title  = make_en_bag(line)
        dic["title"] = title
        dic["koyu_title"] = koyu_title
        dic["num_title"] = num_title
        return dic
    elif i % 3 == 2:
        dic["raw_content"] = line
        content, koyu_content, num_content = make_en_bag(line)
        dic["content"] = content
        dic["koyu_content"] = koyu_content
        dic["num_content"] = num_content
        return dic
def make_en_bag(sentence):    #英語のbag of wordの生成、内容語、固有名詞、数詞に関して三種類を作成
    lis = []
    koyu_lis = []
    num_lis = []
    tokens = nltk.word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    for word in tagged:
        if word[1] == "CD" or word[1] == "FW" or word[1] == "JJ" or word[1] == "JJR" or word[1] == "JJS" or word[1] == "LS" or word[1] == "NN" or word[1] == "NNS" or word[1] == "NNP" or word[1] == "NNPS" or word[1] == "PP" or word[1] == "PP$" or word[1] == "RB" or word[1] == "RBR" or word[1] == "RBS" or word[1] == "VB" or word[1] == "VBD" or word[1] == "VBG" or word[1] == "VBN" or word[1] == "VBP" or word[1] == "VBZ":
            lis.append(word[0])
            if word[1] == "NNP" or word[1] == "NNPS":
                koyu_lis.append(word[0])
            elif word[1] == "CD":
                num_lis.append(word[0])
    return tuple(lis), tuple(koyu_lis), tuple(num_lis)
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
        en_line = en_art[i]
        en_year = en_line["year"]
        en_month = en_line["month"]
        en_day = en_line["day"]
        en_title = en_line["title"]
        en_koyu_title = en_line["koyu_title"]
        en_num_title = en_line["num_title"]
        en_content = en_line["content"]
        en_koyu_content = en_line["koyu_content"]
        en_num_content = en_line["num_content"]
        en_raw_title = en_line["raw_title"]
        en_raw_content = en_line["raw_content"]
        en_id = en_line["id"]
        best_sent = []
        ex_best_sent = []
        x = 0
        k = len(en_content)
        i = 0
        for ja_line in ja_art:
            i += 1
            z = 0
            y = 0
            ti_score = 0
            co_score = 0
            ex_ti_score = 0
            ex_co_score = 0
            ja_year = ja_line.get("year")
	    ja_month = ja_line.get("month")
	    ja_day = ja_line.get("day")
            ja_id = ja_line.get("id")
            ja_title = ja_line.get("title")
            ja_content = ja_line.get("content")
            if ja_year < en_year:
                for i in range(len(en_title)): #タイトルについて
                    a = word_dict.get(en_title[i])#タイトル内の英単語に対応する日単語が存在すると＋１、固有名詞、数詞についても同様
                    if ja_title == None:
                        pass
                    elif not a == None:
                        for word in a:
                            if word.encode('utf-8') in ja_title:
                                ti_score += 1
                                break
                if not len(en_koyu_title) == 0:
                    for i in range(len(en_koyu_title)):
                        a = word_dict.get(en_koyu_title[i])
                        if ja_title == None:
                            pass
                        elif not a == None:
                            for word in a:
                                if word.encode('utf-8') in ja_title:
                                    ex_ti_score += 1
                                    break
                if not len(en_num_title) == 0:
                    for i in range(len(en_num_title)):
                        a = mojimoji.han_to_zen(en_num_title[i])
                        if ja_title == None:
                            pass
                        elif not a == None:
                            if a.encode('utf-8') in ja_title:
                                ex_ti_score += 1
                                break

                for i in range(len(en_content)):#内容について
                    b = word_dict.get(en_content[i])#タイトルと同じ方式でスコアをつける
                    if ja_content == None:
                        pass
                    elif not b == None:
                        for word in b:
                            if word.encode('utf-8') in ja_content:
                                co_score += 1
                                break
                    elif b == None:
                        z += 1
                if not len(en_koyu_content) == 0:
                    for i in range(len(en_koyu_content)):
                        a = word_dict.get(en_koyu_content[i])
                        if ja_content == None:
                            pass
                        elif not a == None:
                            for word in a:
                                if word.encode('utf-8') in ja_content:
                                    co_score += 1
                                    break
                        elif a == None:
                            y += 1
                if not len(en_num_content) == 0:
                    for i in range(len(en_num_content)):
                        a = mojimoji.han_to_zen(en_num_content[i])
                        if ja_content == None:
                            pass
                        elif not a == None:
                            if a.encode('utf-8') in ja_content:
                                ti_score += 1
                                break
                        elif a == None:
                            y += 1

            elif ja_year == en_year and ja_month < en_month < ja_month+3:
                for i in range(len(en_title)):
                    a = word_dict.get(en_title[i])
                    if ja_title == None:
                        pass
                    elif not a == None:
                        for word in a:
                            if word.encode('utf-8') in ja_title:
                                ti_score += 1
                                break
                if not len(en_koyu_title) == 0:
                    for i in range(len(en_koyu_title)):
                        a = word_dict.get(en_koyu_title[i])
                        if ja_title == None:
                            pass
                        elif not a == None:
                            for word in a:
                                if word.encode('utf-8') in ja_title:
                                    ex_ti_score += 1
                                    break
                if not len(en_num_title) == 0:
                    for i in range(len(en_num_title)):
                        a = mojimoji.han_to_zen(en_num_title[i])
                        if ja_title == None:
                            pass
                        elif not a == None:
                            if a.encode('utf-8') in ja_title:
                                ex_ti_score += 1
                                break


                for i in range(len(en_content)):
                    b = word_dict.get(en_content[i])
                    if ja_content == None:
                        pass
                    elif not b == None:
                        for word in b:
                            if word.encode('utf-8') in ja_content:
                                co_score += 1
                                break
                    elif b == None:
                        z += 1
                if not len(en_koyu_content) == 0:
                    for i in range(len(en_koyu_content)):
                        a = word_dict.get(en_koyu_content[i])
                        if ja_content == None:
                            pass
                        elif not a == None:
                            for word in a:
                                if word.encode('utf-8') in ja_content:
                                    co_score += 1
                                    break
                        elif a == None:
                            y += 1
                if not len(en_num_content) == 0:
                    for i in range(len(en_num_content)):
                        a = mojimoji.han_to_zen(en_num_content[i])
                        if ja_content == None:
                            pass
                        elif not a == None:
                            if a.encode('utf-8') in ja_content:
                                co_score += 1
                                break
                        elif a == None:
                            y += 1
            elif ja_year == en_year and ja_month == en_month and ja_day <= en_day:
                for i in range(len(en_title)):
                    a = word_dict.get(en_title[i])
                    if ja_title == None:
                        pass
                    elif not a == None:
                        for word in a:
                            if word.encode('utf-8') in ja_title:
                                ti_score += 1
                                break
                if not len(en_koyu_title) == 0:
                    for i in range(len(en_koyu_title)):
                        a = word_dict.get(en_koyu_title[i])
                        if ja_title == None:
                            pass
                        elif not a == None:
                            for word in a:
                                if word.encode('utf-8') in ja_title:
                                    ex_ti_score += 1
                                    break
                if not len(en_num_title) == 0:
                    for i in range(len(en_num_title)):
                        a = mojimoji.han_to_zen(en_num_title[i])
                        if ja_title == None:
                            pass
                        elif not a == None:
                            if word.encode('utf-8') in ja_title:
                                ex_ti_score += 1
                                break


                for i in range(len(en_content)):
                    b = word_dict.get(en_content[i])
                    if ja_content == None:
                        pass
                    elif not b == None:
                        for word in b:
                            if word.encode('utf-8') in ja_content:
                                co_score += 1
                                break
                    elif b == None:
                        z += 1
                if not len(en_koyu_content) == 0:
                    for i in range(len(en_koyu_content)):
                        a = word_dict.get(en_koyu_content[i])
                        if ja_content == None:
                            pass
                        elif not a == None:
                            for word in a:
                                if word.encode('utf-8') in ja_content:
                                    co_score += 1
                                    break
                        elif a == None:
                            y += 1
                if not len(en_num_content) == 0:
                    for i in range(len(en_num_content)):
                        a = mojimoji.han_to_zen(en_num_content[i])
                        if ja_content == None:
                            pass
                        elif not a == None:
                            if a.encode('utf-8') in ja_content:
                                co_score += 1
                                break
                        elif a == None:
                            y += 1
            else:
                break
            co_score = (float(co_score)/(k-z))*100#スコア＝（対応した単語の数）/（（記事内の単語の数）ー（辞書に存在しなかった未知語））
            if len(best_sent) < 40:
                a = []
                a.append(co_score)
                a.append(ja_line["raw_title"])
		a.append(ja_line["raw_content"])
                a.append(ja_id)
                best_sent.append(a)
                best_sent.sort(key=lambda x:x[0])
            elif len(best_sent) == 40:
                if best_sent[0][0] < co_score:
                    a = []
		    a.append(co_score)
		    a.append(ja_line["raw_title"])
                    a.append(ja_line["raw_content"])
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

list_ja_article = []
article = {}
for i in range(argc-4):
    f = codecs.open(argvs[i+1], 'r', 'utf8', 'ignore')
    text = f.readlines()
    j = 0
    for line in text:
        if u"＼Ｃ０＼" in line:
            if not article == {}:
                list_ja_article.append(article)
            j += 1
#            if j == 7:
 #               break
            article = {}
        article = ja_categolize(line, article)
    list_ja_article.append(article)
    article = {}
    f.close()
f = codecs.open(argvs[argc-3], 'r', 'utf8', 'ignore')
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
f.close()
word_dict = make_dict()
search_best_sent(list_ja_article, list_en_article, word_dict)


