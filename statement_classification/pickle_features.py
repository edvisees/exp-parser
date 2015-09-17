import sys
import codecs
import pickle
from features import FeatureProcessing

trainfile_name = sys.argv[1]
outfile_name = sys.argv[2]
fp = FeatureProcessing()
train_data = [tuple(x.strip().split("\t")) for x in codecs.open(trainfile_name, "r", "utf-8")]
train_labels, train_clauses = zip(*train_data)
print >>sys.stderr, "Indexing features.."
fp.index_data(train_clauses)
feats = [fp.featurize(clause) for clause in train_clauses]

pickle.dump((feats, train_labels, fp.feat_index), open(outfile_name, "wb"))
