__author__ = 'stark'

# Back-Propagation Neural Networks
#
import math
import random
import csv
import types
from multiprocessing import Pool
import copy_reg
import time

random.seed(0)

def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copy_reg.pickle(types.MethodType, _pickle_method)

# calculate a random number where:  a <= rand < b
def rand(a, b):
    return (b-a)*random.random() + a

# Make a matrix (we could use NumPy to speed this up)
def makeMatrix(I, J, fill=0.0):
    m = []
    for i in range(I):
        m.append([fill]*J)
    return m

# our sigmoid function, tanh is a little nicer than the standard 1/(1+e^-x)
def sigmoid(x):
    return math.tanh(x)

# derivative of our sigmoid function, in terms of the output (i.e. y)
def dsigmoid(y):
    return 1.0 - y**2

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts]
             for i in range(wanted_parts) ]

class NN:
    def __init__(self, ni, nh, no):
        # number of input, hidden, and output nodes
        self.ni = ni + 1 # +1 for bias node
        self.nh = nh
        self.no = no

        # activations for nodes
        self.ai = [1.0]*self.ni
        self.ah = [1.0]*self.nh
        self.ao = [1.0]*self.no

        # create weights
        self.wi = makeMatrix(self.ni, self.nh)
        self.wo = makeMatrix(self.nh, self.no)
        # set them to random vaules
        for i in range(self.ni):
            for j in range(self.nh):
                self.wi[i][j] = rand(-0.2, 0.2)
        for j in range(self.nh):
            for k in range(self.no):
                self.wo[j][k] = rand(-2.0, 2.0)

        # last change in weights for momentum
        self.ci = makeMatrix(self.ni, self.nh)
        self.co = makeMatrix(self.nh, self.no)

    def update(self, inputs):
        if len(inputs) != self.ni-1:
            raise ValueError('wrong number of inputs')

        # input activations
        for i in range(self.ni-1):
            #self.ai[i] = sigmoid(inputs[i])
            self.ai[i] = inputs[i]

        # hidden activations
        for j in range(self.nh):
            sum = 0.0
            for i in range(self.ni):
                sum = sum + self.ai[i] * self.wi[i][j]
            self.ah[j] = sigmoid(sum)

        # output activations
        for k in range(self.no):
            sum = 0.0
            for j in range(self.nh):
                sum = sum + self.ah[j] * self.wo[j][k]
            self.ao[k] = sigmoid(sum)

        return self.ao[:]


    def backPropagate(self, targets, N, M):
        if len(targets) != self.no:
            raise ValueError('wrong number of target values')

        # calculate error terms for output
        output_deltas = [0.0] * self.no
        for k in range(self.no):
            error = targets[k]-self.ao[k]
            output_deltas[k] = dsigmoid(self.ao[k]) * error

        # calculate error terms for hidden
        hidden_deltas = [0.0] * self.nh
        for j in range(self.nh):
            error = 0.0
            for k in range(self.no):
                error = error + output_deltas[k]*self.wo[j][k]
            hidden_deltas[j] = dsigmoid(self.ah[j]) * error

        # update output weights
        for j in range(self.nh):
            for k in range(self.no):
                change = output_deltas[k]*self.ah[j]
                self.wo[j][k] = self.wo[j][k] + N*change + M*self.co[j][k]
                self.co[j][k] = change
                #print N*change, M*self.co[j][k]

        # update input weights
        for i in range(self.ni):
            for j in range(self.nh):
                change = hidden_deltas[j]*self.ai[i]
                self.wi[i][j] = self.wi[i][j] + N*change + M*self.ci[i][j]
                self.ci[i][j] = change

        # calculate error
        error = 0.0
        for k in range(len(targets)):
            error = error + 0.5*(targets[k]-self.ao[k])**2
        return error


    def test(self, patterns):
        for p in patterns:
            print(p[0], '->', self.update(p[0]))

    def weights(self):
        print('Input weights:')
        for i in range(self.ni):
            print(self.wi[i])
        print()
        print('Output weights:')
        for j in range(self.nh):
            print(self.wo[j])

    def train(self, patterns, iterations=1000, N=0.5, M=0.1):
        # N: learning rate
        # M: momentum factor
        for i in range(iterations):
            error = 0.0
            for p in patterns:
                inputs = p[0]
                targets = p[1]
                self.update(inputs)
                error = error + self.backPropagate(targets, N, M)
            if i % 100 == 0:
                print('error %-.5f' % error)

    def one_train(self, patterns, N=0.5, M=0.1):
        error = 0.0
        for p in patterns:
            inputs = p[0]
            targets = p[1]
            self.update(inputs)
            error = error + self.backPropagate(targets, N, M)
        return error

