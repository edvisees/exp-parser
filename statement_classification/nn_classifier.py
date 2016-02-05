import sys
import codecs
import cPickle
import numpy
from random import shuffle

from rep_reader import RepReader
from mlp import MLP
from rnn import RNN
from util import evaluate, make_folds

from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.layers.recurrent import LSTM

class StatementClassifier(object):
  def __init__(self, word_rep_file, train=False, cv=True, folds=5, modeltype="mlp", trained_model_name="trained_model.pkl", tagset_file="tagset.pkl"):
    self.trained_model_name = "%s_%s"%(modeltype, trained_model_name)
    self.cv = cv
    self.folds = folds
    self.rep_reader = RepReader(word_rep_file)
    self.input_size = self.rep_reader.rep_shape[0]
    if modeltype == "mlp":
      self.hidden_sizes = [20, 10]
    else:
      self.hidden_size = 20
    self.max_iter = 100
    self.learning_rate = 0.01
    self.tag_index = None
    self.modeltype = modeltype
    if train:
      print >>sys.stderr, "Statement classifier initialized for training."
      if self.cv:
        print >>sys.stderr, "Cross-validation will be done"
      self.classifier = None
    else:
      self.classifier = cPickle.load(open(self.trained_model_name, "rb"))
      print >>sys.stderr, "Stored model loaded. Statement classifier initialized for prediction."

  def make_data(self, trainfile_name):
    print >>sys.stderr, "Reading data.."
    train_data = [tuple(x.strip().split("\t")) for x in codecs.open(trainfile_name, "r", "utf-8")]
    shuffle(train_data)
    train_clauses, train_labels = zip(*train_data)
    train_labels = [tl.lower() for tl in train_labels]
    tagset = list(set(train_labels))
    if not self.tag_index:
      self.tag_index = {l:i for (i, l) in enumerate(tagset)}
    Y = numpy.asarray([self.tag_index[label] for label in train_labels])
    if self.modeltype=="mlp":
      X = numpy.asarray([numpy.mean(self.rep_reader.get_clause_rep(clause.lower()), axis=0) for clause in train_clauses], dtype='float32')
    elif self.modeltype == "rnn":
      X = numpy.asarray([numpy.asarray(self.rep_reader.get_clause_rep(clause.lower()), dtype='float32') for clause in train_clauses])
    elif self.modeltype == "lstm":
      clause_reps = [self.rep_reader.get_clause_rep(clause.lower()) for clause in train_clauses]
      maxlen = max([len(clause_rep) for clause_rep in clause_reps])
      # Padding X with zeros at the end to make all sequences of same length
      X = numpy.zeros((len(train_clauses), maxlen, max(self.rep_reader.rep_shape)))
      for i in range(len(clause_reps)):
        x_len = len(clause_reps[i])
        X[i][-x_len:] = clause_reps[i]
    return X, Y, len(tagset)
    
  def classify(self, classifier, X):
    if self.modeltype == "mlp" or self.modeltype == "rnn":
      output_func = classifier.get_output_func()
      predictions = [numpy.argmax(output_func(x)) for x in X]
    elif self.modeltype == "lstm":
      predictions = [numpy.argmax(classifier.predict(numpy.asarray([x]))) for x in X]
    return predictions

  def fit_model(self, X, Y, num_classes):
    if self.modeltype == "mlp" or self.modeltype == "rnn":
      if self.modeltype == "mlp":
        classifier = MLP(self.input_size, self.hidden_sizes, num_classes)
      else:
        classifier = RNN(self.input_size, self.hidden_size, num_classes)
      train_func = classifier.get_train_func(self.learning_rate)
      for num_iter in range(self.max_iter):
        for x, y in zip(X, Y):
          train_func(x, y)
    elif self.modeltype == "lstm":
      classifier = Sequential()
      classifier.add(LSTM(input_dim=self.input_size, output_dim=self.input_size/2))
      #classifier.add(Dropout(0.3))
      classifier.add(Dense(num_classes, activation='softmax'))
      classifier.compile(loss='categorical_crossentropy', optimizer='adam')
      Y_indexed = numpy.zeros((len(Y), num_classes))
      for i in range(len(Y)):
        Y_indexed[i][Y[i]] = 1
      classifier.fit(X, Y_indexed, nb_epoch=20)
    return classifier

  def train(self, trainfile_name):
    train_X, train_Y, num_classes = self.make_data(trainfile_name)
    accuracies = []
    fscores = []
    if self.cv:
      cv_folds = make_folds(train_X, train_Y, self.folds)
      for i, ((train_fold_X, train_fold_Y), (test_fold_X, test_fold_Y)) in enumerate(cv_folds):
        classifier = self.fit_model(train_fold_X, train_fold_Y, num_classes)
        predictions = self.classify(classifier, test_fold_X)
        accuracy, weighted_fscore, _ = evaluate(test_fold_Y, predictions)
        print >>sys.stderr, "Finished fold %d. Accuracy: %f, F-score: %f"%(i, accuracy, weighted_fscore)
        accuracies.append(accuracy)
        fscores.append(weighted_fscore)
      accuracies = numpy.asarray(accuracies)
      fscores = numpy.asarray(fscores)
      print >>sys.stderr, "Accuracies:", accuracies
      print >>sys.stderr, "Average: %0.4f (+/- %0.4f)"%(accuracies.mean(), accuracies.std() * 2)
      print >>sys.stderr, "Fscores:", fscores
      print >>sys.stderr, "Average: %0.4f (+/- %0.4f)"%(fscores.mean(), fscores.std() * 2)
    #self.classifier = self.fit_model(train_X, train_Y, num_classes)
    #cPickle.dump(classifier, open(self.trained_model_name, "wb"))
    #pickle.dump(tagset, open(self.stored_tagset, "wb"))
    print >>sys.stderr, "Done"

if len(sys.argv) > 3:
  modeltype = sys.argv[3]
sc = StatementClassifier(sys.argv[2], modeltype=modeltype, train=True)
sc.train(sys.argv[1])




