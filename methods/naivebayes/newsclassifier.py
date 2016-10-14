from __future__ import division
from multiprocessing import Pool
import copy_reg
import types
import operator
from functools import reduce
import StringIO
import time

# from naiveBayesClassifier.ExceptionNotSeen import NotSeen
import csv
"""
Suppose you have some texts of news and know their categories.
You want to train a system with this pre-categorized/pre-classified 
texts. So, you have better call this data your training set.
"""
import tokenizer
from trainer import Trainer



def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

class Classifier(object):
    """docstring for Classifier"""
    def __init__(self, trainedData):
        super(Classifier, self).__init__()
        self.data = trainedData
        self.defaultProb = 0.000000001
        self.results = []

    def calc_probs(self, className, csv_reader):
        result = {}
        results = []
        probsOfClasses = {}
        className = self.data.getClasses()[className]
        csv_reader = csv.reader(StringIO.StringIO(csv_reader), delimiter=';')
        for row in csv_reader:
            result["row"] = ";".join(row)
            tokensProbs = [self.getTokenProb(t, className) for t in row]
            tokenSetProb = reduce(lambda a,b: a*b, (i for i in tokensProbs if i) )

            probsOfClasses[className] = tokenSetProb * self.getPrior(className)
            result[className] = str(probsOfClasses[className])
            results.append(result)
        return results

    def test(self, x):
        return x*x

    def collect_results(self, result):
        self.results.extend(result)

    def parallel_classify(self, text):
        documentCount = self.data.getDocCount()
        classes = self.data.getClasses()
        with open(text, 'rb') as csvfile:

            pool = Pool()
            for c_n in range(len(classes)):
                pool.apply_async(self.calc_probs, args=(c_n,csvfile.read(),), callback=self.collect_results)
                # pool.apply_async(self.test, args=(c_n,), callback=self.collect_results)
            pool.close()
            pool.join()

    # ali ata bak
    def classify(self, text):

        documentCount = self.data.getDocCount()
        classes = self.data.getClasses()

        # only unique tokens
        # tokens = list(set(self.tokenizer.tokenize(text)))
        tokens = []
        datas = []
        probsOfClasses = {}
        result = ""
        with open(text, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                result += "Data = " + "; ".join(row) + "\n"
                for className in classes:
                    tokensProbs = [self.getTokenProb(t, className) for t in row]
                    try:
                        tokenSetProb = reduce(lambda a,b: a*b, (i for i in tokensProbs if i) )
                    except:
                        tokenSetProb = 0

                    probsOfClasses[className] = tokenSetProb * self.getPrior(className)
                    result += className + ": " + str(probsOfClasses[className]) + "; "
                result += '\n'
        return result

    def getPrior(self, className):
        return self.data.getClassDocCount(className) /  self.data.getDocCount()

    def getTokenProb(self, token, className):
        #p(token|Class_i)
        classDocumentCount = self.data.getClassDocCount(className)

        # if the token is not seen in the training set, so not indexed,
        # then we return None not to include it into calculations.
        tokenFrequency = self.data.getFrequency(token, className)
        #try:
            # tokenFrequency = self.data.getFrequency(token, className)
        #except NotSeen as e:
            #return None

        # this means the token is not seen in this class but others.
        if tokenFrequency is None:
            return self.defaultProb

        probablity =  tokenFrequency / classDocumentCount
        return probablity


if __name__ == '__main__':
    newsTrainer = Trainer(tokenizer)

    # You need to train the system passing each text one by one to the trainer module.
    """newsSet =[
        {'text': 'not to eat too much is not enough to lose weight', 'category': 'health'},
        {'text': 'Russia try to invade Ukraine', 'category': 'politics'},
        {'text': 'do not neglect exercise', 'category': 'health'},
        {'text': 'Syria is the main issue, Obama says', 'category': 'politics'},
        {'text': 'eat to lose weight', 'category': 'health'},
        {'text': 'you should not eat much', 'category': 'health'}
    ]"""


    newsSet = [
        {'name': 'examples/bad_scores.csv', 'category': 'bad'},
        {'name': 'examples/good_scores.csv', 'category': 'good'}
    ]

    for news in newsSet:
        newsTrainer.train(news['name'], news['category'])
        # newsTrainer.train(news['text'], news['category'])


    # When you have sufficient trained data, you are almost done and can start to use
    # a classifier.
    newsClassifier1 = Classifier(newsTrainer.data)
    newsClassifier2 = Classifier(newsTrainer.data)

    # Now you have a classifier which can give a try to classifiy text of news whose
    # category is unknown, yet.
    cur_time = time.time()
    newsClassifier1.parallel_classify("examples/scores_all.csv")
    end_time1 = time.time() - cur_time
    cur_time = time.time()
    newsClassifier2.classify("examples/scores_all.csv")
    end_time2 = time.time() - cur_time

    print "Parallel: ", end_time1
    print "Sequential: ", end_time2

    # classification = newsClassifier1.results
    # the classification variable holds the detected categories sorted
    # print(classification)
    # with open("results.txt", mode="w") as fh:
    #    fh.write(classification)