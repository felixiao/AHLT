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
# ## -- Extract features for each token in given sentence

def extract_features(tokens) :

   # for each token, generate list of features and add it to the result
   result = []
   for k in range(0,len(tokens)):
      tokenFeatures = []
      t = tokens[k][0]
      tokenFeatures.append("form="+t)
      tokenFeatures.append("formLC="+t.lower())
      # tokenFeatures.append('formLen={len(t)}')
      if len(t)<=3:
         tokenFeatures.append('formLen=Less3')
      elif len(t)<=6:
         tokenFeatures.append('formLen=4to6')
      elif len(t)<=12:
         tokenFeatures.append('formLen=7to12')
      elif len(t)<=20:
         tokenFeatures.append('formLen=12to20')
      else:
         tokenFeatures.append('formLen=More20')
      for i in [3,4,5,6]:
         if len(t)>i:
            tokenFeatures.append(f"prf{i}="+t[:i])
            tokenFeatures.append(f"suf{i}="+t[-i:])
      
      hasUpper = True if re.search('[A-Z]+',t) else False
      hasLower = True if re.search('[a-z]+',t) else False
      hasNumber= True if re.search('[0-9]+',t) else False
      hasSymbol= True if re.search('[-,()/+]+',t)else False
      AllUpper = True if t.isupper() else False
      AllLower = True if t.islower() else False
      AllNumber= True if re.search('^[0-9]+$',t) else False
      isTitle  = True if t[0].isupper() else False

      if AllUpper: tokenFeatures.append("AllUpper")
      if AllLower: tokenFeatures.append("AllLower")
      if AllNumber:tokenFeatures.append("AllNumber")
      if isTitle : tokenFeatures.append("isTitle")
      if hasUpper: tokenFeatures.append('hasUpper')
      if hasLower: tokenFeatures.append('hasLower')
      # if hasNumber:tokenFeatures.append("hasNumber")
      if hasSymbol:tokenFeatures.append("hasSymbol")
      
      # Has both Number and Symbos
      if hasNumber and hasSymbol: tokenFeatures.append('BothNumberAndSymbol')
      # Only Number and All upper
      if hasNumber and not hasLower and not hasSymbol and hasUpper: tokenFeatures.append('OnlyNumberAndUpper')
      # Only Number and All lower
      if hasNumber and hasLower and not hasSymbol and not hasUpper: tokenFeatures.append('OnlyNumberAndLower')
      # Only Symbol and All upper
      if not hasNumber and not hasLower and hasSymbol and hasUpper: tokenFeatures.append('OnlySymbolAndUpper')
      # Only Symbol and All lower
      if not hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append('OnlySymbolAndLower')
      # Only Number, Symbol and All upper
      if hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append('OnlySymbolNumberAndLower')
      # Only Number, Symbol and All lower
      if hasNumber and not hasLower and hasSymbol and hasUpper: tokenFeatures.append('OnlySymbolNumberAndUpper')
      # if re.search('^(',t): tokenFeatures.append('beginWith(')

      if k>0 :
         tPrev = tokens[k-1][0]
         tokenFeatures.append("formPrev="+tPrev)
         tokenFeatures.append("formPrevLC="+tPrev.lower())
         # tokenFeatures.append(f'LenPrev={len(tPrev)}')
         
         if len(tPrev)<=3:
            tokenFeatures.append('PrevLen=Less3')
         elif len(tPrev)<=6:
            tokenFeatures.append('PrevLen=4to6')
         elif len(tPrev)<=12:
            tokenFeatures.append('PrevLen=7to12')
         elif len(tPrev)<=20:
            tokenFeatures.append('PrevLen=12to20')
         else:
            tokenFeatures.append('PrevLen=More20')
         # if len(tPrev)<=3:
         #    tokenFeatures.append('LenPrev=ExShort')
         # elif len(tPrev)<=6:
         #    tokenFeatures.append('LenPrev=Short')
         # elif len(tPrev)<=12:
         #    tokenFeatures.append('LenPrev=Medium')
         # else:
         #    tokenFeatures.append('LenPrev=Long')
         for i in [3,4,5,6]:
            if len(tPrev)>i:
               tokenFeatures.append(f"prf{i}Prev="+tPrev[:i])
               tokenFeatures.append(f"suf{i}Prev="+tPrev[-i:])

         hasUpper = True if re.search('[A-Z]+',tPrev) else False
         hasLower = True if re.search('[a-z]+',tPrev) else False
         hasNumber= True if re.search('[0-9]+',tPrev) else False
         hasSymbol= True if re.search('[-,()/+]+',tPrev)else False
         AllUpper = True if tPrev.isupper() else False
         AllLower = True if tPrev.islower() else False
         AllNumber= True if re.search('^[0-9]+$',tPrev) else False
         isTitle  = True if tPrev[0].isupper() else False

         if AllUpper: tokenFeatures.append("Prev_AllUpper")
         if AllLower: tokenFeatures.append("Prev_AllLower")
         if AllNumber:tokenFeatures.append("Prev_AllNumber")
         if isTitle : tokenFeatures.append("Prev_isTitle")
         if hasUpper: tokenFeatures.append('Prev_hasUpper')
         # if hasLower: tokenFeatures.append('Prev_hasLower')
         if hasNumber:tokenFeatures.append("Prev_hasNumber")
         if hasSymbol:tokenFeatures.append("Prev_hasSymbol")

         # Has both Number and Symbos
         if hasNumber and hasSymbol: tokenFeatures.append('Prev_BothNumberAndSymbol')
         # Only Number and All upper
         if hasNumber and not hasLower and not hasSymbol and hasUpper: tokenFeatures.append('Prev_OnlyNumberAndUpper')
         # Only Number and All lower
         if hasNumber and hasLower and not hasSymbol and not hasUpper: tokenFeatures.append('Prev_OnlyNumberAndLower')
         # Only Symbol and All upper
         if not hasNumber and not hasLower and hasSymbol and hasUpper: tokenFeatures.append('Prev_OnlySymbolAndUpper')
         # Only Symbol and All lower
         if not hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append('Prev_OnlySymbolAndLower')
         # Only Number, Symbol and All upper
         if hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append('Prev_OnlySymbolNumberAndLower')
         # Only Number, Symbol and All lower
         if hasNumber and not hasLower and hasSymbol and hasUpper: tokenFeatures.append('Prev_OnlySymbolNumberAndUpper')

         
         # if re.search('^(',tPrev): tokenFeatures.append('Prev_beginWith(')
      else :
         tokenFeatures.append("BoS")

      if k<len(tokens)-1 :
         tNext = tokens[k+1][0]
         tokenFeatures.append("formNext="+tNext)
         tokenFeatures.append("formNextLC="+tNext.lower())
         # tokenFeatures.append(f'LenNext={len(tNext)}')
         if len(tNext)<=3:
            tokenFeatures.append('NextLen=Less3')
         elif len(tNext)<=6:
            tokenFeatures.append('NextLen=4to6')
         elif len(tNext)<=12:
            tokenFeatures.append('NextLen=7to12')
         elif len(tNext)<=20:
            tokenFeatures.append('NextLen=12to20')
         else:
            tokenFeatures.append('NextLen=More20')

         # if len(tNext)<=3:
         #    tokenFeatures.append('LenNext=ExShort')
         # elif len(tNext)<=6:
         #    tokenFeatures.append('LenNext=Short')
         # elif len(tNext)<=12:
         #    tokenFeatures.append('LenNext=Medium')
         # else:
         #    tokenFeatures.append('LenNext=Long')
         for i in [2,3,4,5,6]:
            if len(tNext)>i:
               tokenFeatures.append(f"prf{i}Next="+tNext[:i])
               tokenFeatures.append(f"suf{i}Next="+tNext[-i:])

         hasUpper = True if re.search('[A-Z]+',tNext) else False
         hasLower = True if re.search('[a-z]+',tNext) else False
         hasNumber= True if re.search('[0-9]+',tNext) else False
         hasSymbol= True if re.search('[-,()/+]+',tNext)else False
         AllUpper = True if tNext.isupper() else False
         AllLower = True if tNext.islower() else False
         AllNumber= True if re.search('^[0-9]+$',tNext) else False
         isTitle  = True if tNext[0].isupper() else False

         if AllUpper: tokenFeatures.append("Next_AllUpper")
         if AllLower: tokenFeatures.append("Next_AllLower")
         if AllNumber:tokenFeatures.append("Next_AllNumber")
         if isTitle : tokenFeatures.append("Next_isTitle")
         if hasUpper: tokenFeatures.append('Next_hasUpper')
         # if hasLower: tokenFeatures.append('Next_hasLower')
         if hasNumber:tokenFeatures.append("Next_hasNumber")
         if hasSymbol:tokenFeatures.append("Next_hasSymbol")

         # Has both Number and Symbos
         if hasNumber and hasSymbol: tokenFeatures.append('Next_BothNumberAndSymbol')
         # Only Number and All upper
         if hasNumber and not hasLower and not hasSymbol and hasUpper: tokenFeatures.append('Next_OnlyNumberAndUpper')
         # Only Number and All lower
         # if hasNumber and hasLower and not hasSymbol and not hasUpper: tokenFeatures.append('Next_OnlyNumberAndLower')
         # Only Symbol and All upper
         if not hasNumber and not hasLower and hasSymbol and hasUpper: tokenFeatures.append('Next_OnlySymbolAndUpper')
         # Only Symbol and All lower
         # if not hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append('Next_OnlySymbolAndLower')
         # Only Number, Symbol and All upper
         # if hasNumber and hasLower and hasSymbol and not hasUpper: tokenFeatures.append('Next_OnlySymbolNumberAndLower')
         # Only Number, Symbol and All lower
         if hasNumber and not hasLower and hasSymbol and hasUpper: tokenFeatures.append('Next_OnlySymbolNumberAndUpper')


         # if re.search('^(',tNext): tokenFeatures.append('Next_beginWith(')
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
