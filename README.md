# medical_ner_crfsuite
基于条件随机场的医疗电子病例的命名实体识别

## INTRODUCE
medical_ner_crfsuite是[CCKS2017全国知识图谱与语义大会](http://www.ccks2017.com/)，医疗电子病例命名实体识别评测任务的一个可执行demo，采用的方法是条件随机场(CRF)，实现CRF的第三方库为[python-crfsuite](https://github.com/scrapinghub/python-crfsuite)。目前该demo准确率为68%，召回率为62%，F1值为64.8%。

## METHOD
1. 数据预处理。调用reader.py中的text2nerformat方法，将data中的数据集转换成NER任务中常用的数据格式
2. 训练模型。通过crf_unit.py，训练CRF模型，目前CRF中的特征包括上下两个词语及其词性，分词和词性标注调用[jieba](https://github.com/fxsjy/jieba)
3. 评估模型。调用crf_unit.py中的bio_classification_report方法，评估模型。

## DEPENDENCY
> pycrfsuite：pip install python-crfsuite

> zhon：pip install zhon

## TODO
1. 参考文献[Clinical Named Entity Recognition Method Based on CRF Yanxu Chen, Gang Zhang, Haizhou Fang, Bin He, Yi Guan](http://ceur-ws.org/Vol-1976/paper09.pdf)，提升模型准确率。
2. 使用深度学习Bi_LSTM_CRF实现命名实体识别任务。
