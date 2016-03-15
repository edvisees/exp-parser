import sys
import codecs
import cPickle
import numpy
import argparse
import theano
import json

from rep_reader import RepReader
from util import read_passages, evaluate, make_folds

from keras.models import Sequential, Graph, model_from_json
from keras.layers.core import TimeDistributedDense, Dropout
from keras.layers.recurrent import LSTM, GRU

#from seya.layers.recurrent import Bidirectional

from attention import TensorAttention
from keras_extensions import HigherOrderTimeDistributedDense

class PassageTagger(object):
  def __init__(self, word_rep_file):
    self.rep_reader = RepReader(word_rep_file)
    self.input_size = self.rep_reader.rep_shape[0]
    self.tagger = None

  def make_data(self, trainfilename, use_attention, maxseqlen=None, maxclauselen=None, label_ind=None, train=False):
    print >>sys.stderr, "Reading data.."
    str_seqs, label_seqs = read_passages(trainfilename, train)
    if not label_ind:
      self.label_ind = {"none": 0}
    else:
      self.label_ind = label_ind
    if not maxseqlen:
      maxseqlen = max([len(label_seq) for label_seq in label_seqs])
    if not maxclauselen:
      if use_attention:
        clauselens = []
        for str_seq in str_seqs:
          clauselens.extend([len(clause.split()) for clause in str_seq])
        maxclauselen = max(clauselens)
    X = []
    Y = []
    Y_inds = []
    for str_seq, label_seq in zip(str_seqs, label_seqs):
      for label in label_seq:
        if label not in self.label_ind:
          self.label_ind[label] = len(self.label_ind)
      if use_attention:
        x = numpy.zeros((maxseqlen, maxclauselen, self.input_size))
      else:
        x = numpy.zeros((maxseqlen, self.input_size))
      y_ind = numpy.zeros(maxseqlen)
      seq_len = len(str_seq)
      # The following conditional is true only when we've already trained, and one of the sequences in the test set is longer than the longest sequence in training.
      if seq_len > maxseqlen:
        str_seq = str_seq[:maxseqlen]
        seq_len = maxseqlen 
      if train:
        for i, (clause, label) in enumerate(zip(str_seq, label_seq)):
          clause_rep = self.rep_reader.get_clause_rep(clause)
          if use_attention:
            if len(clause_rep) > maxclauselen:
              clause_rep = clause_rep[:maxclauselen]
            x[-seq_len+i][-len(clause_rep):] = clause_rep
          else:
            x[-seq_len+i] = numpy.mean(clause_rep, axis=0)
          y_ind[-seq_len+i] = self.label_ind[label]
        X.append(x)
        Y_inds.append(y_ind)
      else:
        for i, clause in enumerate(str_seq):
          clause_rep = self.rep_reader.get_clause_rep(clause)
          if use_attention:
            if len(clause_rep) > maxclauselen:
              clause_rep = clause_rep[:maxclauselen]
            x[-seq_len+i][-len(clause_rep):] = clause_rep
          else:
            x[-seq_len+i] = numpy.mean(clause_rep, axis=0)
        X.append(x)
    for y_ind in Y_inds:
      y = numpy.zeros((maxseqlen, len(self.label_ind)))
      for i, y_ind_i in enumerate(y_ind):
        y[i][y_ind_i] = 1
      Y.append(y) 
    self.rev_label_ind = {i: l for (l, i) in self.label_ind.items()}
    return numpy.asarray(X), numpy.asarray(Y)

  def get_attention_weights(self, X_test):
    if not self.tagger:
      raise RuntimeError, "Tagger not trained yet!"
    inp = self.tagger.get_input()
    att_out = None
    for layer in self.tagger.layers:
      if layer.get_config()['name'].lower() == "tensorattention":
        att_out = layer.get_output()
        break
    if not att_out:
      raise RuntimeError, "No attention layer found!"
    f = theano.function([inp], att_out)
    return f(X_test)

  def predict(self, X, bidirectional, tagger=None):
    if not tagger:
      tagger = self.tagger
    if not tagger:
      raise RuntimeError, "Tagger not trained yet!"
    # Determining actual lengths sans padding
    x_lens = []
    for x in X:
      x_len = 0
      for i, xi in enumerate(x):
        if xi.sum() != 0:
          x_len = len(x) - i
          break
      x_lens.append(x_len)
    if bidirectional:
      pred_probs = tagger.predict({'input':X})['output']
    else:
      pred_probs = tagger.predict(X)
    pred_inds = numpy.argmax(pred_probs, axis=2)
    pred_label_seqs = []
    for pred_ind, x_len in zip(pred_inds, x_lens):
      pred_label_seq = [self.rev_label_ind[pred] for pred in pred_ind][-x_len:]
      pred_label_seqs.append(pred_label_seq)
    return pred_probs, pred_label_seqs, x_lens

  def fit_model(self, X, Y, use_attention, att_context, bidirectional):
    print >>sys.stderr, "Input shape:", X.shape, Y.shape
    num_classes = len(self.label_ind)
    if bidirectional:
      tagger = Graph()
      tagger.add_input(name='input', input_shape=X.shape[1:])
      if use_attention:
        tagger.add_node(TensorAttention(X.shape[1:], context=att_context), name='attention', input='input')
        lstm_input_node = 'attention'
      else:
        lstm_input_node = 'input'
      tagger.add_node(LSTM(X.shape[-1]/2, return_sequences=True), name='forward', input=lstm_input_node)
      tagger.add_node(LSTM(X.shape[-1]/2, return_sequences=True, go_backwards=True), name='backward', input=lstm_input_node)
      tagger.add_node(TimeDistributedDense(num_classes, activation='softmax'), name='softmax', inputs=['forward', 'backward'], merge_mode='concat', concat_axis=-1)
      tagger.add_output(name='output', input='softmax')
      print >>sys.stderr, tagger.summary()
      tagger.compile('adam', {'output':'categorical_crossentropy'})
      tagger.fit({'input':X, 'output':Y})
    else:
      tagger = Sequential()
      word_proj_dim = 50
      if use_attention:
        _, input_len, timesteps, input_dim = X.shape
        tagger.add(HigherOrderTimeDistributedDense(input_dim=input_dim, output_dim=word_proj_dim))
        att_input_shape = (input_len, timesteps, word_proj_dim)
        print >>sys.stderr, "Attention input shape:", att_input_shape
        tagger.add(Dropout(0.5))
        tagger.add(TensorAttention(att_input_shape, context=att_context))
        #tagger.add(Dropout(0.5))
      else:
        _, input_len, input_dim = X.shape
        tagger.add(TimeDistributedDense(input_dim=input_dim, output_dim=word_proj_dim))
      tagger.add(LSTM(input_dim=word_proj_dim, output_dim=word_proj_dim, input_length=input_len, return_sequences=True))
      tagger.add(TimeDistributedDense(num_classes, activation='softmax'))
      print >>sys.stderr, tagger.summary()
      tagger.compile(loss='categorical_crossentropy', optimizer='adam')
      tagger.fit(X, Y, batch_size=10)

    return tagger

  def train(self, X, Y, use_attention, att_context, bidirectional, cv=True, folds=5):
    if cv:
      cv_folds = make_folds(X, Y, folds)
      accuracies = []
      fscores = []
      for fold_num, ((train_fold_X, train_fold_Y), (test_fold_X, test_fold_Y)) in enumerate(cv_folds):
        tagger = self.fit_model(train_fold_X, train_fold_Y, use_attention, att_context, bidirectional)
        pred_probs, pred_label_seqs, x_lens = self.predict(test_fold_X, bidirectional, tagger)
        pred_inds = numpy.argmax(pred_probs, axis=2)
        flattened_preds = []
        flattened_targets = []
        for x_len, pred_ind, test_target in zip(x_lens, pred_inds, test_fold_Y):
          flattened_preds.extend(pred_ind[-x_len:])
          flattened_targets.extend([list(tt).index(1) for tt in test_target[-x_len:]])
        assert len(flattened_preds) == len(flattened_targets)
        accuracy, weighted_fscore, all_fscores = evaluate(flattened_targets, flattened_preds)
        print >>sys.stderr, "Finished fold %d. Accuracy: %f, Weighted F-score: %f"%(fold_num, accuracy, weighted_fscore)
        print >>sys.stderr, "Individual f-scores:"
        for cat in all_fscores:
          print >>sys.stderr, "%s: %f"%(self.rev_label_ind[cat], all_fscores[cat])
        accuracies.append(accuracy)
        fscores.append(weighted_fscore)
      accuracies = numpy.asarray(accuracies)
      fscores = numpy.asarray(fscores)
      print >>sys.stderr, "Accuracies:", accuracies
      print >>sys.stderr, "Average: %0.4f (+/- %0.4f)"%(accuracies.mean(), accuracies.std() * 2)
      print >>sys.stderr, "Fscores:", fscores
      print >>sys.stderr, "Average: %0.4f (+/- %0.4f)"%(fscores.mean(), fscores.std() * 2)
    self.tagger = self.fit_model(X, Y, use_attention, att_context, bidirectional)
    model_ext = "att=%s_cont=%s_bi=%s"%(str(use_attention), att_context, str(bidirectional))
    model_config_file = open("model_%s_config.json"%model_ext, "w")
    model_weights_file_name = "model_%s_weights"%model_ext
    model_label_ind = "model_%s_label_ind.json"%model_ext
    print >>model_config_file, self.tagger.to_json()
    self.tagger.save_weights(model_weights_file_name)
    json.dump(self.label_ind, open(model_label_ind, "w"))
    #model_file = open("model_%s.pkl"%model_ext, "w")
    #cPickle.dump(self.tagger, model_file)

