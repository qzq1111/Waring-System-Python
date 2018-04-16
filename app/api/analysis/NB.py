# coding: utf-8
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import re
import random
import jieba
import joblib

jieba.load_userdict(os.path.join(os.path.dirname(__file__), 'CompanyName.txt'))


class NBclassifier():
    stop_words = [line.strip().decode('utf-8')
                  for line in open(os.path.join(os.path.dirname(__file__), 'StopWords.txt'), 'r').readlines()]

    def __init__(self, clf_path=None, vec_path=None):
        '''
        创建对象时完成的初始化工作，判断分类器与vector路径是否为空，
        若为空则创建新的分类器与vector，否则直接加载已经持久化的分类器与vector。
        '''
        if clf_path is None or vec_path is None:
            self.clf = MultinomialNB()
            self.vec = TfidfVectorizer()
        else:
            self.clf = joblib.load(clf_path)

            self.vec = joblib.load(vec_path)

    # 保存模型
    def saveModel(self, clf_path="clf.m", vec_path="vec.m"):
        joblib.dump(self.clf, clf_path)
        joblib.dump(self.vec, vec_path)

    # 从文件夹中加载文本
    def loadTexts(self):
        dataList = []
        labelList = []
        for line in open(os.path.join(os.path.dirname(__file__), 'Significant.txt'), 'r').readlines():
            dataList.append(line)
            labelList.append('1')
        for line in open(os.path.join(os.path.dirname(__file__), 'Insignificant.txt'), 'r').readlines():
            dataList.append(line)
            labelList.append('0')
        dataList = self.jiebaSplit(dataList)
        return dataList, labelList

    # 载入数据集
    def loadData(self, dataPath):
        dataList = []
        labelList = []
        for line in open(dataPath, 'r').readlines():
            lineArray = line.split('||')
            if len(lineArray) == 2:
                labelList.append(lineArray[0])
                dataList.append(lineArray[1])
        print('长度是{0}'.format(len(dataList)))
        return dataList, labelList

    # 随机生成训练样本与测试样本
    def generateSample(self, dataList, labelList, trainPath, testPath):
        # 取30%作为测试集
        RATE = 0.3
        listLen = len(dataList)
        testLen = int(RATE * listLen)
        trainDir = open(trainPath, 'w')
        testDir = open(testPath, 'w')
        indexList = random.sample([i for i in range(listLen)], listLen)

        for item in indexList[:testLen]:
            testDir.write(labelList[item].encode('utf-8') + '||' + dataList[item].encode('utf-8'))
            testDir.flush()
        for item in indexList[testLen:]:
            trainDir.write(labelList[item].encode('utf-8') + '||' + dataList[item].encode('utf-8'))
            trainDir.flush()

    # 结巴分词
    def jiebaSplit(self, data):
        result = []
        # 首先利用结巴分词
        for content in data:
            c = []
            for word in jieba.cut(content):
                if word in self.stop_words:
                    pass
                else:
                    c.append(word)
            line = ' '.join(c)
            result.append(line)
        return result

    # 训练数据
    def trainNB(self, dataList, labelList):
        # 训练模型首先需要将分好词的文本进行向量化，这里使用的TFIDF进行向量化
        self.clf.fit(self.vec.fit_transform(dataList), labelList)
        self.saveModel()

    # 预测数据
    def predictNB(self, dataList):
        data = self.vec.transform(dataList)
        predictList = self.clf.predict(data)
        return predictList

    # 计算准确率
    def calAccuracy(self, labelList, predictList):
        rightCount = 0
        if len(labelList) == len(predictList):
            for i in range(len(labelList)):
                if labelList[i] == predictList[i]:
                    rightCount += 1
            print ('准确率为：%s' % (rightCount / float(len(labelList))))


# 创建NB分类器
def main():
    nbclassifier = NBclassifier()
    trainPath = u'trainData.txt'
    testPath = u'testData.txt'
    dataList, labelList = nbclassifier.loadTexts()
    nbclassifier.generateSample(dataList, labelList, trainPath, testPath)

    # 载入训练集与测试集
    dataList, labelList = nbclassifier.loadData(trainPath)
    testData, testLabel = nbclassifier.loadData(testPath)
    # # 训练并预测分类正确性
    nbclassifier.trainNB(dataList, labelList)
    predictList = nbclassifier.predictNB(testData)
    nbclassifier.calAccuracy(predictList, testLabel)

# if __name__ == '__main__':
#     # main()
#     nbclassifier = NBclassifier(clf_path='clf.m', vec_path='vec.m')
#     testData = [' '.join(jieba.cut(line)) for line in open('test.txt', 'r').readlines()]
#     print(testData)
#     predictList = nbclassifier.predictNB(testData)
#     sum_ = 0
#     for i in predictList:
#         if i == '1':
#             sum_ += 1
#
#     print(float(sum_) / float(len(predictList)))
