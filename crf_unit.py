#!/usr/bin/python
# -*- coding:utf-8 -*-
# **************************
# * Author      :  baiyyang
# * Email       :  baiyyang@163.com
# * Description :  
# * create time :  2018/1/10上午10:29
# * file name   :  crf_unit.py


import sys
import codecs
import pycrfsuite
import string
import zhon.hanzi as zh
import reader
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelBinarizer
reload(sys)
sys.setdefaultencoding('utf-8')


# 获取数据
def readData(filename):
    fr = codecs.open(filename, 'r', 'utf-8')
    data = []
    for line in fr:
        fields = line.strip().split('\t')
        if len(fields) == 3:
            data.append(fields)
    return data


train = readData('train.txt')
test = readData('test.txt')


# 判断是否为标点符号
# punctuation
def ispunctuation(word):
    punctuation = string.punctuation + zh.punctuation
    if punctuation.find(word) != -1:
        return True
    else:
        return False


# 特征定义
def word2features(sent, i):
    """返回特征列表"""
    word = sent[i][0]
    postag = sent[i][1]
    features = [
        'bias',
        'word=' + word,
        'word_tag=' + postag,
    ]
    if i > 0:
        features.append('word[-1]=' + sent[i-1][0])
        features.append('word[-1]_tag=' + sent[i-1][1])
        if i > 1:
            features.append('word[-2]=' + sent[i-2][0])
            features.append('word[-2, -1]=' + sent[i-2][0] + sent[i-1][0])
            features.append('word[-2]_tag=' + sent[i-2][1])
    if i < len(sent) - 1:
        features.append('word[1]=' + sent[i+1][0])
        features.append('word[1]_tag=' + sent[i+1][1])
        if i < len(sent) - 2:
            features.append('word[2]=' + sent[i+2][0])
            features.append('word[1, 2]=' + sent[i+1][0] + sent[i+2][0])
            features.append('word[2]_tag=' + sent[i+2][1])
    return features


def sent2feature(sent):
    return [word2features(sent, i) for i in range(len(sent))]


def sent2label(sent):
    return [label for word, tag, label in sent]


def sent2word(sent):
    return [word for word, tag, label in sent]


X_train = sent2feature(train)
y_train = sent2label(train)

X_test = sent2feature(test)
y_test = sent2label(test)

# 训练模型
model = pycrfsuite.Trainer(verbose=True)
model.append(X_train, y_train)
model.set_params({
    'c1': 1.0,  # coefficient for L1 penalty
    'c2': 1e-3,  # coefficient for L2 penalty
    'max_iterations': 100,  # stop earlier
    # include transitions that are possible, but not observed
    'feature.possible_transitions': True,
    'feature.minfreq': 3
})

model.train('./medical.crfsuite')


# 预测数据
tagger = pycrfsuite.Tagger()
tagger.open('./medical.crfsuite')

# 一份测试数据集
print ' '.join(sent2word(readData('test1.txt')))
predicted = tagger.tag(sent2feature(readData('test1.txt')))
correct = sent2label(readData('test1.txt'))

# 预测结果对比
print 'Predicted: ', ' '.join(predicted)
print 'Correct: ', ' '.join(correct)

# 预测准确率
num = 0
for i, tag in enumerate(predicted):
    if tag == correct[i]:
        num += 1
print 'accuracy: ', num * 1.0 / len(predicted)


# 实体抽取结果
ans = reader.getNamedEntity(sent2word(readData('test1.txt')), predicted)
for a in ans:
    print a


# 评估模型
def bio_classification_report(y_true, y_pred):
    """
    Classification report for a l ist of BIOSE-encoded sequences.
    It computes token-level metrics and discards 'O' labels.
    :param y_true:
    :param y_pred:
    :return:
    """
    lb = LabelBinarizer()
    y_true_combined = lb.fit_transform(y_true)
    y_pred_combined = lb.transform(y_pred)

    tagset = set(lb.classes_) - {'O'}
    tagset = sorted(tagset, key=lambda tag: tag.split('-', 1)[::-1])
    class_indices = {
        cls: idx for idx, cls in enumerate(lb.classes_)
    }

    return classification_report(
        y_true_combined,
        y_pred_combined,
        labels=[class_indices[cls] for cls in tagset],
        target_names=tagset
    )


y_pred = list(tagger.tag(X_test))
print bio_classification_report(y_test, y_pred)