if __name__ == "__main__":
  argparser = argparse.ArgumentParser(description="Train, cross-validate and run LSTM discourse tagger")
  argparser.add_argument('repfile', metavar='REP-FILE', type=str, help="Gzipped embedding file")
  argparser.add_argument('infile', metavar='INPUT-FILE', type=str, help="Training or test file. One clause per line and passages separated by blank lines. Train file should have clause<tab>label in each line.")
  argparser.add_argument('--train', help="Train?", action='store_true')
  argparser.add_argument('--test_files', type=str, nargs='+', help="Test file(s)")
  argparser.add_argument('--use_attention', help="Use attention over words? Or else will average their representations", action='store_true')
  argparser.add_argument('--att_context', type=str, help="Context to look at for determining attention (word/clause/para)")
  argparser.set_defaults(att_context='word')
  argparser.add_argument('--bidirectional', help="Bidirectional LSTM", action='store_true')
  args = argparser.parse_args()
  repfile = args.repfile
  infile = args.infile
  train = args.train
  use_attention = args.use_attention
  att_context = args.att_context
  bid = args.bidirectional

  nnt = PassageTagger(repfile)
  if train:
    X, Y = nnt.make_data(infile, use_attention, train=True)
    nnt.train(X, Y, use_attention, att_context, bid, cv=False)
  if args.test_files:
    if train:
      label_ind = nnt.label_ind
    else:
      # Load the model from file
      model_ext = "att=%s_cont=%s_bi=%s"%(str(use_attention), att_context, str(bid))
      model_config_file = open("model_%s_config.json"%model_ext, "r")
      model_weights_file_name = "model_%s_weights"%model_ext
      model_label_ind = "model_%s_label_ind.json"%model_ext
      nnt.tagger = model_from_json(model_config_file.read(), custom_objects={"TensorAttention":TensorAttention, "HigherOrderTimeDistributedDense":HigherOrderTimeDistributedDense})
      print >>sys.stderr, "Loaded model:"
      print >>sys.stderr, nnt.tagger.summary()
      nnt.tagger.load_weights(model_weights_file_name)
      print >>sys.stderr, "Loaded weights"
      label_ind_json = json.load(open(model_label_ind))
      label_ind = {k: int(label_ind_json[k]) for k in label_ind_json}
      print >>sys.stderr, "Loaded label index:", label_ind
    for l in nnt.tagger.layers:
      if l.name == "tensorattention":
        maxseqlen, maxclauselen = l.td1, l.td2
        break
    for test_file in args.test_files:
      print >>sys.stderr, "Predicting on file %s"%(test_file)
      test_out_file_name = test_file.split("/")[-1].replace(".txt", "")+"_att=%s_cont=%s_bid=%s"%(str(use_attention), att_context, str(bid))+".out"
      outfile = open(test_out_file_name, "w")
      X_test, _ = nnt.make_data(test_file, use_attention, maxseqlen=maxseqlen, maxclauselen=maxclauselen, label_ind=label_ind, train=False)
      print >>sys.stderr, "X_test shape:", X_test.shape
      pred_probs, pred_label_seqs, _ = nnt.predict(X_test, bid)
      if use_attention:
        att_weights = nnt.get_attention_weights(X_test.astype('float32'))
        clause_seqs, _ = read_passages(test_file, False)
        paralens = [[len(clause.split()) for clause in seq] for seq in clause_seqs]
        for clauselens, sample_att_weights, pred_label_seq in zip(paralens, att_weights, pred_label_seqs):
          for clauselen, clause_weights, pred_label in zip(clauselens, sample_att_weights[-len(clauselens):], pred_label_seq):
            print >>outfile, pred_label, " ".join(["%.4f"%val for val in clause_weights[-clauselen:]])
          print >>outfile
