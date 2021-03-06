from trainedData import TrainedData
import csv
class Trainer(object):
    
    """docstring for Trainer"""
    def __init__(self, tokenizer):
        super(Trainer, self).__init__()
        self.tokenizer = tokenizer
        self.data = TrainedData()

    def train(self, text, className):
        """
        enhances trained data using the given text and class
        """
        
        #tokens = self.tokenizer.tokenize(text)
        with open(text, 'rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for row in reader:
                for cell in row:
                    if cell == "class":
                        className = row[1]
                        self.data.increaseClass(className)
                        break
                    self.data.increaseToken(cell, className)

        #for token in tokens:
            #self.data.increaseToken(token, className)