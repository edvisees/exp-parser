import sys
from passage_tagger import PassageTagger 

ptagger = PassageTagger(do_train=False, algorithm="crf", trained_model_name="crf_trained_model")
str_seqs, feat_seqs, _ = ptagger.read_input(sys.argv[1])
preds = ptagger.predict(feat_seqs)
for pred in preds:
  print "\n".join(pred)
  print
