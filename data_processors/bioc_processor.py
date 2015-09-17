import json
import codecs
import re
import sys

class BiocProcessor(object):
  def __init__(self, filename):
    self.filename = filename
  
  def read_annotations(self, ann_type):
    jobj = json.load(codecs.open(self.filename, "r", "utf-8"))
    anns = jobj["passages"][0]["annotations"]
    anns_info = []
    for ann in anns:
      if ann["infons"]["type"] == "epistSeg":
        anns_info.append((ann["infons"]["value"], ann["locations"][0]["offset"], ann["locations"][0]["length"]))
    text = jobj["passages"][0]["text"] 
    ann_strings = []
    for ann_type, offset, length in anns_info:
      ann_strings.append((ann_type, text[offset : offset + length]))
    return ann_strings
    
  def read_text(self):
    jobj = json.load(codecs.open(self.filename, "r", "utf-8"))
    text = jobj["passages"][0]["text"]
    return text

  def write_annotations(self, ann_type, ext_anns, annotated_filename):
    jobj = json.load(codecs.open(self.filename, "r", "utf-8"))
    anns = jobj["passages"][0]["annotations"]
    text = jobj["passages"][0]["text"]
    for label, clause in ext_anns:
      try:
        clauses_in_text = re.findall(clause.replace(" ", "\s*"), text)
        for ct in clauses_in_text:
          text_index = text.index(ct)
          clause_len = len(ct)
          ann_frame = {u'infons': {u'type': ann_type, u'value': label}, u'locations': [{u'length': clause_len, u'offset': text_index}], u'text': ct}
          anns.append(ann_frame)
      except:
        print >>sys.stderr, "Invalid regex formed: %s"%clause.replace(" ", "\s*")
    json.dump(jobj, open(annotated_filename, "w"))
