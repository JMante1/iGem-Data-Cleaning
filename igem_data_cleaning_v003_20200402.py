# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 20:01:38 2020

@author: JVM
"""
import json
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pandas.io.json import json_normalize
import os

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def sparqling(query_text, is_basic = True, 
              no_sequence = False, progress = True):
    all_pages = []
    
    #loops over all pages and extracts query results
    for i in range(0,2000):
        
        if progress: #print progress
            print(i)
            
        #replace placeholder in query_text with page number to get
        queryed = query_text.replace("replacehere", str(i*10000))
        
        #make request for data
        r = requests.post("https://synbiohub.org/sparql",
                          data = {"query":queryed},
                          headers = {"Accept":"application/json"})
        
        #reformat page data
        d = json.loads(r.text)
        one_page = json_normalize(d['results']['bindings'])
        
        #add page data to all pages data
        all_pages.append(one_page)
        
        #if the page was no longer a full page stop loop
        if len(one_page)<10000:
            break
        
    #create pandas data frame containing all page information
    all_pages = pd.concat(all_pages)
    
    """Data Wrangling"""
    #Making sure data from all three queries has all three columns
    
    all_pages['Basic'] = is_basic
    
    if is_basic:
        all_pages['role2.type'] = None
        all_pages['role2.value'] = None
        all_pages['subpart.type'] = None
        all_pages['subpart.value'] = None
        all_pages['Equal'] = False
        
        if no_sequence:
            all_pages['seq.type'] = None
            all_pages['seq.value'] = ''
        
    else:
        #Check whether or not subpart roles match top level role
        all_pages['Equal'] = np.where(all_pages['role1.value']==all_pages['role2.value'], 
                 True, False)
        #Sort so False comes at the top (so if any subpart roles don't match
        #the top level part they will be the first part seen)
        all_pages = all_pages.sort_values('Equal')
        
        #remove duplicates so only one line per top level part
        all_pages = all_pages.drop_duplicates(['s.value'],keep='first')

    return(all_pages)
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
progress = True #Whether to print out progress going through sparql pages
seq_out = True #Whether to save a csv of the sequences output
pivot_out = True #Whether to save the csv of the pivot table
igem_out = True #Whether to save a csv with all filtering data

cwd = os.getcwd() #get current working directory

#Names of files containing the sparql code
queries = ['Sbol-role-of-subparts', 'SBOL-Subpartless-Parts',
           'Sparql-Blanks']

#read in the three queries
query_texts = []
for query in queries:
    f_open = open(f'{cwd}\\Sparql-Queries\\{query}.txt','r')
    query_texts += [f_open.read()]
    f_open.close()

#Run each of the three queries
subparts = sparqling(query_texts[0], is_basic=False, progress = progress)
no_subparts = sparqling(query_texts[1], progress = progress)
no_sequence = sparqling(query_texts[2], no_sequence = True, progress = progress)

#Create one pandas dataframe with all of the information
df_all = pd.concat([subparts, no_subparts, no_sequence],sort=True)

#Output sequences only
if seq_out:
    sequences = df_all[['s.value','seq.value']]
    sequences.to_csv(f'{cwd}\\Outputs\\Sequences.csv',index=False)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#Read in the minimum lengths to use for each part type
df_min_len = pd.read_csv(f'{cwd}\\Min_Len\\Min_Len.csv', index_col = 0)
#create a dictionary
dict_min_len = df_min_len.to_dict()

#add a column with the minimum length for each row
df_all['Min_Len_Param'] = df_all['role1.value'].map(dict_min_len['Min_Len'])

#add a column with the maximum length for each row
df_all['Max_Len_Param'] = df_all['role1.value'].map(dict_min_len['Max_Len'])

#add a column with the common role name for each row
df_all['Role_Name'] = df_all['role1.value'].map(dict_min_len['Role_Name'])
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#drop unnecessar columns
df_all = df_all.drop(columns=['descript.datatype', 'descript.type',
       'discontinued.type', 'displayId.type', 'dominant.type',
       'notes.datatype', 'notes.type', 'role1.type',
       'role2.type', 's.type', 'seq.type', 'source.type', 'subpart.type',
       'title.type', 'title.value'])

"""Duplicates mask"""
#sort by sequence value
df_all = df_all.sort_values(by=['seq.value'])

#column with false everytime a new non duplicate sequence is seen (based on sort order)
df_all['Dupe_Seq'] = df_all.duplicated('seq.value',keep='first')

#Cluster number for each sequence (e.g. all blanks are 1, 
#next seq are all 2 etc)
df_all['Dupe_Seq_Num'] = (~df_all['Dupe_Seq']).cumsum()

#column with false everytime a new non duplicate sequence for that role 
#is seen (based on sort order)
df_all['Dupe_By_Role'] = df_all.duplicated(['seq.value','role1.value'],keep='first') #Here Duplicates are marked as True

#Not of Dupe by role (Duplicates are marked as false)
df_all['Inverse_Dupe_By_Role'] = ~df_all['Dupe_By_Role']
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""Filters"""
#column added with an integer value of sequence length
df_all['Seq_Len'] = df_all['seq.value'].str.len()

