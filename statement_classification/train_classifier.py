import sys
import codecs
import numpy
from random import shuffle

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier

from preprocess import separate_clauses, tokenize_sentences
from features import FeatureProcessing

print >>sys.stderr, "Reading data.."
train_data = [tuple(x.strip().split("\t")) for x in codecs.open(sys.argv[1], "r", "utf-8")]
shuffle(train_data)
valid_prop = 0.2
train_size = int(len(train_data) * (1 - valid_prop))

labels, clauses = zip(*train_data)

train_labels, train_clauses = labels[:train_size], clauses[:train_size]
valid_labels, valid_clauses = labels[train_size:], clauses[train_size:]

fp = FeatureProcessing()
print >>sys.stderr, "Indexing features.."
fp.index_data(clauses)
X = numpy.asarray([fp.featurize(clause) for clause in train_clauses])
X_valid = numpy.asarray([fp.featurize(clause) for clause in valid_clauses])
tagset = list(set(labels))
tag_index = {l:i for (i, l) in enumerate(tagset)}
num_classes = len(tag_index)
Y = numpy.asarray([[tag_index[label]] for label in train_labels])
Y_valid = numpy.asarray([tag_index[label] for label in valid_labels])

classifier = OneVsRestClassifier(SVC(kernel='linear'))
print >>sys.stderr, "Starting training.."
classifier.fit(X, Y)
print >>sys.stderr, "Done"
correct = sum([x == y for x, y in zip(Y_valid, classifier.predict(X_valid))])
acc = float(correct) / len(Y_valid)
print >>sys.stderr, "Validation accuracy: %f"%acc
