# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:19:22 2020

@author: JVM
"""
#import requests
#import os
#import pandas as pd
#
#
#def make_subpart_map(url, counter):
#    cwd = os.getcwd()
#    
#    partname = url[url.find("igem/")+5:]
#    partname = partname[:partname.find("/")]
#    
#    get_url = "http://song.ece.utah.edu/dnafiles/"+partname
#    
#    linearity = 'linear'
#    detect = 'true'
#    
#    
#    #get fasta for url
#    s = requests.get(f"{url}/fasta")
#    fasta_text = s.text
#    
#    #remove preamble
#    preface_end = fasta_text.find("bp)")
#    fasta_text = fasta_text[preface_end+3:]
#    
#    #remove line breaks
#    fasta_text = fasta_text.replace('\n', '')
#    
#    newtext_url = "http://song.ece.utah.edu/examples/pages/acceptNewText.php" #link to post to
#    
#    
#    #data to send
#    data = {"textToUpload": fasta_text,
#            "detectFeatures": detect,
#            "textId": partname,
#            "textName": partname,
#            "topology": linearity} 
#    #parameters to send
#    params ={} 
#    
#    #post data to snapgene server
#    requests.post(newtext_url, data = data, params = params,  headers = {"Accept":"text/plain"})
#    
#    #get the genebank file generated
#    t = requests.get(f"{get_url}.gb")
#    
#    genbank = t.text
#    #remove odd additional spacing that prevents genebank from being read
#    genbank = "\n".join(genbank.splitlines())
#    with open(os.path.join(cwd, "subpartcheck", f"{counter}_{partname}.gb"), 'w') as f:
#            f.write(genbank)
#    
#    #get the png map generated
#    q = requests.get(f"{get_url}.png")
#    with open(os.path.join(cwd, "subpartcheck", f"{counter}_{partname}.png"), 'wb') as f:
#            f.write(q.content)
#            
#    return(genbank)
#    
##%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
##from url list collect all of the annotated pngs and the annotated gb
#cwd = os.getcwd()
#
#url_list = pd.read_csv(os.path.join(cwd,'terms_to_check_subparts.csv'), header = None)
#
#for index, url in enumerate(url_list[0]):
#    counter = index+100
#    make_subpart_map(url, counter)
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#import glob
#cwd = os.getcwd()
#import os
#import requests
#
#in_location = os.path.join(cwd, "subpartcheck", "")
#out_location = os.path.join(cwd, "subpartcheck", "SBOL","")
#
#in_files = glob.glob(f'{in_location}*.gb')
#
#for file_name in in_files:
#
#    #get the just filename put in and remove the .gb ending
#    out_name = os.path.split(file_name)[1][:-3]
#    
#    out_file = os.path.join(out_location, f'{out_name}.xml')
#    
#    
#    file = open(file_name,"r") 
#    genbank = file.read()
#    file.close()
#
#    request = { 'options': {'language' : 'SBOL2',
#                            'test_equality': False,
#                            'check_uri_compliance': False,
#                            'check_completeness': False,
#                            'check_best_practices': False,
#                            'fail_on_first_error': False,
#                            'provide_detailed_stack_trace': False,
#                            'uri_prefix': 'trial',
#                            'version': '',
#                            'insert_type': False
#                                    },
#                'return_file': True,
#                'main_file': genbank
#              }
#    
#    resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
#    content = resp.json()["result"]
#    
#    
#    with open(out_file, 'w') as f:
#            f.write(content)
           
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import os
cwd = os.getcwd()
import glob

in_location = os.path.join(cwd, "subpartcheck", "SBOL", "")

in_files = glob.glob(f'{in_location}*.xml')

#in_path = os.path.join(cwd,"subpartcheck","SBOL","121_BBa_J34805.xml")

#print(in_path)

import sbol2
from sbol2.document import Config, Document
import pandas as pd

#file_name = "C:\\Users\\JVM\\Downloads\\BBa_E0240.xml"

Config.setOption('sbol_compliant_uris', True)
Config.setOption('sbol_typed_uris', False)

file_names = in_files

annotations_df = []

for file_name in file_names:
    part_name = os.path.split(file_name)[1]
    
    doc = Document()
    
    doc.read(file_name)
    
    #print(doc)
    
    annotations = []
    
    for compdef in doc.componentDefinitions:
#        print(compdef)
        for annotation in compdef.sequenceAnnotations:
            split = os.path.split(str(annotation))[1]
            annotations.append(split)
            
    num_anno = len(annotations)
            
    annotations_df.append([part_name, annotations, num_anno])




annotations_df = pd.DataFrame(annotations_df, columns = ["Name", "annotations", "Number_of_Annotations"]) 

pivot = pd.pivot_table(annotations_df, index=['Number_of_Annotations'], aggfunc={
            'Number_of_Annotations':['count']})
    
print(pivot)





















    
    