import theano
import numpy
from theano import tensor as T

class Layer(object):
  def __init__(self, input_size, output_size, numpy_rng, activation):
    weight_range = numpy.sqrt(6. / (input_size + output_size))
    init_weights = numpy_rng.uniform(low = -weight_range, high = weight_range, size = (input_size, output_size))
    self.weights = theano.shared(init_weights)
    self.activation = activation

  def get_output(self, input_vec):
    return self.activation(T.dot(input_vec, self.weights))

class MLP(object):
  def __init__(self, input_size, hidden_sizes, num_classes):
    self.numpy_rng = numpy.random.RandomState(12345)
    self.hidden_layers = []
    self.input = T.vector('input')
    in_size = input_size
    in_vec = self.input
    for out_size in hidden_sizes:
      layer = Layer(in_size, out_size, self.numpy_rng, T.tanh)
      layer_out = layer.get_output(in_vec)
      self.hidden_layers.append(layer)
      in_size = out_size
      in_vec = layer_out
    self.output_layer = Layer(hidden_sizes[-1], num_classes, self.numpy_rng, T.nnet.softmax)
    self.output = self.output_layer.get_output(in_vec)[0]
    self.label = T.iscalar('label')
    self.cost = -T.log(self.output)[self.label]

  def get_output_func(self):
    return theano.function([self.input], self.output)

  def get_train_func(self, learning_rate):
    params = [layer.weights for layer in self.hidden_layers + [self.output_layer]]
    gparams = T.grad(self.cost, params)
    updates = [(param, param - learning_rate * gparam) for param, gparam in zip(params, gparams)]
    train_func = theano.function([self.input, self.label], self.cost, updates=updates)
    return train_func
    
      
    
    
    
