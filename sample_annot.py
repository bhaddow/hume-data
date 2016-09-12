#!/usr/bin/env python3
from xml.etree.ElementTree import ElementTree, tostring, fromstring
from xml.dom import minidom
import pprint

from ucca.convert import *

def main():
  dfh = open("data/raw/mteval_de1.dump")
  sep = dfh.readline()
  user = dfh.readline()[:-1]
  ID = dfh.readline()[:-1]
  dfh.readline() # blank line
  source = dfh.readline()[:-1]
  target = dfh.readline()[:-1]
  align = dfh.readline()[:-1]
  annot = dfh.readline()[2:-2]
  
  pprint.pprint (annot)
  elem = fromstring(annot)
  #xmlstr = minidom.parseString(ET.tostring(elem)).toprettyxml(indent="   ")
  #print(xmlstr)
  passage = from_standard(elem)
  print("Passage nodes count: ", len(passage.nodes))



if __name__ == "__main__":
  main()
