#!/usr/bin/python
# -*- coding:utf-8 -*-
# **************************
# * Author      :  baiyyang
# * Email       :  baiyyang@163.com
# * Description :  
# * create time :  2018/1/9下午3:39
# * file name   :  reader.py


import jieba.posseg
import re
import sys
import codecs
reload(sys)
sys.setdefaultencoding('utf-8')


htmltag = ['症状和体征', '检查和检验', '治疗', '疾病和诊断', '身体部位']
englishtag = ['SYMPTOM', 'CHECK', 'TREATMENT', 'DISEASE', 'BODY']


def readFileUTF8(filename):
    fr = codecs.open(filename, 'r', 'utf-8')
    text = ''
    for line in fr:
        text += line.strip()
    return text


def extract_tag_information(text):
    res = {}
    for i, html in enumerate(htmltag):
        res[englishtag[i]] = []
        pattern = re.compile(r'<' + html + '>(.*?)</' + html + '>', re.S)
        contents = pattern.findall(text)
        for content in contents:
            content = re.compile('<[^>]+>', re.S).sub('', content)
            res[englishtag[i]].append(content)
    return res


def extract_all_information(text):
    pattern = re.compile('<(.*?)>(.*?)</\\1>', re.S)
    contents = pattern.findall(text)
    ans = ''
    for content in contents:
        content = re.compile('<[^>]+>', re.S).sub('', content[1])
        ans += content
        print content
    return ans


def getType(type):
    if type == '症状和体征':
        return 'SIGNS'
    elif type == '检查和检验':
        return 'CHECK'
    elif type == '疾病和诊断':
        return 'DISEASE'
    elif type == '治疗':
        return 'TREATMENT'
    elif type == '身体部位':
        return 'BODY'
    else:
        return 'OTHER'


def split(text):
    """以标签数据分割成list"""
    res = []
    start = 0
    end = 0
    while end < len(text):
        if text[end] == '<':
            # < 前面的信息写入
            if start != end:
                res.append(text[start: end])
                start = end + 1
            else:
                start += 1
            # <>中的信息
            end = go(text, start)
            res.append(text[start: end])
            start = end + 1
            end = start
        else:
            end += 1
    if start != end:
        res.append(text[start: end])
    return res


# 将标签数据集转换成ner格式的标准数据集
def text2nerformat(text):
    # 过滤掉所有的标签
    # content = re.compile('<[^>]+>', re.S).sub('', text)
    segment = jieba.posseg.cut(text)
    # 采用BIOSE方式
    # B: 开始，I：中间，O：无关词，S：单个词，E：结尾
    # 将训练数据转换为标准的ner格式的数据
    start = 0
    type = ''
    stack = []
    flag = 0
    features = []
    pieces = split(text)
    pre = 0
    for seg in segment:
        if seg.word == '<':
            flag = 1
            pre = 0
            continue
        elif seg.word == '>':
            flag = 0
            pre = 0
            continue

        if flag == 0:
            while start < len(pieces) and getType(pieces[start]) != 'OTHER':
                stack.append(getType(pieces[start]))
                start += 1
            while start < len(pieces) and getType(pieces[start][1:]) != 'OTHER':
                stack.pop()
                start += 1
            while start < len(pieces) and getType(pieces[start]) != 'OTHER':
                stack.append(getType(pieces[start]))
                start += 1
            index = pieces[start].find(seg.word, pre)
            pre = index + 1
            if len(stack) == 0:
                type = 'O'
                if start < len(pieces) and index + len(seg.word) == len(pieces[start]):
                    start += 1
            else:
                if start < len(pieces):
                    if index == 0 and len(seg.word) == len(pieces[start]):
                        type = 'S-' + stack[-1]
                        start += 1
                    elif index == 0 and len(seg.word) != len(pieces[start]):
                        type = 'B-' + stack[-1]
                    elif index != -1 and len(pieces[start]) - index == len(seg.word):
                        if start + 1 == len(pieces) or getType(pieces[start + 1]) == 'OTHER':
                            type = 'E-' + stack[-1]
                        else:
                            type = 'I-' + stack[-1]
                        start += 1
                    elif index != -1:
                        type = 'I-' + stack[-1]

            features.append([seg.word, seg.flag, type])
            # print '%s, %s, %s' % (seg.word, seg.flag, type)
    return features


def go(text, i):
    while i < len(text):
        if text[i] == '>':
            break
        else:
            i += 1
    return i


# 将标注过的ner数据集，提取出实体
def getNamedEntity(word, ner):
    ans = []
    cur = ''
    for i, tag in enumerate(ner):
        if 'B' == tag.split('-')[0]:
            cur += word[i]
        elif 'I' == tag.split('-')[0]:
            cur += word[i]
        elif 'E' == tag.split('-')[0]:
            cur += word[i]
            ans.append(cur)
            cur = ''
        elif 'S' == tag.split('-')[0]:
            if len(cur) == 0:
                ans.append(word[i])
            else:
                cur += word[i]
    return ans


if __name__ == '__main__':
    # fw = file('test1.txt', 'w')
    # for i in range(100, 101):
    #     filename = 'data/病史特点-' + str(i) + '.txt'
    #     answer = text2nerformat(readFileUTF8(filename))
    #     for [word, pos, ner] in answer:
    #         fw.write(word + '\t' + pos + '\t' + ner + '\n')
    #     print 'file ' + str(i) + ' has already finished!'
    # fw.flush()
    # fw.close()
    fr = codecs.open('test1.txt', 'r', 'utf-8')
    data = []
    for line in fr:
        fields = line.strip().split('\t')
        if len(fields) == 3:
            data.append(fields)
    word = [w for w, tag, label in data]
    ner = [label for w, tag, label in data]
    ans = getNamedEntity(word, ner)
    for a in ans:
        print a

