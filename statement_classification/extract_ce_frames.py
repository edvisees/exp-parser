#TODO: Make this modular
# Conceptual and Experimental frame extraction
# Input: Results text (output of nxml2txt) and statement classification output (tsv)
# Output: Conceptual and Experimental frames (json)

import sys
import codecs
import json

conc_types = ["goal", "hypothesis", "fact", "implication"]
exp_types = ["method", "result"]
conc_counter = 0
exp_counter = 0

pmid = sys.argv[3]
main_frame = {"pmid": pmid, "frame-type": "conceptual-experimental-link", "meta-info": {"link-criterion": "passage-id", "statement-classifier-version": "2015-09-10"}, "frames": []}
conc_frame_temp = {"frame-id": "", "frame-type": "conceptual", "goal": [], "hypothesis": [], "fact": [], "implication":[], "ref-exp-frame": None, "passage-text": ""}
exp_frame_temp = {"frame-id": "", "frame-type": "experimental", "method": [], "result": [], "ref-conc-frame": None, "passage-text": ""}


def write_frames(conc_clauses, exp_clauses, pass_text):
  global conc_counter
  global exp_counter

  conc_frame = dict(conc_frame_temp)
  exp_frame = dict(exp_frame_temp)
  empty_conc_frame = True
  empty_exp_frame = True

  conc_id = "%s-conc-%d"%(pmid, conc_counter)
  conc_counter += 1
  conc_frame["frame-id"] = conc_id
  for label in conc_clauses:
    clauses = conc_clauses[label]
    if len(clauses) > 0:
      empty_conc_frame = False
      conc_frame[label] = clauses
  conc_frame["passage-text"] = pass_text
  exp_id = "%s-exp-%d"%(pmid, exp_counter)
  exp_counter += 1
  exp_frame["frame-id"] = exp_id
  for label in exp_clauses:
    clauses = exp_clauses[label]
    if len(clauses) > 0:
      empty_exp_frame = False
      exp_frame[label] = clauses
  exp_frame["passage-text"] = pass_text

  if not empty_exp_frame:
    conc_frame["ref-exp-frame"] = exp_id  
  if not empty_conc_frame:
    exp_frame["ref-conc-frame"] = conc_id

  if not empty_exp_frame:
    main_frame["frames"].append(exp_frame)
  if not empty_conc_frame:
    main_frame["frames"].append(conc_frame)

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
