import json
import codecs

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
      ann_strings.append((anntype, text[offset : offset + length]))
    return ann_strings
    
  def write_annotations(self):
    raise NotImplementedError
