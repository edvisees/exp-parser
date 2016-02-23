import sys
import codecs
import pickle
import numpy
from random import shuffle

from features import FeatureProcessing
from pycrfsuite import Tagger, Trainer, ItemSequence
from pystruct.models import ChainCRF
from pystruct.learners import FrankWolfeSSVM

class PassageTagger(object):
  def __init__(self, do_train=False, trained_model_name="passage_crf_model", algorithm="crf"):
    self.trained_model_name = trained_model_name
    self.fp = FeatureProcessing()
    self.do_train = do_train
    self.algorithm = algorithm
    if algorithm == "crf":
      if do_train:
        self.trainer = Trainer()
      else:
        self.tagger = Tagger()
    else:
      if do_train:
        model = ChainCRF()
        self.trainer = FrankWolfeSSVM(model=model)
        self.feat_index = {}
        self.label_index = {}
      else:
        self.tagger = pickle.load(open(self.trained_model_name, "rb"))
        self.feat_index = pickle.load(open("ssvm_feat_index.pkl", "rb"))
        label_index = pickle.load(open("ssvm_label_index.pkl", "rb"))
        self.rev_label_index = {i: x for x, i in label_index.items()}

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
    if self.algorithm == "crf":
      self.tagger.open(self.trained_model_name)
      preds = []
      for feat_seq in feat_seqs:
        pred = self.tagger.tag(ItemSequence(feat_seq))
        marginals = [self.tagger.marginal(p, i) for i, p in enumerate(pred)]
	preds.append(zip(pred, marginals))
      #preds = [self.tagger.tag(ItemSequence(feat_seq)) for feat_seq in feat_seqs]
    else:
      Xs = []
      for fs in feat_seqs:
        X = []
        for feat_dict in fs:
          x = [0] * len(self.feat_index)
          for f in feat_dict:
            if f in self.feat_index:
              x[self.feat_index[f]] = feat_dict[f]
          X.append(x)
        Xs.append(numpy.asarray(X))
      pred_ind_seqs = self.tagger.predict(Xs)
      preds = []
      for ps in pred_ind_seqs:
        pred = []
        for pred_ind in ps:
          pred.append(self.rev_label_index[pred_ind])
        preds.append(pred)
    return preds

  def train(self, feat_seqs, label_seqs, cv=True):
    print >>sys.stderr, "Training on %d sequences"%len(feat_seqs)
    if self.algorithm == "crf":
      feat_label_zip = zip(feat_seqs, label_seqs)
      shuffle(feat_label_zip)
      for i, (feat_seq, label_seq) in enumerate(feat_label_zip):
        self.trainer.append(ItemSequence(feat_seq), label_seq, group=i%5)
      if cv:
        for hl in range(5):
          self.trainer.train('', holdout=hl)
      self.trainer.train(self.trained_model_name)
    else:
      for fs in feat_seqs:
        for feat_dict in fs:
          for f in feat_dict:
            if f not in self.feat_index:
              self.feat_index[f] = len(self.feat_index)
      Xs = []
      for fs in feat_seqs:
        X = []
        for feat_dict in fs:
          x = [0] * len(self.feat_index)
          for f in feat_dict:
            x[self.feat_index[f]] = feat_dict[f]
          X.append(x)
        Xs.append(numpy.asarray(X))

      for ls in label_seqs:
        for label in ls:
          if label not in self.label_index:
            self.label_index[label] = len(self.label_index)

      Ys = []
      for ls in label_seqs:
        Y = []
        for label in ls:
          Y.append(self.label_index[label])
        Ys.append(numpy.asarray(Y))

      self.trainer.fit(Xs, Ys)
      pickle.dump(self.trainer, open(self.trained_model_name, "wb"))
      pickle.dump(self.feat_index, open("ssvm_feat_index.pkl", "wb"))
      pickle.dump(self.label_index, open("ssvm_label_index.pkl", "wb"))

