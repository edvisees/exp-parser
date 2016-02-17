import theano
import numpy
from theano import tensor as T

from keras import activations, initializations, regularizers
from keras.layers.core import Layer

class TensorAttention(Layer):
  '''Attention layer that operates on tensors

  '''
  input_ndim = 4
  def __init__(self, input_shape, init='glorot_uniform', activation='tanh', weights=None, **kwargs):
    self.init = initializations.get(init)
    self.activation = activations.get(activation)
    self.proj_regularizer = regularizers.l2(0.01)
    self.score_regularizer = regularizers.l2(0.01)
    self.initial_weights = weights
    kwargs['input_shape'] = input_shape
    super(TensorAttention, self).__init__(**kwargs)

  def build(self):
    proj_dim = self.input_shape[3]/2
    self.local_att_proj = self.init((self.input_shape[3], proj_dim))
    self.local_att_scorer = self.init((proj_dim,))
    self.params = [self.local_att_proj, self.local_att_scorer]
    self.proj_regularizer.set_param(self.local_att_proj)
    self.score_regularizer.set_param(self.local_att_scorer)
    self.regularizers = [self.proj_regularizer, self.score_regularizer]
    if self.initial_weights is not None:
      self.set_weights(self.initial_weights)
      del self.initial_weights

  @property
  def output_shape(self):
    return (self.input_shape[0], self.input_shape[1], self.input_shape[3])

  def get_output(self, train=False):
    input = self.get_input(train)
    proj_input = self.activation(T.tensordot(input, self.local_att_proj, axes=(3,0)))
    att_scores = T.tensordot(proj_input, self.local_att_scorer, axes=(3, 0))
    # Nested scans. For shame!
    def get_sample_att(sample_input, sample_att):
      sample_att_inp, _ = theano.scan(fn=lambda s_att_i, s_input_i: T.dot(s_att_i, s_input_i), sequences=[T.nnet.softmax(sample_att), sample_input])
      return sample_att_inp

    att_input, _ = theano.scan(fn=get_sample_att, sequences=[input, att_scores])
    return att_input
