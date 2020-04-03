# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 20:01:38 2020

@author: JVM
"""
#ISSUE ONLY GETTING FIRST 10,000

import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize

query0 = """
  
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sbol: <http://sbols.org/v2#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX purl: <http://purl.obolibrary.org/obo/>
PREFIX igem: <http://wiki.synbiohub.org/wiki/Terms/igem#>

SELECT
   #(COUNT(?s) as ?count)
   ?s
   ?discontinued
   ?dominant
   ?displayId
   ?title
   ?subpart
   ?role1
   ?role2
   ?descript
   ?notes
   ?source
   ?seq

WHERE {
    FILTER regex(?role1, "identifiers")
    FILTER regex(?role2, "identifiers")
  
    ?s a sbol:ComponentDefinition .    
    ?s sbol:sequence/sbol:elements ?seq .
    <https://synbiohub.org/public/igem/igem_collection/1> sbol:member ?s .
    ?s sbol:component/sbol:definition ?subpart .
 
    ?s sbol:role ?role1 .
    ?subpart sbol:role ?role2 .
  
    OPTIONAL {?s igem:discontinued ?discontinued} .
    OPTIONAL {?s igem:dominant ?dominant} . 
    OPTIONAL {?s sbol:displayId ?displayId} .
    OPTIONAL {?s dcterms:title ?title} .
    OPTIONAL {?s sbh:mutableDescription ?descript} .
    OPTIONAL {?s sbh:mutableNotes ?notes} .
    OPTIONAL {?s sbh:mutableProvenance ?source} .
  }

Limit 10000 Offset replacehere
"""


query1 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sbol: <http://sbols.org/v2#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX purl: <http://purl.obolibrary.org/obo/>
PREFIX igem: <http://wiki.synbiohub.org/wiki/Terms/igem#>

#https://synbiohub.org/public/igem/BBa_K1428000/1 is an interesting case to look at
#can have parts with no subparts but seqAnnotations with defined roles

SELECT
    #(COUNT(?s) as ?count)
    ?s
		?discontinued
		?dominant
    ?displayId
    ?title
  	?role1
		?descript
		?notes
		?source
    ?seq

WHERE {
        FILTER regex(?role1, "identifiers")
        

    ?s a sbol:ComponentDefinition .    
    ?s sbol:sequence/sbol:elements ?seq .
    <https://synbiohub.org/public/igem/igem_collection/1> sbol:member ?s .
    
  	?s sbol:role ?role1 .
  
  		OPTIONAL {?s igem:discontinued ?discontinued} .
  		OPTIONAL {?s igem:dominant ?dominant} . 
      OPTIONAL {?s sbol:displayId ?displayId} .
      OPTIONAL {?s dcterms:title ?title} .
  		OPTIONAL {?s sbh:mutableDescription ?descript} .
  		OPTIONAL {?s sbh:mutableNotes ?notes} .
  		OPTIONAL {?s sbh:mutableProvenance ?source} .
  
  FILTER NOT EXISTS {?s sbol:component ?subcomponent .}
  }

Limit 10000 Offset replacehere
"""


#x = 10,000npython
query2 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX sbol: <http://sbols.org/v2#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX purl: <http://purl.obolibrary.org/obo/>
PREFIX igem: <http://wiki.synbiohub.org/wiki/Terms/igem#>

SELECT
	?s
	?discontinued
	?dominant
    ?displayId
    ?title
    ?role1
	?descript
	?notes
	?source

WHERE {
  ?s a sbol:ComponentDefinition .
  <https://synbiohub.org/public/igem/igem_collection/1> sbol:member ?s .
  Filter not exists {?s sbol:sequence ?seq}
  FILTER regex(?role1, "identifiers")
  
  OPTIONAL {?s igem:discontinued ?discontinued} .
  OPTIONAL {?s igem:dominant ?dominant} .
  OPTIONAL {?s sbol:role ?role1 } . 
  OPTIONAL {?s sbol:displayId ?displayId} .
  OPTIONAL {?s dcterms:title ?title} .
  OPTIONAL {?s sbh:mutableDescription ?descript} .
  OPTIONAL {?s sbh:mutableNotes ?notes} .
  OPTIONAL {?s sbh:mutableProvenance ?source} .
  }

