import sys
from passage_tagger import PassageTagger 

ptagger = PassageTagger(do_train=True)
str_seqs, feat_seqs, label_seqs = ptagger.read_input(sys.argv[1])
ptagger.train(feat_seqs, label_seqs)
