# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 11:19:22 2020

@author: JVM
"""
import requests
import os
import pandas as pd


def make_subpart_map(url, counter):
    cwd = os.getcwd()
    
    partname = url[url.find("igem/")+5:]
    partname = partname[:partname.find("/")]
    
    get_url = "http://song.ece.utah.edu/dnafiles/"+partname
    
    linearity = 'linear'
    detect = 'true'
    
    
    #get fasta for url
    s = requests.get(f"{url}/fasta")
    fasta_text = s.text
    
    #remove preamble
    preface_end = fasta_text.find("bp)")
    fasta_text = fasta_text[preface_end+3:]
    
    #remove line breaks
    fasta_text = fasta_text.replace('\n', '')
    
    newtext_url = "http://song.ece.utah.edu/examples/pages/acceptNewText.php" #link to post to
    
    
    #data to send
    data = {"textToUpload": fasta_text,
            "detectFeatures": detect,
            "textId": partname,
            "textName": partname,
            "topology": linearity} 
    #parameters to send
    params ={} 
    
    #post data to snapgene server
    requests.post(newtext_url, data = data, params = params,  headers = {"Accept":"text/plain"})
    
    #get the genebank file generated
    t = requests.get(f"{get_url}.gb")
    
    genbank = t.text
    #remove odd additional spacing that prevents genebank from being read
    genbank = "\n".join(genbank.splitlines())
    with open(os.path.join(cwd, "subpartcheck", f"{counter}_{partname}.gb"), 'w') as f:
            f.write(genbank)
    
    #get the png map generated
    q = requests.get(f"{get_url}.png")
    with open(os.path.join(cwd, "subpartcheck", f"{counter}_{partname}.png"), 'wb') as f:
            f.write(q.content)
            
    return(genbank)
    
# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#from url list collect all of the annotated pngs and the annotated gb
cwd = os.getcwd()

url_list = pd.read_csv(os.path.join(cwd,'terms_to_check_subparts.csv'), header = None)

for index, url in enumerate(url_list[0]):
    counter = index+100
    make_subpart_map(url, counter)
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#CONVERT Genebank to sbol


import glob
cwd = os.getcwd()
import os
import requests

in_location = os.path.join(cwd, "subpartcheck", "")
out_location = os.path.join(cwd, "subpartcheck", "SBOL","")

in_files = glob.glob(f'{in_location}*.gb')

for file_name in in_files:

    #get the just filename put in and remove the .gb ending
    out_name = os.path.split(file_name)[1][:-3]
    
    out_file = os.path.join(out_location, f'{out_name}.xml')
    
    
    file = open(file_name,"r") 
    genbank = file.read()
    file.close()

    request = { 'options': {'language' : 'SBOL2',
                            'test_equality': False,
                            'check_uri_compliance': False,
                            'check_completeness': False,
                            'check_best_practices': False,
                            'fail_on_first_error': False,
                            'provide_detailed_stack_trace': False,
                            'uri_prefix': 'trial',
                            'version': '',
                            'insert_type': False
                                    },
                'return_file': True,
                'main_file': genbank
              }
    
    resp = requests.post("https://validator.sbolstandard.org/validate/", json=request)
    content = resp.json()["result"]
    
    
    with open(out_file, 'w') as f:
            f.write(content)


# #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

role_dict = {'0005836':'regulatory_region', '0000551':'polyA_signal_sequence',
 '0000316':'CDS', '0000167':'promoter', '0000553':'polyA_site', 
 '0005850':'primer_binding_site', '0000139':'ribosome_entry_site',
 '0000110':'sequence_feature', '0000296':'origin_of_replication',
 '0000141':'terminator', '0000418':'signal_peptide ', '0000673':'transcript',
 '0001411':'biological_region', '0000188':'intron', '0000657':'repeat_region',
 '0000165':'terminator_of_type_2_RNApol_III_promoter', '0000655':'ncRNA',
 '0000204':'five_prime_UTR'}




#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Collect all annotations from the sbol


import os
cwd = os.getcwd()
import glob

role_looking_for = '0000139'
in_location = os.path.join(cwd, "subpartcheck", "SBOL", "")

in_files = glob.glob(f'{in_location}*.xml')

in_path = os.path.join(cwd,"subpartcheck","SBOL","121_BBa_J34805.xml")

print(in_path)

import sbol2
from sbol2.document import Config, Document
import pandas as pd

#file_name = "C:\\Users\\JVM\\Downloads\\BBa_E0240.xml"

Config.setOption('sbol_compliant_uris', True)
Config.setOption('sbol_typed_uris', False)

sequence_code = "['http://identifiers.org/so/SO:0002206']"

file_names = in_files

annotations_df = []

# file_names = in_files[0:1]



track = 0
for file_name in file_names:
    
    Non_interested_role = False
    role_name = []
    
    part_name = os.path.split(file_name)[1]
    
    doc = Document()
    
    doc.read(file_name)
    
    #print(doc)
    
    annotations = []
    annotation_roles = []
    annotation_start_stop = []
    annot_seq = []
    
    print(track)
    track = track+1
    for compdef in doc.componentDefinitions:
#        print(compdef)
        for annotation in compdef.sequenceAnnotations:
            for loc in annotation.locations:
                # print(f"{loc.start}, {loc.end}")
                print("#")

            if str(annotation.roles) != sequence_code:
                for loc in annotation.locations:
                    annotation_start_stop.append([loc.start, loc.end])
                split = os.path.split(str(annotation))[1]
                annotations.append(split)
                
                role = str(annotation.roles)[31:-2]
                
                annotation_roles.append(role)
                
                if role != role_looking_for:
                    Non_interested_role = True
                    role_name.append(role_dict[role])

                    
    num_anno = len(annotations)            
                
                
    
    for sequence in doc.sequences:
        seq = str(sequence.elements)[22:-3]
        seq_len = len(seq)

    for annot in annotation_start_stop:
        annot_seq.append(seq[annot[0]:annot[1]]) #CHECK THIS WITH CHRIS, IS IT INCLUSIVE??
    if len(annotation_start_stop) == 0:
        annot_seq = [seq]
            
    annotations_df.append([part_name, annotations, annotation_roles,
                            num_anno, Non_interested_role, seq_len, role_name,
                            annotation_start_stop, seq_len, seq, annot_seq])




annotations_df = pd.DataFrame(annotations_df, columns = ["Name", 
                        "annotations","roles", "Number_of_Annotations",
                        "non_interested_role_parts_present", "Seq_len", 
                        "role_name", "Annotation_Start_Stop", "Sequence_length",
                        "Sequence", "Annotations_Seq"]) 

# annotations_df.to_csv(os.path.join(cwd,"Annotations_short1_RBS.csv"))
    
pivot = pd.pivot_table(annotations_df, index=["non_interested_role_parts_present",
            'Number_of_Annotations'], aggfunc={
            'Number_of_Annotations':['count'], "Seq_len":['max','min','mean']})

# pivot.to_csv(os.path.join(cwd,"Annotations_Pivot_RBS.csv")) #comment
    
print(pivot)

#annotation names and percentage of sequence, look at all basic terminators


##############################################################################################
