import sys
from featrich_passage_tagger import PassageTagger 

ptagger = PassageTagger(do_train=False, algorithm="crf", trained_model_name="crf_trained_model")
str_seqs, feat_seqs, _ = ptagger.read_input(sys.argv[1])
preds = ptagger.predict(feat_seqs)
for pred in preds:
  if type(pred[0]) is tuple:
    print "\n".join(["%s\t%.4f"%(p[0], p[1]) for p in pred])
  else:
    print "\n".join(pred)
  print
