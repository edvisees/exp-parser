#TODO: Make this modular
# Conceptual and Experimental frame extraction
# Input: Results text (output of nxml2txt) and statement classification output (tsv)
# Output: Conceptual and Experimental frames (json)

import sys
import codecs
import json

conc_types = ["goal", "hypothesis", "fact", "implication", "problem"]
exp_types = ["method", "result"]
counter = 0

pmid = sys.argv[3]
main_frame = {"pmid": pmid, "frame-type": "conceptual-experimental-link", "meta-info": {"link-criterion": "passage-id", "statement-classifier-version": "2015-09-10"}, "frames": []}
passage_frame_temp = {"frame-id": "", "frame-type": "passage", "text":"", "conceptual-frame": None, "experimental-frame": None}
conc_frame_temp = {"subframe-id": "", "frame-type": "conceptual", "goal": [], "hypothesis": [], "fact": [], "implication":[], "problem":[]}
exp_frame_temp = {"subframe-id": "", "frame-type": "experimental", "method": [], "result": []}


def write_frames(conc_clauses, exp_clauses, pass_text):
  global counter

  passage_frame = dict(passage_frame_temp)
  conc_frame = dict(conc_frame_temp)
  exp_frame = dict(exp_frame_temp)
  empty_conc_frame = True
  empty_exp_frame = True
  
  passage_id = "%s-pass-%d"%(pmid, counter)
  passage_frame["text"] = pass_text
  passage_frame["frame-id"] = passage_id

  conc_id = "%s-conc-%d"%(pmid, counter)
  conc_frame["subframe-id"] = conc_id
  for label in conc_clauses:
    clauses = conc_clauses[label]
    if len(clauses) > 0:
      empty_conc_frame = False
      conc_frame[label] = clauses

  exp_id = "%s-exp-%d"%(pmid, counter)
  exp_frame["subframe-id"] = exp_id
  for label in exp_clauses:
    clauses = exp_clauses[label]
    if len(clauses) > 0:
      empty_exp_frame = False
      exp_frame[label] = clauses

  if not empty_exp_frame:
    passage_frame["experimental-frame"] = exp_frame 
  if not empty_conc_frame:
    passage_frame["conceptual-frame"] = conc_frame

  if not empty_exp_frame or not empty_conc_frame:
    main_frame["frames"].append(passage_frame)
    counter += 1

txtfile = codecs.open(sys.argv[1], "r", "utf-8")
sc_resfile = codecs.open(sys.argv[2], "r", "utf-8")
clause_labels = [(x.split("\t")[0], x.strip().split("\t")[1]) for x in sc_resfile]
cl_ind = 0

for tline in txtfile:
  tline_ns = tline.replace(" ", "")
  conc_clauses = {}
  exp_clauses = {}
  while True:
    if cl_ind == len(clause_labels):
      break
    clause, label = clause_labels[cl_ind]
    if clause.replace(" ", "") not in tline_ns:
      break
    if label in conc_types:
      if label in conc_clauses:
        conc_clauses[label].append(clause)
      else:
        conc_clauses[label] = [clause]
    if label in exp_types:
      if label in exp_clauses:
        exp_clauses[label].append(clause)
      else:
        exp_clauses[label] = [clause]
    cl_ind += 1
  write_frames(conc_clauses, exp_clauses, tline.strip())

print json.dumps(main_frame, indent=2, sort_keys=False)