class Parallel_NN:
    def __init__(self, ni, nh, no):
        self.pool_number = no
        self.process_nn = []
        for i in range(no):
            self.process_nn.append(NN(ni, nh, no))
        self.head_nn = NN(ni, nh, no)
        self.errors = [0, 0, 0]

    def process(self, patterns, pool_number, N, M):
        return [pool_number, self.process_nn[pool_number].one_train(patterns, N, M)]


    def _syncronyze(self, win_number):
        elements = [self.head_nn] + self.process_nn
        for elem in elements:
            elem.ah = self.process_nn[int(win_number)].ah
            elem.ai = self.process_nn[int(win_number)].ai
            elem.ao = self.process_nn[int(win_number)].ao

            elem.ci = self.process_nn[int(win_number)].ci
            elem.co = self.process_nn[int(win_number)].co

            elem.wi = self.process_nn[int(win_number)].wi
            elem.wo = self.process_nn[int(win_number)].wo


    def resultCollector(self, result):
        self.errors[result[0]] = result[1]

    def train(self, patterns, iterations=1000, N=0.5, M=0.1):
        # N: learning rate
        # M: momentum factor
        for i in range(iterations):
            patterns_split = split_list(patterns, 20)
            pool = Pool()
            for i in range(0, len(patterns_split)):
                pool.apply_async(self.process, args=(patterns_split[i], i, N, M, ), callback=self.resultCollector)
            pool.close()
            pool.join()
            # time.sleep(0.01)
            self._syncronyze(self.errors.index(min(self.errors)))
        final_error = self.head_nn.one_train(patterns, N, M)
        return final_error


    def test(self, patterns):
        for p in patterns:
            print(p[0], '->', self.head_nn.update(p[0]))

    def weights(self):
        print('Input weights:')
        for i in range(self.head_nn.ni):
            print(self.head_nn.wi[i])
        print()
        print('Output weights:')
        for j in range(self.head_nn.nh):
            print(self.head_nn.wo[j])


# Teach network XOR function
def normalize(number_list):
    old_min = min(number_list)
    old_max = max(number_list)
    output = [(x-old_min)/(old_max-old_min) for x in number_list]
    return output

def bitfield(n):
    if n == 1:
        return [0, 0, 1]
    if n == 2:
        return [0, 1, 0]
    if n == 4:
        return [1, 0, 0]
    # return [int(digit) for digit in bin(n)[2:]]


def demo():


    # Training sets
    # training_one    = [ Instance( [0.1,0], [0, 1, 1] ), Instance( [0.5,1], [1, 1, 0] ), Instance( [1,0.6], [1, 0, 1] ), Instance( [1,1], [0, 1, 1] ) ]
    input_length = 0

    pat = []

    training_one = []
    with open("Data10.csv", mode="r") as fh:
        temp_data = []
        readed_data = csv.reader(fh, delimiter=',')
        i = 0
        for row in readed_data:
            input_length = len(row) - 2
            name = row[0]
            for j in range(1, len(row) - 1):
                temp_data.append(float(row[j]))

            temp_data = normalize(temp_data)
            target = bitfield(int(row[len(row) - 1]))
            temp_instance = []
            temp_instance.append(temp_data)
            temp_instance.append(target)
            temp_data = []
            pat.append(temp_instance)
            i += 1
            if i == 90:
                break


    now = time.time()
    # create a network with two input, two hidden, and one output nodes
    n = NN(26, 50, 3)
    # train it with some patterns
    n.train(pat, iterations=100)
    # test it
    #n.test(pat)
    print "Sequential version is done. Time: ", (time.time() - now)


    now = time.time()
    # parallel version
    n = Parallel_NN(26, 50, 3)
    # train it with some patterns
    error = n.train(pat, iterations=100)
    # print "Parallel version error: " + str(error)
    # test it
    #n.test(pat)
    print "Parallel version is done. Time: ", (time.time() - now)

if __name__ == '__main__':
    demo()