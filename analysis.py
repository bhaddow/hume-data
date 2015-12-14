#!/usr/bin/env python3
from xml.etree.ElementTree import ElementTree, tostring, fromstring
from xml.dom import minidom
import argparse

from ucca.convert import *
from ucca import core, layer0, layer1, convert, util, scenes

import pprint

fileName = "data/raw/mteval_de1.dump"




#  and with the sentence as read
#from the XML, the username who created the UCCA tree and the timestamp
#when the MT evaluation was submitted).
#separator:         ===================
#userid:            new_mteval_de1
#ID:                -1477
#alignment:         34:65#33:65#42:71#44:65#27:79#32:79#35:71#38:71#37:71#36:71#40:82#30:71#41:71#39:79#43:65#31:65#1:66#
#source:            Activities lasting for 10 minutes or more are of more benefit.
#target:            Aktivitäten für 10 Minuten oder mehr sind von mehr profitieren .
#alignment?:        0:0#2:1#3:2#4:3#5:4#6:5#7:6#8:7#9:8#10:9#11:10
#UCCA tree:         b'<root annotationID="0" passageID="1457"><attributes /><layer layerID="0"><attributes /><node ID="0.1" type="Word"><attributes paragraph="1" paragraph_position="1" text="Activities" /></node><node ID="0.2" type="Word"><attributes paragraph="1" paragraph_position="2" text="lasting" /></node><node ID="0.3" type="Word"><attributes paragraph="1" paragraph_position="3" text="for" /></node><node ID="0.4" type="Word"><attributes paragraph="1" paragraph_position="4" text="10" /></node><node ID="0.5" type="Word"><attributes paragraph="1" paragraph_position="5" text="minutes" /></node><node ID="0.6" type="Word"><attributes paragraph="1" paragraph_position="6" text="or" /></node><node ID="0.7" type="Word"><attributes paragraph="1" paragraph_position="7" text="more" /></node><node ID="0.8" type="Word"><attributes paragraph="1" paragraph_position="8" text="are" /></node><node ID="0.9" type="Word"><attributes paragraph="1" paragraph_position="9" text="of" /></node><node ID="0.10" type="Word"><attributes paragraph="1" paragraph_position="10" text="more" /></node><node ID="0.11" type="Word"><attributes paragraph="1" paragraph_position="11" text="benefit" /></node><node ID="0.12" type="Punctuation"><attributes paragraph="1" paragraph_position="12" text="." /></node></layer><layer layerID="1"><attributes /><node ID="1.1" type="FN"><attributes /><edge toID="1.2" type="H"><attributes /></edge><edge toID="1.18" type="U"><attributes /></edge></node><node ID="1.2" type="FN"><attributes /><edge toID="1.3" type="A"><attributes /></edge><edge toID="1.14" type="F"><attributes /></edge><edge toID="1.15" type="R"><attributes /></edge><edge toID="1.16" type="D"><attributes /></edge><edge toID="1.17" type="S"><attributes /></edge></node><node ID="1.3" type="FN"><attributes /><edge toID="1.4" type="P"><attributes /></edge><edge toID="1.5" type="Ti"><attributes /></edge></node><node ID="1.4" type="FN"><attributes /><edge toID="0.1" type="T"><attributes /></edge></node><node ID="1.5" type="FN"><attributes /><edge toID="1.6" type="F"><attributes /></edge><edge toID="1.7" type="R"><attributes /></edge><edge toID="1.8" type="C"><attributes /></edge></node><node ID="1.6" type="FN"><attributes /><edge toID="0.2" type="T"><attributes /></edge></node><node ID="1.7" type="FN"><attributes /><edge toID="0.3" type="T"><attributes /></edge></node><node ID="1.8" type="FN"><attributes /><edge toID="1.9" type="C"><attributes /></edge><edge toID="1.12" type="N"><attributes /></edge><edge toID="1.13" type="C"><attributes /></edge></node><node ID="1.9" type="FN"><attributes /><edge toID="1.10" type="E"><attributes /></edge><edge toID="1.11" type="C"><attributes /></edge></node><node ID="1.10" type="FN"><attributes /><edge toID="0.4" type="T"><attributes /></edge></node><node ID="1.11" type="FN"><attributes /><edge toID="0.5" type="T"><attributes /></edge></node><node ID="1.12" type="FN"><attributes /><edge toID="0.6" type="T"><attributes /></edge></node><node ID="1.13" type="FN"><attributes /><edge toID="0.7" type="T"><attributes /></edge></node><node ID="1.14" type="FN"><attributes /><edge toID="0.8" type="T"><attributes /></edge></node><node ID="1.15" type="FN"><attributes /><edge toID="0.9" type="T"><attributes /></edge></node><node ID="1.16" type="FN"><attributes /><edge toID="0.10" type="T"><attributes /></edge></node><node ID="1.17" type="FN"><attributes /><edge toID="0.11" type="T"><attributes /></edge></node><node ID="1.18" type="PNCT"><attributes /><edge toID="0.12" type="T"><attributes /></edge></node></layer></root>'
#sentence from Xml: Activities lasting for 10 minutes or more are of more benefit .
#UCCA annotator:    omri1
#timestamp MT eval: 2015-11-18 16:56:51.216115

