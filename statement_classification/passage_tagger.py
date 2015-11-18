import sys
import codecs

from features import FeatureProcessing
from pycrfsuite import Tagger, Trainer, ItemSequence

class PassageTagger(object):
  def __init__(self, do_train=False, trained_model_name="passage_crf_model"):
    self.trained_model_name = trained_model_name
    self.fp = FeatureProcessing()
    self.do_train = do_train
    if do_train:
      self.trainer = Trainer()
    else:
      self.tagger = Tagger()

  def read_input(self, filename):
    str_seqs = []
    str_seq = []
    feat_seqs = []
    feat_seq = []
    label_seqs = []
    label_seq = []
    for line in codecs.open(filename, "r", "utf-8"):
      lnstrp = line.strip()
      if lnstrp == "":
        if len(str_seq) != 0:
          str_seqs.append(str_seq)
          str_seq = []
          feat_seqs.append(feat_seq)
          feat_seq = []
          label_seqs.append(label_seq)
          label_seq = []
      else:
        if self.do_train:
          clause, label = lnstrp.split("\t")
          label_seq.append(label)
        else:
          clause = lnstrp
        str_seq.append(clause)
        feats = self.fp.get_features(clause)
        feat_dict = {}
        for f in feats:
          if f in feat_dict:
            feat_dict[f] += 1
          else:
            feat_dict[f] = 1
        #feat_dict = {i: v for i, v in enumerate(feats)}
        feat_seq.append(feat_dict)
    if len(str_seq) != 0:
      str_seqs.append(str_seq)
      str_seq = []
      feat_seqs.append(feat_seq)
      feat_seq = []
      label_seqs.append(label_seq)
      label_seq = []
    return str_seqs, feat_seqs, label_seqs

  def predict(self, feat_seqs):
    print >>sys.stderr, "Tagging %d sequences"%len(feat_seqs)
    self.tagger.open(self.trained_model_name)
    preds = [self.tagger.tag(ItemSequence(feat_seq)) for feat_seq in feat_seqs]
    return preds

  def train(self, feat_seqs, label_seqs):
    print >>sys.stderr, "Training on %d sequences"%len(feat_seqs)
    for feat_seq, label_seq in zip(feat_seqs, label_seqs):
      self.trainer.append(ItemSequence(feat_seq), label_seq)
    self.trainer.train(self.trained_model_name)

