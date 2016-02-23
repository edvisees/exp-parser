import sys
from featrich_passage_tagger import PassageTagger 

ptagger = PassageTagger(do_train=True, algorithm="crf", trained_model_name="crf_passage_trained_model")
str_seqs, feat_seqs, label_seqs = ptagger.read_input(sys.argv[1])
ptagger.train(feat_seqs, label_seqs)
