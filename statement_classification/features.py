from nltk.tag import StanfordPOSTagger
from nltk.tokenize import word_tokenize
import os
import sys

os.environ['CLASSPATH'] = "/usr1/shared/tools/stanford-postagger-full-2015-04-20"
os.environ['STANFORD_MODELS'] = "/usr1/shared/tools/stanford-postagger-full-2015-04-20/models"

class FeatureProcessing(object):
  def __init__(self):
    self.feat_index = {}
    self.pos_tagger = StanfordPOSTagger('english-bidirectional-distsim.tagger')

  def get_features(self, phrase):
    words = word_tokenize(phrase)
    pos_tags = self.pos_tagger.tag(words)
    features = []
    for word, tag in pos_tags:
      if tag != ',' and tag != '.':
        features.append(tag)
      if tag == 'RB' or tag.startswith('VB'):
        features.append(word.lower())
    return features

  def index_data(self, data):
    all_features = [self.get_features(datum) for datum in data]
    for features in all_features:
      for feat in features:
        if feat not in self.feat_index:
          self.feat_index[feat] = len(self.feat_index)

  def featurize(self, phrase):
    indexed_features = [0] * len(self.feat_index)
    features = self.get_features(phrase)
    for feat in features:
      indexed_features[self.feat_index[feat]] += 1
    return indexed_features
