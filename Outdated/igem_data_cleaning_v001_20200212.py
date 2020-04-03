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
a.insert(0, 'Basic', 1)

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
c.insert(0, 'Basic', 0)
c.insert(15, 'role2.type', None)
c.insert(16, 'role2.value', None)
c.insert(23, 'subpart.type', None)
c.insert(24, 'subpart.value', None)

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
blanks.insert(0, 'Basic', 0)
blanks.insert(15, 'role2.type', None)
blanks.insert(16, 'role2.value', None)
blanks.insert(19, 'seq.type', None)
blanks.insert(20, 'seq.value', None)
blanks.insert(23, 'subpart.type', None)
blanks.insert(24, 'subpart.value', None)


dfall = pd.concat([a, c, blanks])


a1 = dfall[['Basic','s.value', 'discontinued.value','dominant.value','role1.value', 'role2.value', 'subpart.value', 'seq.value', 'descript.value', 'notes.value', 'source.value']]
a1 = a1.sort_values(by=['seq.value'])
a1.insert(0, 'Duplicate1', ~a1.duplicated('seq.value',keep='first'))
a1.insert(0, 'Duplicate', a1['Duplicate1'].cumsum())
a1.insert(0, 'Duplicate2', a1['Duplicate1']+0)
###del a1['Duplicate1']
##print(a1[['Duplicate2', 'Duplicate1','seq.value']])


lendict = {'http://identifiers.org/so/SO:0000110' :  6, 'http://identifiers.org/so/SO:0000112' :  6, 'http://identifiers.org/so/SO:0000139' :  6, 'http://identifiers.org/so/SO:0000141' :  3, 'http://identifiers.org/so/SO:0000155' :  6, 'http://identifiers.org/so/SO:0000167' :  6, 'http://identifiers.org/so/SO:0000316' :  40, 'http://identifiers.org/so/SO:0000324' :  6, 'http://identifiers.org/so/SO:0000340' :  6, 'http://identifiers.org/so/SO:0000417' :  6, 'http://identifiers.org/so/SO:0000724' :  6, 'http://identifiers.org/so/SO:0000755' :  6, 'http://identifiers.org/so/SO:0000804' :  6, 'http://identifiers.org/so/SO:0000834' :  6, 'http://identifiers.org/so/SO:0001207' :  6, 'http://identifiers.org/so/SO:0001953' :  6}
namedict = {'http://identifiers.org/so/SO:0000110' :  'Sequence feature', 'http://identifiers.org/so/SO:0000112' :  'Primer', 'http://identifiers.org/so/SO:0000139' :  'Ribosome Entry Site', 'http://identifiers.org/so/SO:0000141' :  'Terminator', 'http://identifiers.org/so/SO:0000155' :  'Plasmid', 'http://identifiers.org/so/SO:0000167' :  'Promoter', 'http://identifiers.org/so/SO:0000316' :  'CDS', 'http://identifiers.org/so/SO:0000324' :  'Tag', 'http://identifiers.org/so/SO:0000340' :  'Chromosome', 'http://identifiers.org/so/SO:0000417' :  'Polypeptide Domain', 'http://identifiers.org/so/SO:0000724' :  'OriT', 'http://identifiers.org/so/SO:0000755' :  'Plasmid Vector', 'http://identifiers.org/so/SO:0000804' :  'Engineered Region', 'http://identifiers.org/so/SO:0000834' :  'Mature Transcript Region', 'http://identifiers.org/so/SO:0001207' :  'T7 RNA Polymerase Promoter', 'http://identifiers.org/so/SO:0001953' :  'Restriction Enzyme Assembly Scar'} 


a1.insert(3,'MinLen', a1['role1.value'].map(lendict))
a1.insert(3,'RoleName', a1['role1.value'].map(namedict))
a1['SeqLen'] = [len(str(x)) for x in a1['seq.value']]
a1['OverMinLen'] = np.where(a1['SeqLen']>a1['MinLen'], 1, 0)
a1['UniqueOverMin'] = np.where(a1['OverMinLen']>0, a1['seq.value'], None)
a1['UniqueBasic'] = np.where((a1['Basic']==0) & (a1['OverMinLen']>0), a1['seq.value'], None)
a1['UniqueComposite'] = np.where((a1['Basic']==1) & (a1['OverMinLen']>0), a1['seq.value'], None)
a1.insert(0, 'CompositeTypeEqual', (a1['role1.value']==a1['role2.value'])+0)
a1['UniqueCompositeRoleEqual'] = np.where(((a1['CompositeTypeEqual']>0)|(a1['Basic']==0)) & (a1['OverMinLen']>0), a1['seq.value'], None)
##print(a1.iloc[0])
#
#
table = pd.pivot_table(a1, index=['RoleName'], aggfunc={
            'Duplicate1':'count',
            'seq.value':['nunique'],
            'SeqLen':['min', 'max', 'mean', 'std'],
            'OverMinLen':['sum'],
            'UniqueOverMin':['nunique'],
            'MinLen':['max'],
            'UniqueBasic':['nunique'],
            'UniqueComposite':['nunique'],
            'UniqueCompositeRoleEqual':['nunique']
                       })
#table.columns = ['Total Sequence Number', 'MinLen', "Over Min Length", "SeqLen Max","SeqLen Mean",
#                "SeqLen Min", "SeqLen Std", 'Unique Over Min Len','Unique Seq Number']
###NB when Duplicate 2 sum is used you don't get the correct unique count as there are sequences that are repeated between object types
print(table)
print(table.iloc[0])
#
table.to_csv("C:\\Users\\JVM\\Downloads\\Pivot.csv")
#
##a1.to_csv("C:\\Users\\JVM\\Downloads\\iGEM_ALL.csv",index=False)
##print(lessthan)