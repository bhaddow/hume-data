#!/usr/bin/env python3
import logging
from xml.etree.ElementTree import ElementTree, tostring, fromstring
from xml.dom import minidom
import argparse

from ucca.convert import *
from ucca import core, layer0, layer1, convert, util, scenes

import pprint

LOG = logging.getLogger(__name__)

fileName = "data/raw/mteval_de1.dump"


def read_dump(fileName):
    myDump = []

    try:
        dfh = open(fileName)
    except IOError as e:
        LOG.error("I/O error({0}): {1}".format(e.errno, e.strerror))
    else:

        sentId=0
        while True:
            data = {}
            data['seg'] = dfh.readline()
            if data['seg'] == '':
                LOG.info('End of file, number of sentences: %d' %  sentId)
                break
            m = re.search('^=+$', data['seg'] )
            if m:
                sentId+=1
            else:
                raise Exception('Error sentences and segments not lining up', sendId)
                break
            annot = dfh.readline()[2:-2]#Some weird b at beginning, and '' around field
            data['filename'] = annot
            data['lang'] = annot[-3:-1]
            data['user'] = annot[-3:]
            data['ID'] = dfh.readline()[:-1]

            mtevals = dfh.readline()[2:-2]
            if not mtevals:
                LOG.warn('ERROR: no mt evaluations for this sentence')
            mtdict = parse_mteval(mtevals)
            data['mteval'] = mtdict

            data['source'] = dfh.readline()[2:-2]
            data['target'] = dfh.readline()[2:-2]
            data['align'] = dfh.readline()[2:-2]

            xml = dfh.readline() #[2:-2]
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
    LOG.info("Passage nodes count: %d" %  len(passage.nodes))
    for ID,node in passage.nodes.items():
        #LOG.debug("ID", ID, "node", node )

        myList = list(node.iter(method='bfs',duplicates=True))
        #for item in myList:
        #    print ("item", item )
 
      

    #for node in passage.nodes:
    #    print ("ID", node)

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
                #if  id in mteval:
                #    print ("Node", node.ID, "Map", idMap[node.ID], "Eval:", mteval[id])
                #else:
                #    print ("Missing MT node evaluation")
            #else:
            #    print ("Missing mapping to MT node", node.ID)
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
    base['filename'] = sent['filename']


    passage = sent['annot']
    mteval  = sent['mteval']

    idMap = sent['idmap']

    for key in passage.nodes:
        node = passage.nodes[key]
        if node.tag == 'FN': #discount terminals (Word) and punctuation (PNCT
            storeNode = base.copy() #cope base to node for storing
            storeNode["id"] = node.ID
            #storeNode["parents"] = " ".join([parent.ID for parent in node.parents])
            fparent = node.fparent
            if fparent:
                storeNode["parent"] = fparent.ID
            else:
                storeNode["parent"] = "0"
            storeNode["numChildren"] = len(node.children)
            storeNode["uccalabel"] = node.ftag
            storeNode["children"] = " ".join([child.ID for child in node.children])
            if node.ID in idMap.keys():
                id = int(idMap[node.ID])
                if  id in mteval:
                    #print ("Node", node.ID, "Map", idMap[node.ID], "Eval:", mteval[id])
                    storeNode["mteval"] = getCode(mteval[id])
                else:
                    #print ("Missing MT node evaluation")
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



def main():
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--inputFile', nargs='+', dest='inFile', help="Input UCCAMT Eval dump files")
    parser.add_argument('-o', '--output', dest='outFile', help="Output file")
    args = parser.parse_args()



    bStats = []
    nStats = []
    tStats = []

    sentsNum = 0
    ofh = None
    keys = ("id", "sent", "user", "lang", "filename", "mteval", "numChildren", "children", "parent", "uccalabel", "uccauser", "timestamp")
    if args.outFile:
      ofh = open(args.outFile, "w")
      print(",".join(keys), file=ofh)
    for inFile in args.inFile:
        LOG.info("Parsing input file: " + inFile)
        myDump = read_dump(inFile)
        sentsNum += len(myDump)
        for sent in myDump:
            #bStats = getBasicStats(sent)
            sentStats = getNodeStats(sent)
            nStats += sentStats
            if ofh:
              for node in sentStats:
                print (",".join([str(node[k]) for k in keys]), file=ofh)
            tStats = getTreeStats(sent)





if __name__ == "__main__":
  main()
