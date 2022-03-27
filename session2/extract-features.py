#! /usr/bin/python3

from lib2to3.pgen2 import token
from opcode import hasname
import sys
import re
from os import listdir

from xml.dom.minidom import parse
from nltk.tokenize import word_tokenize


   
## --------- tokenize sentence ----------- 
## -- Tokenize sentence, returning tokens and span offsets

def tokenize(txt):
    offset = 0
    tks = []
    ## word_tokenize splits words, taking into account punctuations, numbers, etc.
    for t in word_tokenize(txt):
        ## keep track of the position where each token should appear, and
        ## store that information with the token
        offset = txt.find(t, offset)
        tks.append((t, offset, offset+len(t)-1))
        offset += len(t)

    ## tks is a list of triples (word,start,end)
    return tks


## --------- get tag ----------- 
##  Find out whether given token is marked as part of an entity in the XML

def get_tag(token, spans) :
   (form,start,end) = token
   for (spanS,spanE,spanT) in spans :
      if start==spanS and end<=spanE : return "B-"+spanT
      elif start>=spanS and end<=spanE : return "I-"+spanT

   return "O"

## --------- Feature extractor ----------- 
## -- Extract features for each token in given sentence
def get_features(t,tokenFeatures,featurePrefx):
   # Word Forms
   tokenFeatures.append(f"{featurePrefx}={t}")
   tokenFeatures.append(f"{featurePrefx}LC={t.lower()}")
   tokenFeatures.append(f'{featurePrefx}Len={len(t)}')
   # Prefixes and Suffixes
   for i in range(2,11):
      if len(t)>i:
         tokenFeatures.append(f"{featurePrefx}prf{i}={t[:i]}")
         tokenFeatures.append(f"{featurePrefx}suf{i}={t[-i:]}")
   # Capitalization
   hasUpper = True if re.search('[A-Z]+',t) else False
   hasLower = True if re.search('[a-z]+',t) else False
   isTitle  = True if len(t)>1 and t[0].isupper() and t[1].islower() else False
   AllUpper = True if t.isupper() else False
   AllLower = True if t.islower() else False
   if AllUpper: tokenFeatures.append(f'{featurePrefx}=AllUpper')
   if AllLower: tokenFeatures.append(f'{featurePrefx}=AllLower')
   if isTitle : tokenFeatures.append(f'{featurePrefx}=Title')
   if hasUpper: tokenFeatures.append(f'{featurePrefx}=hasUpper')
   if hasLower: tokenFeatures.append(f'{featurePrefx}=hasLower')
   if not t[0].isupper() and hasUpper: tokenFeatures.append(f'{featurePrefx}=Camel')
   # Number and symbols
   hasNumber= True if re.search('[0-9]+',t) else False
   allNumber= True if re.search('^[0-9]+$',t) else False
   hasSymbol = False
   for s in ['-','(',')','+']:
      if s in t: 
         tokenFeatures.append(f'{featurePrefx}=has{s}')
         hasSymbol= True
   allSymbol=True if re.search('^[-()+,]+$',t) else False

   if hasNumber:tokenFeatures.append(f'{featurePrefx}=hasNumber')
   if hasSymbol:tokenFeatures.append(f'{featurePrefx}=hasSymbol')
   if allNumber:tokenFeatures.append(f'{featurePrefx}=allNumber')
   if allSymbol:tokenFeatures.append(f'{featurePrefx}=allSymbol')

   # Compound Features: Only Symbol and all Upper
   # Has both Number and Symbos
   if hasNumber and hasSymbol: tokenFeatures.append(f'{featurePrefx}=BothNumberAndSymbol')
   # Only Number and All upper
   if hasNumber and not hasLower and not hasSymbol and hasUpper: tokenFeatures.append(f'{featurePrefx}=OnlyNumberAndUpper')
   # Only Number and All lower
   if hasNumber and hasLower and not hasSymbol and not hasUpper: tokenFeatures.append(f'{featurePrefx}=OnlyNumberAndLower')
   # Only Symbol and All lower
   if not hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append(f'{featurePrefx}=OnlySymbolAndLower')
   # Only Number, Symbol and All lower
   # if hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append(f'{featurePrefx}=OnlySymbolNumberAndLower')

   # if not hasNumber and not hasLower and hasSymbol and hasUpper: tokenFeatures.append(f'{featurePrefx}=OnlySymbolAndUpper')

   # Position Features
   if t[0]=='(':  tokenFeatures.append(f'{featurePrefx}=sw(')
   # if t[-1]==')': tokenFeatures.append(f'{featurePrefx}=ew)')
   if t[0]=='-':  tokenFeatures.append(f'{featurePrefx}=sw-')
   if t[-1]=='-': tokenFeatures.append(f'{featurePrefx}=ew-')
   if t[0]=='+':  tokenFeatures.append(f'{featurePrefx}=sw+')
   # if t[-1]=='+': tokenFeatures.append(f'{featurePrefx}=ew+')
   # if t[0] in range(10):  tokenFeatures.append(f'{featurePrefx}=swNumber')
   # if t[-1] in range(10): tokenFeatures.append(f'{featurePrefx}=ewNumber')

def extract_features(tokens) :
   # for each token, generate list of features and add it to the result
   result = []
   for k in range(0,len(tokens)):
      tokenFeatures = []
      t = tokens[k][0]
      get_features(t,tokenFeatures,'Cur')

      if k>0 :
         tPrev = tokens[k-1][0]
         get_features(tPrev,tokenFeatures,'Prev')
      else :
         tokenFeatures.append("BoS")

      if k<len(tokens)-1 :
         tNext = tokens[k+1][0]
         get_features(tNext,tokenFeatures,'Next')
      else:
         tokenFeatures.append("EoS")

      result.append(tokenFeatures)
    
   return result


## --------- MAIN PROGRAM ----------- 
## --
## -- Usage:  baseline-NER.py target-dir
## --
## -- Extracts Drug NE from all XML files in target-dir, and writes
## -- them in the output format requested by the evalution programs.
## --


# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in listdir(datadir) :
   
   # parse XML file, obtaining a DOM tree
   tree = parse(datadir+"/"+f)
   
   # process each sentence in the file
   sentences = tree.getElementsByTagName("sentence")
   for s in sentences :
      sid = s.attributes["id"].value   # get sentence id
      spans = []
      stext = s.attributes["text"].value   # get sentence text
      entities = s.getElementsByTagName("entity")
      for e in entities :
         # for discontinuous entities, we only get the first span
         # (will not work, but there are few of them)
         (start,end) = e.attributes["charOffset"].value.split(";")[0].split("-")
         typ =  e.attributes["type"].value
         spans.append((int(start),int(end),typ))
         

      # convert the sentence to a list of tokens
      tokens = tokenize(stext)
      # extract sentence features
      features = extract_features(tokens)

      # print features in format expected by crfsuite trainer
      for i in range (0,len(tokens)) :
         # see if the token is part of an entity
         tag = get_tag(tokens[i], spans) 
         print (sid, tokens[i][0], tokens[i][1], tokens[i][2], tag, "\t".join(features[i]), sep='\t')

      # blank line to separate sentences
      print()
