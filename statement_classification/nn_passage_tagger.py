import sys
import codecs
import cPickle
import numpy

from rep_reader import RepReader
from util import read_passages, evaluate, make_folds

from keras.models import Sequential
from keras.layers.core import TimeDistributedDense, Dropout
from keras.layers.recurrent import LSTM

class PassageTagger(object):
  def __init__(self, word_rep_file):
    self.rep_reader = RepReader(word_rep_file)
    self.input_size = self.rep_reader.rep_shape[0]
    self.tagger = None

  def make_data(self, trainfilename, train=False):
    print >>sys.stderr, "Reading data.."
    str_seqs, label_seqs = read_passages(trainfilename, train)
    self.label_ind = {"none": 0}
    maxseqlen = max([len(label_seq) for label_seq in label_seqs])
    X = []
    Y = []
    Y_inds = []
    for str_seq, label_seq in zip(str_seqs, label_seqs):
      for label in label_seq:
        if label not in self.label_ind:
          self.label_ind[label] = len(self.label_ind)
      x = numpy.zeros((maxseqlen, self.input_size))
      y_ind = numpy.zeros(maxseqlen)
      seq_len = len(str_seq)
      for i, (clause, label) in enumerate(zip(str_seq, label_seq)):
        clause_rep = self.rep_reader.get_clause_rep(clause)
        x[-seq_len+i] = numpy.mean(clause_rep, axis=0)
        y_ind[-seq_len+i] = self.label_ind[label]
      X.append(x)
      Y_inds.append(y_ind)
    for y_ind in Y_inds:
      y = numpy.zeros((maxseqlen, len(self.label_ind)))
      for i, y_ind_i in enumerate(y_ind):
        y[i][y_ind_i] = 1
      Y.append(y) 
    self.rev_label_ind = {i: l for (l, i) in self.label_ind.items()}
    return numpy.asarray(X), numpy.asarray(Y)

  def predict(self, X, tagger=None):
    if not tagger:
      tagger = self.tagger
    if not tagger:
      raise RuntimeError, "Tagger not trained yet!"
    # Determining actual lengths sans padding
    x_lens = []
    for x in X:
      x_len = 0
      for i, xi in enumerate(x):
        if sum(xi) != 0:
          x_len = len(x) - i
          break
      x_lens.append(x_len)
    pred_probs = tagger.predict(X)
    pred_inds = numpy.argmax(pred_probs, axis=2)
    pred_label_seqs = []
    for pred_ind, x_len in zip(pred_inds, x_lens):
      pred_label_seq = [self.rev_label_ind[pred] for pred in pred_ind][-x_len:]
      pred_label_seqs.append(pred_label_seq)
    return pred_inds, pred_label_seqs, x_lens

  def fit_model(self, X, Y):
    num_classes = len(self.label_ind)
    tagger = Sequential()
    tagger.add(LSTM(input_dim=self.input_size, output_dim=self.input_size/2, return_sequences=True, inner_activation='sigmoid'))
    tagger.add(TimeDistributedDense(num_classes, activation='softmax'))
    tagger.compile(loss='categorical_crossentropy', optimizer='adam')
    tagger.fit(X, Y)
    return tagger

  def train(self, X, Y, cv=True, folds=5):
    if cv:
      cv_folds = make_folds(X, Y, folds)
      accuracies = []
      fscores = []
      for fold_num, ((train_fold_X, train_fold_Y), (test_fold_X, test_fold_Y)) in enumerate(cv_folds):
        tagger = self.fit_model(train_fold_X, train_fold_Y)
        pred_inds, pred_label_seqs, x_lens = self.predict(test_fold_X, tagger)
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
    self.tagger = self.fit_model(X, Y)

  """
  def evaluate(self, y, pred):
    accuracy = float(sum([c == p for c, p in zip(y, pred)]))/len(pred)
    num_gold = {}
    num_pred = {}
    num_correct = {}
    for c, p in zip(y, pred):
      if c in num_gold:
        num_gold[c] += 1
      else:
        num_gold[c] = 1
      if p in num_pred:
        num_pred[p] += 1
      else:
        num_pred[p] = 1
      if c == p:
        if c in num_correct:
          num_correct[c] += 1
        else:
          num_correct[c] = 1
    fscores = {}
    for p in num_pred:
      precision = float(num_correct[p]) / num_pred[p] if p in num_correct else 0.0
      recall = float(num_correct[p]) / num_gold[p] if p in num_correct else 0.0
      fscores[p] = 2 * precision * recall / (precision + recall) if precision !=0 and recall !=0 else 0.0
    weighted_fscore = sum([fscores[p] * num_gold[p] if p in num_gold else 0.0 for p in fscores]) / sum(num_gold.values())
    return accuracy, weighted_fscore, fscores
  """

if __name__ == "__main__":
  repfile = sys.argv[1]
  infile = sys.argv[2]
  mode = sys.argv[3]
  train = False
  if mode.lower() == "train":
    train = True
  nnt = PassageTagger(repfile)
  if train:
    X, Y = nnt.make_data(infile, True)
    nnt.train(X, Y)
