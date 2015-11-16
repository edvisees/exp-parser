import sys
import codecs
import numpy
from sklearn.svm import SVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn import cross_validation
from nltk.tokenize import word_tokenize

def get_idfs(words, tok_lines):
  idfs = {}
  num_docs = len(tok_lines)
  for word in words:
    num_docs_for_word = 0
    for line in tok_lines:
      if word in line:
        num_docs_for_word += 1
    idfs[word] = numpy.log(float(num_docs)/num_docs_for_word)
  return idfs

def get_tfidf_vec(tok_line, word_index, idfs):
  vec = [0.0] * len(word_index)
  for word in tok_line.split():
    if word in word_index:
      vec[word_index[word]] += idfs[word]
  return vec

trainfile = codecs.open(sys.argv[1], "r", "utf-8")
class_text = {}
data = []
classes = set([])
words = []
for line in trainfile:
  label, text = line.strip().split("\t")
  text = " ".join(word_tokenize(text)).lower()
  words.extend(text.split())
  data.append((label, text))
  classes.add(label)
  if label in class_text:
    class_text[label].append(text)
  else:
    class_text[label] = [text]

classes = list(classes)
print >>sys.stderr, "Number of classes: %d"%(len(classes))
class_index = {label: i for i, label in enumerate(classes)}
words = list(set(words))
print >>sys.stderr, "Vocabulary size: %d"%(len(words))
word_index = {word: i for i, word in enumerate(words)}
tok_lines = [" ".join(class_text[label]) for label in classes]
idfs = get_idfs(words, tok_lines)

X = numpy.asarray([get_tfidf_vec(text, word_index, idfs) for _, text in data])
y_inds = [label for label, _ in data]
classifier = OneVsRestClassifier(SVC(kernel='linear'))
predictions = cross_validation.cross_val_predict(classifier, X, y_inds, cv=5)
scores = cross_validation.cross_val_score(classifier, X, y_inds, cv=5, scoring='f1_weighted')
print >>sys.stderr, "Scores:", scores
print >>sys.stderr, "Average: %0.4f (+/- %0.4f)"%(scores.mean(), scores.std() * 2)
print "\n".join(predictions)