def read_dump(fileName):
    myDump = []

    try:
        dfh = open(fileName)
    except IOError as e:
        print ("I/O error({0}): {1}".format(e.errno, e.strerror))
    else:

        sentId=0
        while True:
            data = {}
            data['seg'] = dfh.readline()
            if data['seg'] == '':
                print  ('End of file, number of sentences: ', sentId)
                break
            m = re.search('^=+$', data['seg'] )
            if m:
                sentId+=1
            else:
                raise Exception('Error sentences and segments not lining up', sendId)
                break
            data['user'] = dfh.readline()[2:-2]#Some weird b at beginning, and '' around field
            data['lang'] = data['user'][-3:-1]
            data['ID'] = dfh.readline()[:-1]

            mtevals = dfh.readline()[2:-2]
            if not mtevals:
                print ('ERROR: no mt evaluations for this sentence')
            mtdict = parse_mteval(mtevals)
            data['mteval'] = mtdict

            data['source'] = dfh.readline()[2:-2]
            data['target'] = dfh.readline()[2:-2]
            data['align'] = dfh.readline()[2:-2]

            xml = dfh.readline()[2:-2]
            elem = fromstring(xml)  
            #passage = from_standard(elem) - old style with node ids = 0.1 etc
            passage,idMap = from_site(elem,True)
            data['annot'] = passage
            data['idmap'] = idMap

            data['sent'] = dfh.readline()[2:-2]
            data['uccauser'] = dfh.readline()[2:-2]
            data['timestamp'] = dfh.readline()[:-1]


            #print ("Sentence id: ", data['ID'])
            myDump.append(data)
        dfh.close()

    return myDump

def parse_mteval(line):
    eval_list = {}
    items = line.split("#")
    for item in items:
        els = item.split(":")
        if len(els) == 2:
            eval_list[int(els[0])] = int(els[1])
    return eval_list

def getTreeStats(sent):
    
    passage = sent['annot']
    print("Passage nodes count: ", len(passage.nodes))
    for ID,node in passage.nodes.items():
        print ("ID", ID, "node", node )

        myList = list(node.iter(method='bfs',duplicates=True))
        for item in myList:
            print ("item", item )
 
      

    for node in passage.nodes:
        print ("ID", node)

def getBasicStats(sent):

    stats={}

    passage = sent['annot']
    mteval  = sent['user']


    tokens = [x.text for x in sorted(passage.layer(layer0.LAYER_ID).all,
                                 key=lambda x: x.position)]

    count = 0
    for x in scenes.extract_possible_scenes(passage):
        scenes.extract_head(x)
        count += 1


    stats['numWords'] = len(tokens)
    #stats['numNodes'] = len(passage.nodes)
    stats['numNodes'] = 0

    idMap = sent['idmap']
    for key in passage.nodes:
        node = passage.nodes[key]
        if node.tag == 'FN': #discount terminals (Word) and punctuation (PNCT)
            stats['numNodes'] += 1
            if node.ID in idMap.keys():
                id = int(idMap[node.ID])
                if  id in mteval:
                    print ("Node", node.ID, "Map", idMap[node.ID], "Eval:", mteval[id])
                else:
                    print ("Missing MT node evaluation")
            else:
                print ("Missing mapping to MT node", node.ID)
    stats['numScenes'] = count
    stats['numGreen'] = 0
    stats['numOrange'] = 0
    stats['numRed'] = 0
    stats['numMTNodes'] = 0
    stats['numLexical'] = 0
    stats['numStructural'] = 0
    stats['numAccept'] = 0
    stats['numBad'] = 0

    for key,val in mteval.items():
