import sys
import codecs
import pickle
import numpy
from random import shuffle

from feature_ablation import get_filter
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn import cross_validation

from preprocess import separate_clauses, tokenize_sentences
from features import FeatureProcessing

class StatementClassifier(object):
  def __init__(self, train=False, cv=True, folds=5, trained_model_name="trained_model.pkl", feat_index_name="feature_index.pkl", stored_tagset="tagset.pkl"):
    self.trained_model_name = trained_model_name
    self.feat_index_name = feat_index_name
    self.stored_tagset = stored_tagset
    self.cv = cv
    self.folds = folds
    self.fp = FeatureProcessing()
    if train:
      print >>sys.stderr, "Statement classifier initialized for training."
      if self.cv:
        print >>sys.stderr, "Cross-validation will be done"
    else:
      self.classifier = pickle.load(open(self.trained_model_name, "rb"))
      feat_index = pickle.load(open(self.feat_index_name, "rb"))
      self.tagset = pickle.load(open(self.stored_tagset, "rb"))
      self.fp.feat_index = feat_index
      print >>sys.stderr, "Stored model loaded. Statement classifier initialized for prediction."

  def predict(self, testfile_name):
    test_data = [x.strip() for x in codecs.open(testfile_name, "r", "utf-8")]
    filter_feature = get_filter()
    if len(test_data) == 0:
      return []
    X = numpy.asarray([self.fp.featurize(clause, filter_feature) for clause in test_data])
    predictions = [self.tagset[ind] for ind in self.classifier.predict(X)]
    return zip(predictions, test_data)

  def train(self, trainfile_name):
    print >>sys.stderr, "Reading data.."
    train_data = [tuple(x.strip().split("\t")) for x in codecs.open(trainfile_name, "r", "utf-8")]
    shuffle(train_data)
    filter_feature = get_filter()
    train_labels, train_clauses = zip(*train_data)
    train_labels = [tl.lower() for tl in train_labels]
    print >>sys.stderr, "Indexing features.."
    self.fp.index_data(train_clauses, filter_feature)
    X = numpy.asarray([self.fp.featurize(clause, filter_feature) for clause in train_clauses])
    tagset = list(set(train_labels))
    tag_index = {l:i for (i, l) in enumerate(tagset)}
    Y = numpy.asarray([[tag_index[label]] for label in train_labels])

    classifier = OneVsRestClassifier(SVC(kernel='linear'))
    if self.cv:
      #num_classes = [0] * len(tagset)
      #for label in train_labels:
      #  num_classes[tag_index[label]] += 1
      #folds = min(num_classes)
      print >>sys.stderr, "Starting Cross-validation for %d folds.."%(self.folds)
      y = [l[0] for l in Y]
      scores = cross_validation.cross_val_score(classifier, X, y, cv=self.folds, scoring='f1_weighted')
      print >>sys.stderr, "Scores:", scores
      print >>sys.stderr, "Average: %0.4f (+/- %0.4f)"%(scores.mean(), scores.std() * 2)

    print >>sys.stderr, "Starting training.."
    classifier.fit(X, Y)
    pickle.dump(classifier, open(self.trained_model_name, "wb"))
    pickle.dump(self.fp.feat_index, open(self.feat_index_name, "wb"))
    pickle.dump(tagset, open(self.stored_tagset, "wb"))

    print >>sys.stderr, "Done"
