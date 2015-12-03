# Written based on Graham Taylor's implementation: https://github.com/gwtaylor/theano-rnn/blob/master/rnn.py

import theano
import numpy
from theano import tensor as T

class RNN(object):
  def __init__(self, n_in, n_hidden, n_out, activation=T.tanh):
    numpy_rng = numpy.random.RandomState(12345)
    # TODO: Better initialization?
    W_init = numpy.asarray(numpy_rng.uniform(low = -0.01, high=0.01, size=(n_hidden, n_hidden)))
    self.W = theano.shared(value=W_init, name='W')
    W_in_init = numpy.asarray(numpy_rng.uniform(low = -0.01, high=0.01, size=(n_in, n_hidden)))
    self.W_in = theano.shared(value=W_in_init, name='W_in')
    W_out_init = numpy.asarray(numpy_rng.uniform(low = -0.01, high=0.01, size=(n_hidden, n_out)))
    self.W_out = theano.shared(value=W_out_init, name='W_out')
    h0_init = numpy.zeros((n_hidden,))
    self.h0 = theano.shared(value=h0_init, name='h0')
    self.params = [self.W, self.W_in, self.W_out, self.h0]
    
    self.input = T.matrix('input')
    def step(x_t, h_tm1):
      h_t = activation(T.dot(x_t, self.W_in) + T.dot(h_tm1, self.W))
      y_t = T.dot(h_t, self.W_out)
      return h_t, y_t

    [h, y_pred], _ = theano.scan(step, sequences=self.input, outputs_info=[self.h0, None])

    #self.L1 = abs(self.W.sum()) + abs(self.W_in.sum()) + abs(self.W_out.sum())
    #self.L2_sqr = (self.w ** 2).sum() + (self.W_in ** 2).sum() + (self.W_out ** 2).sum()
    self.label = T.iscalar('label')
    self.output = T.nnet.softmax(y_pred[-1])[0]
    self.cost = -T.log(self.output)[self.label]

  def get_output_func(self):
    return theano.function([self.input], self.output)

  def get_train_func(self, learning_rate):
    gparams = T.grad(self.cost, self.params)
    updates = [(param, param - learning_rate * gparam) for param, gparam in zip(self.params, gparams)]
    train_func = theano.function([self.input, self.label], self.cost, updates=updates)
    return train_func