#        print ("MTNode:", key)
        stats['numMTNodes'] += 1
#65 means ACCEPTABLE
#66 means BAD
#71 means GREEN
#79 means ORANGE
#82 means RED
        if val == 65:
            stats['numAccept'] += 1
            stats['numStructural'] += 1
        elif val == 66:
            stats['numBad'] += 1
            stats['numStructural'] += 1
        elif val == 71:
            stats['numGreen'] += 1
            stats['numLexical'] += 1
        elif val == 79:
            stats['numOrange'] += 1
            stats['numLexical'] += 1
        elif val == 82:
            stats['numRed'] += 1
            stats['numLexical'] += 1


    return stats



def getNodeStats(sent):

    stats = []
    base = {}
    base['lang'] = sent['lang']
    base['user'] = sent['user']
    base['uccauser'] = sent['uccauser']
    base['sent'] = sent['ID']
    base['timestamp'] = sent['timestamp']


    passage = sent['annot']
    mteval  = sent['mteval']

    idMap = sent['idmap']

    for key in passage.nodes:
        node = passage.nodes[key]
        if node.tag == 'FN': #discount terminals (Word) and punctuation (PNCT
            storeNode = base.copy() #cope base to node for storing
            storeNode["id"] = node.ID
            storeNode["numChildren"] = len(node.children)
            if node.ID in idMap.keys():
                id = int(idMap[node.ID])
                if  id in mteval:
                    print ("Node", node.ID, "Map", idMap[node.ID], "Eval:", mteval[id])
                    storeNode["mteval"] = getCode(mteval[id])
                else:
                    print ("Missing MT node evaluation")
                    storeNode["mteval"] = getCode(0)
            else:
                storeNode["mteval"] = getCode(0)
            stats.append(storeNode)
    return stats



def getCode(val):

#65 means ACCEPTABLE
#66 means BAD
#71 means GREEN
#79 means ORANGE
#82 means RED
    if val == 65:
        return "A"
    elif val == 66:
        return "B"
    elif val == 71:
        return "G"
    elif val == 79:
        return "O"
    elif val == 82:
        return "R"
    elif val == 0:
        return "M" #Missing mapping
    else:
        return "E" #Error wrong code



def printBasicStats(stats, num):

    print ("Number of annotated sentences: ", num)
#    keys = ('numScenes','numWords','numNodes','numMTNodes','numLexical','numStructural','numGreen','numOrange','numRed','numAccept','numBad'):
#    print (",".join(keys))

    values = ()
    for key in keys:
        attach
        print ("Key: ", key, " val:", stats[key])
#    for key, val in stats.items():
#        print ("Key: ", key, " val:", val)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', nargs='+', dest='inFile', help="Input UCCAMT Eval dump files")
    parser.add_argument('-o', '--output', dest='outFile', help="Output file")
    parser.add_argument('-v', '--verbose', dest='verboseSetting', help="Verbose level", default = 1, type=int)
    args = parser.parse_args()

    global verbose
    if (args.verboseSetting > 0):
        verbose = int(args.verboseSetting)
        print ("Parsing input file: ", args.inFile)



    bStats = []
    nStats = []
    tStats = []

    sentsNum = 0
    for inFile in args.inFile:
        myDump = read_dump(inFile)
        sentsNum += len(myDump)
        for sent in myDump:
            #bStats = getBasicStats(sent)
            nStats = nStats + getNodeStats(sent)
            tStats = getTreeStats(sent)


    printBasicStats(myStats, sentsNum)



if __name__ == "__main__":
  main()
