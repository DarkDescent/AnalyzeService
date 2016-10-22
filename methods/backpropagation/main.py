# -*- coding: utf-8 -*-
from activation_functions import sigmoid_function, tanh_function, linear_function,\
                                 LReLU_function, ReLU_function, elliot_function, symmetric_elliot_function, softmax_function
from cost_functions import sum_squared_error, cross_entropy_cost, exponential_cost, hellinger_distance, softmax_cross_entropy_cost
from learning_algorithms import backpropagation, scaled_conjugate_gradient, scipyoptimize, resilient_backpropagation
from neuralnet import NeuralNet
from tools import Instance
import csv

def bitfield(n):
    if n == 1:
        return [0, 0, 1]
    if n == 2:
        return [0, 1, 0]
    if n == 4:
        return [1, 0, 0]
    # return [int(digit) for digit in bin(n)[2:]]


def normalize(number_list):
    old_min = min(number_list)
    old_max = max(number_list)
    output = [(x-old_min)/(old_max-old_min) for x in number_list]
    return output

# Training sets
# training_one    = [ Instance( [0.1,0], [0, 1, 1] ), Instance( [0.5,1], [1, 1, 0] ), Instance( [1,0.6], [1, 0, 1] ), Instance( [1,1], [0, 1, 1] ) ]
def main(file_path):
    input_length = 0

    training_one = []
    with open(file_path, mode="r") as fh:
        temp_data = []
        readed_data = csv.reader(fh, delimiter=',')
        for row in readed_data:
            input_length = len(row) - 2
            name = row[0]
            for j in range(1, len(row) - 1):
                temp_data.append(float(row[j]))

            temp_data = normalize(temp_data)
            target = bitfield(int(row[len(row) - 1]))
            temp_instance = Instance(temp_data, target, name)
            temp_data = []
            training_one.append(temp_instance)

    settings = {
        # Required settings
        "cost_function"         : sum_squared_error,
        "n_inputs"              : input_length,       # Number of network input signals
        "layers"                : [ (26, sigmoid_function), (15, sigmoid_function), (10, sigmoid_function), (3, sigmoid_function) ],
                                            # [ (number_of_neurons, activation_function) ]
                                            # The last pair in you list describes the number of output signals

        # Optional settings
        "weights_low"           : -1,     # Lower bound on initial weight range
        "weights_high"          : 0,      # Upper bound on initial weight range
        "save_trained_network"  : False,    # Whether to write the trained weights to disk

        "input_layer_dropout"   : 0.0,      # dropout fraction of the input layer
        "hidden_layer_dropout"  : 0.0,      # dropout fraction in all hidden layers
    }


    # initialize the neural network
    network = NeuralNet( settings )

    # load a stored network configuration
    # network = NeuralNet.load_from_file( "trained_configuration.pkl" )

    # Train the network using backpropagation
    backpropagation(
            network,
            training_one,          # specify the training set
            ERROR_LIMIT     = 1e-3, # define an acceptable error limit
            #max_iterations  = 100, # continues until the error limit is reach if this argument is skipped

            # optional parameters
            learning_rate   = 0.01, # learning rate
            momentum_factor = 0.9, # momentum
            max_iterations=100000
             )
    """
    # Train the network using SciPy
    scipyoptimize(
            network,
            training_one,
            method = "Newton-CG",
            ERROR_LIMIT = 1e-4
        )

    # Train the network using Scaled Conjugate Gradient
    scaled_conjugate_gradient(
            network,
            training_one,
            ERROR_LIMIT = 1e-4
        )

    # Train the network using resilient backpropagation
    resilient_backpropagation(
            network,
            training_one,          # specify the training set
            ERROR_LIMIT     = 1e-3, # define an acceptable error limit
            #max_iterations = (),   # continues until the error limit is reach if this argument is skipped

            # optional parameters
            weight_step_max = 50.,
            weight_step_min = 0.,
            start_step = 0.5,
            learn_max = 1.2,
            learn_min = 0.5
        )

    """
    # есть метод save_to_file в neuralnet. надо попробовать его использовать
    return network.print_test( training_one )
