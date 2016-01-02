import sys
import codecs
import json
from copy import copy

discourse_type = {"fact", "goal", "problem", "hypothesis", "method", "result", "implication"}

def readinput(infile):
    sections = []
    curr_section = []
    curr_para = []
    for line in codecs.open(infile, 'r', 'utf-8'):
        lnstrp = line.strip()
        if lnstrp == "PARA BREAK" or lnstrp == "":
            if len(curr_para) != 0:
                curr_section.append(curr_para)
                curr_para = []
            if lnstrp == "":
                if len(curr_section) != 0:
                    sections.append(curr_section)
                    curr_section = []
                curr_para = []
            continue
        clause, label = lnstrp.split("\t")
        curr_para.append((clause, label))
    return sections

sections = readinput(sys.argv[1])
cosid_frames = []
context_frame = {"frame-type": "context","problems": None, "hypotheses": None, "goals": None, "facts": None, "implications": None}
experiment_frame = {"frame-type":"experiment", "id": None, "local_hypotheses": None, "local_goals": None, "methods": None, "results": None}
interpretation_frame = {"frame-type":"interpretation", "local_implications": None}

def make_exp_frame(clauses):
    curr_exp_frame = dict(experiment_frame)
    for clause, label in clauses:
        if label in ["hypothesis", "goal", "method", "result"]:
            if label == "hypothesis":
                frame_label = "local_hypotheses"
            elif label == "goal":
                frame_label = "local_goals"
            elif label == "method":
                frame_label = "methods"
            else:
                frame_label = "results"
            if curr_exp_frame[frame_label] is None:
                curr_exp_frame[frame_label] = [clause]
            else:
                curr_exp_frame[frame_label].append(clause)
    return curr_exp_frame

def make_context_frame(clauses):
    curr_context_frame = dict(context_frame)
    for clause, label in clauses:
        if label in ["hypothesis", "problem", "fact", "goal", "implication"]:
            if label == "hypothesis":
                frame_label = "hypotheses"
            elif label == "goal":
                frame_label = "goals"
            elif label == "fact":
                frame_label = "facts"
            elif label == "problem":
                frame_label = "problems"
            else:
                frame_label = "implications"
            if curr_context_frame[frame_label] is None:
                curr_context_frame[frame_label] = [clause]
            else:
                curr_context_frame[frame_label].append(clause)
    return curr_context_frame
    
def make_interp_frame(clauses):
    curr_interp_frame = dict(interpretation_frame)
    for clause, label in clauses:
        if label == "implication":
            if curr_interp_frame["local_implications"] is None:
                curr_interp_frame["local_implications"] = [clause]
            else:
                curr_interp_frame["local_implications"].append(clause)
    return curr_interp_frame

for section in sections:
    context_clauses = []
    experiments = []
    for i, para in enumerate(section):
        all_labels = [label for clause, label in para]
        seen_labels = []
        in_exp = False
        exp_clauses = []
        interp_clauses = []
        for j, (clause, label) in enumerate(para):
            if label in ["hypothesis", "fact", "result", "goal", "problem"]:
                if i == 0:
                    if label == "result":
                        if in_exp:
                            exp_clauses.append((clause, label))
                        else:
                            context_clauses.append((clause, label))
                    elif label == "goal":
                        if "method" in all_labels:
                            exp_clauses.append((clause, label))
                        else:
                            context_clauses.append((clause, label))
                    else:
                        context_clauses.append((clause, label))
                else:
                    exp_clauses.append((clause, label))
            elif label == "method":
                in_exp = True
                exp_clauses.append((clause, label))
            elif label == "implication":
                remaining_labels = set([label for _, label in para[j:]])
                if i == len(section) - 1 and "result" not in remaining_labels and "method" not in remaining_labels:
                    context_clauses.append((clause, label))
                else:
                    interp_clauses.append((clause, label))
        if len(exp_clauses) != 0 or len(interp_clauses) != 0:
            experiments.append([make_exp_frame(exp_clauses), make_interp_frame(interp_clauses)])
    curr_context_frame = make_context_frame(context_clauses)
    cosid_frames.append([curr_context_frame, experiments])

"""narr_id = 1
for cf, efs in cosid_frames:
    print "\nNarrative %d\n--------------\nContext of Narrative %d:"%(narr_id, narr_id)
    for k in cf:
        if k == "frame-type":
            continue
        if cf[k]:
            print "\t%s: %s"%(k, " ".join(cf[k]))
    print "\nExperiments in Narrative %d:"%(narr_id)
    expid = 0
    for ef, intf in efs:
        print "\n\tExperiment %d.%d"%(narr_id, expid + 1)
        for k in ef:
            if k == "frame-type":
                continue
            if ef[k]:
                print "\t\t%s: %s"%(k, " ".join(ef[k]))
        print "\n\tInterpretation %d.%d"%(narr_id, expid + 1)
        for k in intf:
            if k == "frame-type":
                continue
            if intf[k]:
                print "\t\t%s: %s"%(k, " ".join(intf[k]))
        expid += 1
    narr_id += 1"""
print json.dumps(cosid_frames, indent=2, sort_keys=True)
                    
