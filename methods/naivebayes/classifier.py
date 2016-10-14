from __future__ import division
import operator
from functools import reduce

from ExceptionNotSeen import NotSeen
import csv

class Classifier(object):
    """docstring for Classifier"""
    def __init__(self, trainedData, tokenizer):
        super(Classifier, self).__init__()
        self.data = trainedData
        self.tokenizer = tokenizer
        self.defaultProb = 0.000000001

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
        """
        probsOfClasses = {}
        result = ""
        for j in range(len(tokens)):
            result += str(j) + ' = '
            for className in classes:

                # we are calculating the probablity of seeing each token
                # in the text of this class
                # P(Token_1|Class_i)
                tokensProbs = [self.getTokenProb(t, className) for t in tokens[j]]

                # calculating the probablity of seeing the the set of tokens
                # in the text of this class
                # P(Token_1|Class_i) * P(Token_2|Class_i) * ... * P(Token_n|Class_i)
                try:
                    tokenSetProb = reduce(lambda a,b: a*b, (i for i in tokensProbs if i) )
                except:
                    tokenSetProb = 0

                probsOfClasses[className] = tokenSetProb * self.getPrior(className)
                result += className + "; " + str(probsOfClasses[className]) + "; "
            result += '\n'"""



    def getPrior(self, className):
        return self.data.getClassDocCount(className) /  self.data.getDocCount()

    def getTokenProb(self, token, className):
        #p(token|Class_i)
        classDocumentCount = self.data.getClassDocCount(className)

        # if the token is not seen in the training set, so not indexed,
        # then we return None not to include it into calculations.
        try:
            tokenFrequency = self.data.getFrequency(token, className)
        except NotSeen as e:
            return None

        # this means the token is not seen in this class but others.
        if tokenFrequency is None:
            return self.defaultProb

        probablity =  tokenFrequency / classDocumentCount
        return probablity