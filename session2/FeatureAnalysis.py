import csv
from re import T
import sys
from matplotlib.pyplot import title, xlabel, xticks
import numpy as np
import re
import matplotlib.pyplot as plt

feature_file = sys.argv[1]

DrugList = []
DrugNList= []
GroupList= []
BrandList= []
OtherList= []

DrugEXTList = []
DrugNEXTList= []
GroupEXTList= []
BrandEXTList= []


def Analysis(tokens,extractTokens, listName,topK=20):
    # Count of tokens
    print(f'\n{listName}\tCount\t{len(tokens)}')
    # Prefix 3-7
    # Suffix 3-7
    prefix_frequency = {}
    suffix_frequency = {}
    # Top 10 frequent tokens
    if listName !='Other':
        tokens_frequency = {t: tokens.count(t) for t in tokens}
        tokens_frequency_sorted = sorted(tokens_frequency.items(), key=lambda x:x[1], reverse=True)

        extractTokens_freq = {t:extractTokens.count(t) for t in extractTokens}
        extractTokens_freq_sorted = sorted(extractTokens_freq.items(), key=lambda x:x[1], reverse=True)
        # list top k tokens
        FN = []
        FP = []
        for i, t in enumerate(tokens_frequency_sorted):
            if i<topK:
                print(f'{listName}\tFreq [{i}]\t{t}')
            if t[0] not in extractTokens_freq.keys(): #False Negative
                FN.append(t[0])
        for i, t in enumerate(extractTokens_freq_sorted):
            if t[0] not in tokens_frequency.keys(): # False Positive
                FP.append(t[0])
        print(f'{listName}\tFalse Negative\t{len(FN)}')
        for i, t in enumerate(FN):
            print(f'{listName}\tFN [{i}]\t{t}')
        print(f'{listName}\tFalse Positive\t{len(FP)}')
        for i, t in enumerate(FP):
            print(f'{listName}\tFP [{i}]\t{t}')

    # Upper cases count
    count_uppertokens = 0
    count_buppertokens= 0
    count_lowertokens = 0
    count_hasupper    = 0
    count_cameltokens = 0
    count_hassymbols  = 0
    count_hasnumbers  = 0


    # Token length count
    list_longtokens = dict()
    list_length = np.zeros(100)
    for t in tokens:
        list_length[len(t)]+=1

        if len(t)>=30:
            if list_longtokens.get(len(t)) is None:
                list_longtokens[len(t)] = [t]
            else:
                list_longtokens[len(t)].append(t)
        if t.islower(): 
            count_lowertokens+=1
        elif t.isupper():
            count_uppertokens+=1
        elif t[0].isupper():
            count_buppertokens+=1
        elif not t[0].isupper() and re.search('[A-Z]+',t):
            count_cameltokens+=1
        else:
            count_hasupper+=1
        if re.search('[0-9]+',t): count_hasnumbers+=1
        if re.search('[-,()]+',t):count_hassymbols+=1
        if listName !='Other':
            for i in range(3,8):
                if prefix_frequency.get(t[:i]) is None:
                    prefix_frequency[t[:i]]=1
                else:prefix_frequency[t[:i]]+=1
                if suffix_frequency.get(t[-i:]) is None:
                    suffix_frequency[t[-i:]]=1
                else:suffix_frequency[t[-i:]]+=1
    if listName !='Other':
        prefix_frequency_sorted = sorted(prefix_frequency.items(),key=lambda x:x[1],reverse=True)
        suffix_frequency_sorted = sorted(suffix_frequency.items(),key=lambda x:x[1],reverse=True)
        prefix_length = np.zeros([8,2])
        suffix_length = np.zeros([8,2])

        for i, t in enumerate(prefix_frequency_sorted):
            if t[1]>2:
                prefix_length[len(t[0])]+=[1,t[1]]
            if i<=topK:
                print(f'{listName}\tFreqPrfx [{i}]\t{t}')
        for i, t in enumerate(suffix_frequency_sorted):
            if t[1]>2:
                suffix_length[len(t[0])]+=[1,t[1]]
            if i<=topK:
                print(f'{listName}\tFreqSufx [{i}]\t{t}')
        for i, l in enumerate(prefix_length):
            if l[0]>0 and i>2:
                print(f'{listName}\tFreqPrefLen [{i}]\t{l}')
        for i, l in enumerate(suffix_length):
            if l[0]>0 and i>2:
                print(f'{listName}\tFreqSuffLen [{i}]\t{l}')


    for i, l in enumerate(list_length):
        if l>0:
            print(f'{listName}\tFreqLen [{i+1}]\t{l/len(tokens):2.1%}')
            if i>=30:
                print(str(list_longtokens[i]))
    
        
    print(f'{listName}\tAllUpper\t{count_uppertokens/len(tokens):2.1%}')
    print(f'{listName}\tAllLower\t{count_lowertokens/len(tokens):2.1%}')
    print(f'{listName}\tTitle\t{count_buppertokens/len(tokens):2.1%}')
    print(f'{listName}\tCamel\t{count_cameltokens/len(tokens):2.1%}')
    print(f'{listName}\tHasupper\t{count_hasupper/len(tokens):2.1%}')
    print(f'{listName}\tHassymbols\t{count_hassymbols/len(tokens):2.1%}')
    print(f'{listName}\tHasnumbers\t{count_hasnumbers/len(tokens):2.1%}')


    largerthan20 =0
    for i in range(21,len(list_length)):
        largerthan20+=list_length[i]
    list_length[21] = largerthan20
    plt.bar(range(21),list_length[1:22]/len(tokens),tick_label=['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','>20'])
    
    plt.title(listName)
    plt.show()


with open(feature_file+'.feat', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='\t', quotechar=' ')
    for i,row in enumerate(spamreader):
        if len(row)>0:
            # print(f'{i}\t{row[1]}\t{row[4]}')
            if row[4]=='O': OtherList.append(row[1])
            elif row[4]=='B-brand' or row[4]=='I-brand':
                BrandList.append(row[1])
            elif row[4]=='B-group' or row[4]=='I-group':
                GroupList.append(row[1])
            elif row[4]=='B-drug' or row[4]=='I-drug':
                DrugList.append(row[1])
            else:
                DrugNList.append(row[1])
with open(feature_file+'-CRF.out', newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter='|', quotechar=' ')
    for i,row in enumerate(spamreader):
        if len(row)>0:
            # print(f'{i}\t{row[3]}\t{row[2]}')
            if row[3]=='drug':
                if ' ' in row[2]:
                    ds = row[2].split(' ')
                    for d in ds:
                        DrugEXTList.append(d)
                else:
                    DrugEXTList.append(row[2])
            elif row[3]=='group':
                if ' ' in row[2]:
                    ds = row[2].split(' ')
                    for d in ds:
                        GroupEXTList.append(d)
                else:
                    GroupEXTList.append(row[2])
            elif row[3]=='drug_n':
                if ' ' in row[2]:
                    ds = row[2].split(' ')
                    for d in ds:
                        DrugNEXTList.append(d)
                else:
                    DrugNEXTList.append(row[2])
            else:
                if ' ' in row[2]:
                    ds = row[2].split(' ')
                    for d in ds:
                        BrandEXTList.append(d)
                else:
                    BrandEXTList.append(row[2])

Analysis(DrugList,DrugEXTList,'Drug_')
Analysis(DrugNList,DrugNEXTList,'DrugN')
Analysis(BrandList,BrandEXTList,'Brand')
Analysis(GroupList,GroupEXTList,'Group')
Analysis(OtherList,None,'Other')

