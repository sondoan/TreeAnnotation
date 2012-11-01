# Parser for PCFG project
# Written by Son Doan, Dec, 2009
# Run: python Parser_V1.py ../data/dataset1/train/dat1a_train_singledrug ../grammar_V1.cfg

import nltk
import re
import sys
import sys

grammar_file = sys.argv[2]
file_path = 'file:'+grammar_file
grammar = nltk.data.load(file_path)
#grammar = nltk.data.load('file:grammar_V1.cfg')
parser =nltk.parse.ChartParser(grammar, nltk.parse.TD_STRATEGY)

#parser =nltk.RecursiveDescentParser(grammar)
#parser =nltk.ShiftReduceParser(grammar)

# Global variables
Dict = {}
DictMulti = {}

# function to compare between 2 offset e.g., [134,4] [135,0]
# Return 1 - a < b, 0 - a > b
def OffCmp(a,b):
    offset1 = a
    offset2 = b
    if int(offset1[0]) == int(offset2[0]):
        if int(offset1[1]) <= int(offset2[1]):
            return 1
        else:
            return 0
    elif int(offset1[0]) < int(offset2[0]):
        return 1
    elif int(offset1[0]) > int(offset2[0]):
        return 0

# Function for swapping
def SwapItem(a,b):
    temp = a
    a = b
    b = temp

# Sort the list of Array = [('MED',['34','4']), ('DOSE',['34','8']),... ]
def SortList(Arr):
    Num = len(Arr)
    for i in range(0,Num):
        for j in range(i+1,Num):
            if OffCmp(Arr[i][1],Arr[j][1])==0:
                temp = Arr[i]
                Arr[i]=Arr[j]
                Arr[j]=temp

# Array = [('MED',['34','4']), ('DOSE',['34','8']),... ]
# Print MED - DOSE - ...
def PrintCode(Arr):
    code = ''
    for i in range(0,len(Arr)):
        code = code + Arr[i][0] + ' - '  
    if Dict.has_key(code):
        Dict[code]=Dict[code]+1
    else:
        Dict[code]=1
    return code

# Assign code into a finding
def AssignCode(ExtList,ofstList,sem,text):
    if re.match(r'^m=',sem):
        ExtList.append(('MED',ofstList,text))
    elif re.match(r'^do=',sem):
        ExtList.append(('DOSE',ofstList,text))
    elif re.match(r'^mo=',sem):
        ExtList.append(('MODE',ofstList,text))
    elif re.match(r'^f=',sem):
        ExtList.append(('FREQ',ofstList,text))
    elif re.match(r'^du=',sem):
        ExtList.append(('DRT',ofstList,text))
    elif re.match(r'^r=',sem):
        ExtList.append(('REASON',ofstList,text))

# Function deal with each finding
# Input: finding = "m="aspirin" 123:2 123:2||do="" 123 ... 
def FindingOut(finding):
    # For each finding
    #extraction = info[2].split('||')
    extraction = finding.split("||")
    ExtList = []
    for item in extraction[0:6]:
        if re.search(r'"',item):
            str = item.split('"')[1]
            sem = item.split('"')[0]
            if str!='nm':
                ofst = item.split('"')[2]
                ofstList = [ofst.split()[0].split(':')[0],ofst.split()[0].split(':')[1]]
                AssignCode(ExtList,ofstList,sem)
    SortList(ExtList)
    Output = PrintCode(ExtList)
    return Output

# Return unique set
def uniq(alist):
    set = {}
    setL = []
    for item in alist:
        set[(item[1][0],item[1][1],item[2])]=item[0]

    for key in set.iterkeys():
        setL.append((set[key],list(key)))
    return setL

# Assign codes for multiple drugs
def AssignCodeMulti(ExtList):
    CombinedStr= '||'.join(ExtList[0:])
    extraction = CombinedStr.split("||")
    ExtList = []
    for item in extraction[0:]:
        if re.search(r'"',item): 
            str = item.split('"')[1]
            sem = item.split('"')[0]
            if str!='nm' and not re.search(r'narrative|list',item):
                ofst = item.split('"')[2]
                ofstList = [ofst.split()[0].split(':')[0],ofst.split()[0].split(':')[1]]
                AssignCode(ExtList,ofstList,sem,str)
    SExtList = uniq(ExtList)
    SortList(SExtList)
    print SExtList
    # print original order
    str = ''
    for item in SExtList:
        str = str + item[0] + '-'
    return str

def SemTagger(ExtList):
    CombinedStr= '||'.join(ExtList[0:])
    extraction = CombinedStr.split("||")
    ExtList = []
    for item in extraction[0:]:
        if re.search(r'"',item): 
            str = item.split('"')[1]
            sem = item.split('"')[0]
            if str!='nm' and not re.search(r'narrative|list',item):
                ofst = item.split('"')[2]
                ofstList = [ofst.split()[0].split(':')[0],ofst.split()[0].split(':')[1]]
                AssignCode(ExtList,ofstList,sem,str)
    SExtList = uniq(ExtList)
    SortList(SExtList)
    # print original order
    semtag = []
    for item in SExtList:
        semtag.append(('s'+item[0], item[1][2]))
    return semtag

# Parse a semantic sentence
# sent = [(sMED,'aspirin'),(sDOSE,'10 mg'),(sDRT,'for 10 days')]
def ParseSent(sent):
    sent_tag = []
    for item in sent:
        sent_tag.append(item[0])
    return parser.nbest_parse(sent_tag,n=10)

def main():
    # Read text file
    fin = open(sys.argv[1])
    for line in fin.readlines():
        info = line.rstrip().split('\t')
        orig_sent = info[1]
        Lfinding = info[2:]
        origCode = SemTagger(Lfinding)
        #print line
        print orig_sent
        print origCode
        #print "TREE"
        trees = ParseSent(origCode)
        if trees:    
            #tree = trees[0]
            #print tree
            #print(tree.pprint(margin=1500,indent=0,nodesep='',parens='()',quotes=False))
            #print tree.productions()
            tree_count = 0
            for tree in trees:
            #    tree_count = tree_count + 1
                print tree
            #    print(tree.pprint(margin=1500,indent=0,nodesep='',parens='()',quotes=True))
            #    #print tree.productions()
                if tree_count>=20:
                    break

            ##print tree_count
            #if tree_count >=2: 
            #    print orig_sent
            #    print origCode
            #    print "TREE"
            #    for tree in trees:
            #
            #        print tree
            #    print "============"
        else:
            print "Not parsing!"
        print "================="

    fin.close()

########
# MAIN #
########

if __name__=="__main__":
    main()