#If under max length true
df_all['Under_Max_Len'] = np.where(df_all['Seq_Len']<df_all['Max_Len_Param'], True, False)


#If over min length true
df_all['Over_Min_Len'] = np.where(df_all['Seq_Len']>df_all['Min_Len_Param'], True, False)

#if over min length and a basic part true
df_all['Basic_Min_Len'] = np.where((df_all['Basic']) & (df_all['Over_Min_Len']), True, False)

#if composite and over min length then true
df_all['Composite_Min_Len'] = np.where((~df_all['Basic']) & (df_all['Over_Min_Len']), True, False)

#True if over min length and either basic or compposite with subpart role equal to part role
df_all['Basic_Or_Comp_Role_Equal'] = np.where(((df_all['Equal'])|(df_all['Basic'])) & (df_all['Over_Min_Len']), True, False)

#True if over min length and compposite with subpart role equal to part role
df_all['Comp_Role_Equal'] = np.where((df_all['Equal']) & (df_all['Over_Min_Len']), True, False)

#Like columns added above but must also be the first occurence of the sequence by role
df_all['U_Over_Min_Len'] = np.where(df_all['Over_Min_Len'] & ~df_all['Dupe_By_Role'], True, False)
df_all['U_Basic_Min_Len'] = np.where(df_all['Basic_Min_Len'] & ~df_all['Dupe_By_Role'], True, False)
df_all['U_Composite_Min_Len'] = np.where(df_all['Composite_Min_Len'] & ~df_all['Dupe_By_Role'], True, False)
df_all['U_Basic_Or_Comp_Role_Equal'] = np.where(df_all['Basic_Or_Comp_Role_Equal'] & ~df_all['Dupe_By_Role'], True, False)
df_all['U_Comp_Role_Equal'] = np.where(df_all['Comp_Role_Equal'] & ~df_all['Dupe_By_Role'], True, False)

if igem_out:
    df_all.to_csv(f'{cwd}\\Outputs\\iGEM_All.csv',index=False)
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

#Count simply counts the number of entries, nunique counts the number of
#unique entries, and sum counts the number of true entries. min, max, mean,
#and std are just what would be expected
table = pd.pivot_table(df_all, index=['Role_Name'], aggfunc={
            'seq.value':['nunique'],
            'Seq_Len':['count','min', 'max', 'mean', 'std'],
            'Over_Min_Len':['sum'],
            'U_Over_Min_Len':['sum'],
            'Min_Len_Param':['max'],
            'U_Basic_Min_Len':['sum'],
            'U_Composite_Min_Len':['sum'],
            'U_Basic_Or_Comp_Role_Equal':['sum'],
            'U_Comp_Role_Equal':['sum']
                       })

if pivot_out:
    table.to_csv(f'{cwd}\\Outputs\\Pivot.csv')

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""Create Histograms of a column"""
Col_Name = 'U_Basic_Min_Len' #looking at basic parts
edges = [*range(0,70000,10)] #making sure bins are only 10 wide

for role in table.index:
    #select only rows with the role specified
    fltr_temp = df_all[df_all['Role_Name']==role]
    
    
    #select only rows where column value is true
    fltr_temp = fltr_temp[fltr_temp[Col_Name]]
    
    #create a new figure
    plt.figure()
    
    #create histogram
    fltr_temp['Seq_Len'].hist(figsize=(10,10),
             histtype='step', facecolor="None",
             bins=edges)
    
    #Make histogram pretty
    axes = plt.gca()
    axes.set_yscale('log')
    axes.set_xscale('log')
    plt.xlabel('Sequence Length')
    plt.ylabel('Number of Occurrences')
    plt.title(f'{role}: {Col_Name}')
    
    
    plt.savefig(f'{cwd}\\Outputs\\Histogram_{role}.jpg')
    plt.close()
