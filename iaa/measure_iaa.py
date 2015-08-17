import sys
import json
import codecs

def get_anns_of_type(anns, type_str):
  anns_subset = []
  for ann in anns:
    if ann["infons"]["type"] == type_str:
      anns_subset.append(ann)
  return anns_subset

#TODO: Modify for variable number of annotators

jobj1 = json.load(codecs.open(sys.argv[1]))
jobj2 = json.load(codecs.open(sys.argv[2]))

anns1 = jobj1["passages"][0]["annotations"]
anns2 = jobj2["passages"][0]["annotations"]

epi_anns1 = get_anns_of_type(anns1, "epistSeg")
epi_anns2 = get_anns_of_type(anns2, "epistSeg")

full_agreements = []
partial_agreements = []

for ann1 in epi_anns1:
  ann1_segtype = ann1["infons"]["value"]
  ann1_start = ann1["locations"][0]["offset"]
  ann1_end = ann1_start + ann1["locations"][0]["length"]
  full_found = False
  partial_found = False
  full_match = None
  partial_match = None
  for ann2 in epi_anns2:
    ann2_segtype = ann2["infons"]["value"]
    ann2_start = ann2["locations"][0]["offset"]
    ann2_end = ann1_start + ann2["locations"][0]["length"]
    if ann1_segtype != ann2_segtype:
      continue
    if (ann1_start, ann1_end) == (ann2_start, ann2_end):
      full_found = True
      full_match = (ann1_segtype, ann1_start, ann1_end)
      break
    elif (ann1_start <= ann2_start and ann1_end >= ann2_start) or (ann2_start <= ann1_start and ann2_start >= ann1_start):
      partial_found = True
      partial_match = (ann1_segtype, ann1_start, ann1_end, ann2_start, ann2_end)
  if full_found:
    full_agreements.append(full_match)
  elif partial_found:
    partial_agreements.append(partial_match)

print "Full agreements: ", len(full_agreements)
print "Partial agreements: ", len(partial_agreements)
#print "Set1 annotations: ", "\n".join([str(ann) for ann in epi_anns1])
#print "Set2 annotations: ", "\n".join([str(ann) for ann in epi_anns2])
print "Set1 annotations: ", len(epi_anns1)
print "Set2 annotations: ", len(epi_anns2)