Limit 10000 Offset replacehere
"""
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

afull = []
for i in range(0,10000):
    print(i)
    queryed = query0.replace("replacehere", str(i*10000))
    r = requests.post("https://synbiohub.org/sparql", data = {"query":queryed}, headers = {"Accept":"application/json"})
    d = json.loads(r.text)
    a = json_normalize(d['results']['bindings'])
    afull.append(a)
    if len(a)<10000:
        break
    
a = pd.concat(afull)
a.insert(0, 'Basic', False)


#remove multiple rows (one for each subpart top part combination)
a['Equal'] = np.where(a['role1.value']==a['role2.value'], True, False)
a = a.sort_values('Equal')
a = a.drop_duplicates(['s.value'],keep='first')


abasic = []
for i in range(0,10000):
    print(i)
    queryed = query1.replace("replacehere", str(i*10000))
    r = requests.post("https://synbiohub.org/sparql", data = {"query":queryed}, headers = {"Accept":"application/json"})
    d = json.loads(r.text)
    c = json_normalize(d['results']['bindings'])
    abasic.append(c)
    if len(c)<10000:
        break
    
c = pd.concat(abasic)
c.insert(0, 'Basic', True)
c.insert(15, 'role2.type', None)
c.insert(16, 'role2.value', None)
c.insert(23, 'subpart.type', None)
c.insert(24, 'subpart.value', None)
c.insert(27, 'Equal', False)

blanks = []
for i in range(0,10000):
    print(i)
    queryed = query2.replace("replacehere", str(i*10000))
    r = requests.post("https://synbiohub.org/sparql", data = {"query":queryed}, headers = {"Accept":"application/json"})
    d = json.loads(r.text)
    b = json_normalize(d['results']['bindings'])
    blanks.append(b)
    if len(b)<10000:
        break
blanks = pd.concat(blanks)
blanks.insert(0, 'Basic', True)
blanks.insert(15, 'role2.type', None)
blanks.insert(16, 'role2.value', None)
blanks.insert(19, 'seq.type', None)
blanks.insert(20, 'seq.value', '')
blanks.insert(23, 'subpart.type', None)
blanks.insert(24, 'subpart.value', None)
blanks.insert(27, 'Equal', False)

dfall = pd.concat([a, c, blanks])
sequences = dfall[['s.value','seq.value']]
sequences.to_csv('C:\\Users\\JVM\\Downloads\\Seq1.csv',index=False)
            

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

a1 = dfall[['Basic','s.value', 'discontinued.value','dominant.value','role1.value', 'role2.value', 'subpart.value', 'seq.value', 'descript.value', 'notes.value', 'source.value', 'Equal']]
a1 = a1.sort_values(by=['seq.value'])
a1['DupeSeq'] = a1.duplicated('seq.value',keep='first')
a1['DupeSeqNum'] = (~a1['DupeSeq']).cumsum()
a1['DupeByRole'] = a1.duplicated(['seq.value','role1.value'],keep='first') #Here Duplicates are marked as True
a1['InverseDupeByRole'] = ~a1['DupeByRole'] #Here Duplicates are marked as False


lendict = {'http://identifiers.org/so/SO:0000316' :  40, 'http://identifiers.org/so/SO:0000340' :  6, 'http://identifiers.org/so/SO:0000804' :  6, 'http://identifiers.org/so/SO:0000834' :  6, 'http://identifiers.org/so/SO:0000724' :  6, 'http://identifiers.org/so/SO:0000155' :  40, 'http://identifiers.org/so/SO:0000755' :  40, 'http://identifiers.org/so/SO:0000417' :  6, 'http://identifiers.org/so/SO:0000112' :  6, 'http://identifiers.org/so/SO:0000167' :  6, 'http://identifiers.org/so/SO:0001953' :  6, 'http://identifiers.org/so/SO:0000139' :  6, 'http://identifiers.org/so/SO:0000110' :  6, 'http://identifiers.org/so/SO:0001207' :  6, 'http://identifiers.org/so/SO:0000324' :  6, 'http://identifiers.org/so/SO:0000141' :  6}
namedict = {'http://identifiers.org/so/SO:0000110' :  'Sequence feature', 'http://identifiers.org/so/SO:0000112' :  'Primer', 'http://identifiers.org/so/SO:0000139' :  'Ribosome Entry Site', 'http://identifiers.org/so/SO:0000141' :  'Terminator', 'http://identifiers.org/so/SO:0000155' :  'Plasmid', 'http://identifiers.org/so/SO:0000167' :  'Promoter', 'http://identifiers.org/so/SO:0000316' :  'CDS', 'http://identifiers.org/so/SO:0000324' :  'Tag', 'http://identifiers.org/so/SO:0000340' :  'Chromosome', 'http://identifiers.org/so/SO:0000417' :  'Polypeptide Domain', 'http://identifiers.org/so/SO:0000724' :  'OriT', 'http://identifiers.org/so/SO:0000755' :  'Plasmid Vector', 'http://identifiers.org/so/SO:0000804' :  'Engineered Region', 'http://identifiers.org/so/SO:0000834' :  'Mature Transcript Region', 'http://identifiers.org/so/SO:0001207' :  'T7 RNA Polymerase Promoter', 'http://identifiers.org/so/SO:0001953' :  'Restriction Enzyme Assembly Scar'} 


#a1.insert(3,'MinLen', a1['role1.value'].map(lendict))
#a1.insert(3,'RoleName', a1['role1.value'].map(namedict))
#a1['SeqLen'] = [len(str(x)) for x in a1['seq.value']]
#a1['OverMinLen'] = np.where(a1['SeqLen']>a1['MinLen'], True, False)
###a1['OML_Len'] = [None if x == None else len(x) for x in a1['OverMinLen']]
#a1['UniqueBasic'] = np.where((a1['Basic']==0) & (a1['OverMinLen']>0), a1['seq.value'], None)
#a1['UB_Len'] = [None if x == None else len(x) for x in a1['UniqueBasic']]
#a1['UniqueComposite'] = np.where((a1['Basic']==1) & (a1['OverMinLen']>0), a1['seq.value'], None)
#a1['UC_Len'] = [len(str(x)) for x in a1['UniqueComposite']]
#a1['UniqueCompositeRoleEqual'] = np.where(((a1['Equal']==1)|(a1['Basic']==0)) & (a1['OverMinLen']>0), a1['seq.value'], None)
#a1['UCRE_Len'] = [len(str(x)) for x in a1['UniqueCompositeRoleEqual']]
###print(a1.iloc[0])

a1.insert(3,'MinLen', a1['role1.value'].map(lendict))
a1.insert(3,'RoleName', a1['role1.value'].map(namedict))


#Create Filter Mask
a1['SeqLen'] = [len(str(x)) for x in a1['seq.value']]
a1['All'] = True
a1['OverMinLen'] = np.where(a1['SeqLen']>a1['MinLen'], True, False)
a1['BasicMinLen'] = np.where((a1['Basic']) & (a1['OverMinLen']), True, False)
a1['CompositeMinLen'] = np.where((~a1['Basic']) & (a1['OverMinLen']), True, False)
a1['CompRoleEqual'] = np.where(((a1['Equal'])|(a1['Basic'])) & (a1['OverMinLen']), True, False)
a1['CompOnlyRoleEqual'] = np.where((a1['Equal']) & (a1['OverMinLen']), True, False)

#Unique in role
a1['U_OverMinLen'] = np.where(a1['OverMinLen'] & ~a1['DupeByRole'], True, False)
a1['U_BasicMinLen'] = np.where(a1['BasicMinLen'] & ~a1['DupeByRole'], True, False)
a1['U_CompositeMinLen'] = np.where(a1['CompositeMinLen'] & ~a1['DupeByRole'], True, False)
a1['U_CompRoleEqual'] = np.where(a1['CompRoleEqual'] & ~a1['DupeByRole'], True, False)
a1['U_CompOnlyRoleEqual'] = np.where(a1['CompOnlyRoleEqual'] & ~a1['DupeByRole'], True, False)

###table = pd.pivot_table(a1, index=['RoleName'], aggfunc={'InverseDupeByRole':['count','sum']})
###print(table)
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
####print(a1.iloc[0])
###
###
table = pd.pivot_table(a1, index=['RoleName'], aggfunc={
            'seq.value':['nunique'],
            'SeqLen':['count','min', 'max', 'mean', 'std'],
            'OverMinLen':['sum'],
            'U_OverMinLen':['sum'],
            'MinLen':['max'],
            'U_BasicMinLen':['sum'],
            'U_CompositeMinLen':['sum'],
            'U_CompRoleEqual':['sum'],
            'U_CompOnlyRoleEqual':['sum']
                       })

print(table)
table.to_csv("C:\\Users\\JVM\\Downloads\\Pivot.csv")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

####table.index
####a1['SeqLen'].hist(by=a1['RoleName'], bins=edges)

##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
###
#filters = a1.columns[19:]
#edges = [*range(0,70000,10)]
#
#for fcounter, fltr in enumerate(filters):
#    fltr_temp = a1[a1[fltr]]
#    for rcounter, role in enumerate(table.index):
#         plt.figure(rcounter)
#         print(f'{rcounter+1}/{len(table.index)}: {role}')
#         temp = fltr_temp[fltr_temp['RoleName'].str.match(role)]
#         temp['SeqLen'].hist(bins=edges, figsize=(10,10),
#             histtype='step', facecolor="None", label=[fltr])
#
#         
#for rcounter,role in enumerate(table.index):
#    plt.figure(rcounter)
#    axes = plt.gca()
#    axes.set_yscale('log')
#    axes.set_xscale('log')
#    plt.xlabel('Sequence Length')
#    plt.ylabel('Number of Occurrences')
#    plt.title(f'{role}')
#    plt.legend()
#    plt.savefig(f'C:\\Users\\JVM\\Downloads\\Distribution\\FurtherLogLog_{rcounter}_{role}.jpg', bbox_inches='tight')
#
#plt.close()

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##table.columns = ['Total Sequence Number', 'MinLen', "Over Min Length", "SeqLen Max","SeqLen Mean",
##                "SeqLen Min", "SeqLen Std", 'Unique Over Min Len','Unique Seq Number']
###NB when Duplicate 2 sum is used you don't get the correct unique count as there are sequences that are repeated between object types
#print(table)
#print(table.iloc[0])
##
#table.to_csv("C:\\Users\\JVM\\Downloads\\Pivot.csv")
#a1.to_csv("C:\\Users\\JVM\\Downloads\\a1.csv")
#
#a1.to_csv("C:\\Users\\JVM\\Downloads\\iGEM_ALL.csv",index=False)
##print(lessthan)