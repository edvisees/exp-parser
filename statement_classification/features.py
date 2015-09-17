from nltk.tag import StanfordPOSTagger
from nltk.tokenize import word_tokenize
import re
import os
import sys

os.environ['CLASSPATH'] = "/usr1/shared/tools/stanford-postagger-full-2015-04-20"
os.environ['STANFORD_MODELS'] = "/usr1/shared/tools/stanford-postagger-full-2015-04-20/models"

class FeatureProcessing(object):
  def __init__(self):
    self.feat_index = {}
    self.implication_words = ["demonstrate", "suggest", "indicate"]
    self.hyp_words = ["possible"]
    self.method_words = ["probe", "detect"]
    self.pos_tagger = StanfordPOSTagger('english-bidirectional-distsim.tagger')

  def get_features(self, phrase):
    words = word_tokenize(phrase)
    pos_tags = self.pos_tagger.tag(words)
    features = []
    for word, tag in pos_tags:
      wl = word.lower()
      if tag != ',' and tag != '.':
        features.append(tag)
      if tag == 'RB' or tag.startswith('VB'):
        features.append(wl)
      if word.startswith("Fig"):
        features.append("figure")
    if re.search("[A-Z][^\s]+ et al.", phrase) is not None:
      features.append("reference")
    if re.search("[Dd]ata not shown", phrase) is not None:
      features.append("data_not_shown")
    for word in self.implication_words:
      if word in phrase:
        features.append("implication_word")
    for word in self.hyp_words:
      if word in phrase:
        features.append("hyp_word")
    for word in self.method_words:
      if word in phrase:
        features.append("method_word")
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
      if feat not in self.feat_index:
        continue
      indexed_features[self.feat_index[feat]] += 1
    return indexed_features
