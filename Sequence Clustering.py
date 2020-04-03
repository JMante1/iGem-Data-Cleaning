# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 18:22:09 2020

@author: JVM
"""

import pandas as pd
import difflib
import matplotlib.pyplot as plt
from scipy import spatial, cluster


#df = pd.read_csv("C:\\Users\\JVM\\Downloads\\Sequences.csv")
#df = df.drop_duplicates(subset=['Sequences'])
#URIs = df['URI'].to_numpy()
#cutoff = 80
#lendf = len(df)
#clusters =[]
#
#
##for counter, row in enumerate(df['Sequences']):
##    cluster = []
##    print(f'{counter+1}/{lendf}')
##    for counter2, row2 in enumerate(df['Sequences']):
##        if counter2 == counter:
##            d = 0
##        else:
##            seq=difflib.SequenceMatcher(None, row,row2)
##            d= 100 - seq.ratio()*100
##        cluster.append(d)
##    clusters.append(cluster)
#
#for counter, row in enumerate(df['Sequences']):
#    cluster = []
#    print(f'{counter+1}/{lendf}')
#    for counter2, row2 in enumerate(df['Sequences']):
#        if counter == counter2:
#            d = 0
#        elif counter2 > counter:
#            seq=difflib.SequenceMatcher(None, row,row2)
#            d= 100 - seq.ratio()*100
#        else:
#            d = clusters[counter2][counter]
#        cluster.append(d)
#    clusters.append(cluster)
#
#
#matrix = pd.DataFrame(clusters)
#points = len(matrix)
#y = spatial.distance.squareform(matrix)
#z = cluster.hierarchy.linkage(y, method='centroid')
#dftree = pd.DataFrame(z)
#
#cluck = list(range(points, points+len(z)))
#
#dftree['4']=cluck
#
#clustered = cluster.hierarchy.fcluster(z, t=100-cutoff, criterion='distance')
#
#
#
#dftree2 = dftree.where(dftree[2]<20).dropna()

dc = {}

for i, row in dftree2.iterrows():
    dc[row['4']]=[row[0],row[1]]
    
    
print(dc)
todel = []

for i in dc:
    print(i)
    temp = []
    
    if dc[i][0]>=189:
        temp += dc[dc[i][0]]
        todel += [dc[i][0]]
    else:
        temp += [dc[i][0]]
        
    if dc[i][1]>=189:
        temp += dc[dc[i][1]]
        todel += [dc[i][1]]
    else:
        temp += [dc[i][1]]
    dc[i] = temp

for i in todel:
    del(dc[i])
    
print(dc)
            

###https://scipy.github.io/devdocs/generated/scipy.cluster.hierarchy.fcluster.html#scipy.cluster.hierarchy.fcluster
#numclust = int(max(clustered))
#
#plt.figure(figsize=(30,30))
#dendo = cluster.hierarchy.dendrogram(z, p = numclust,
#        get_leaves=True, labels=URIs, 
#        color_threshold = 20)
#plt.savefig(f'C:\\Users\\JVM\\Downloads\\Dendo.jpg', bbox_inches='tight')

#df['cluster']=clustered
#df = df.sort_values(by=['cluster'])
#
#
#df['CluSize']= df.duplicated(subset=['cluster'])+0
#table = pd.pivot_table(df, index=['cluster'], aggfunc={'CluSize':['sum']})
#temp = table['CluSize']['sum']+1
#temp = temp.to_frame()
#temp = temp.to_dict('index')
#temp = dict(map(lambda x: (x[0], x[1]['sum']), temp.items() ))
#
#df['CluSize']=df['cluster'].map(temp)
#
#
#plt.figure(figsize=(30,30))
#
#dendo = cluster.hierarchy.dendrogram(z, labels=URIs, distance_sort=True)
#plt.savefig(f'C:\\Users\\JVM\\Downloads\\Dendo.jpg', bbox_inches='tight')
#plt.close()
#
#
#def augmented_dendrogram(*args, **kwargs):
#
#    ddata = cluster.hierarchy.dendrogram(*args, **kwargs)
#    heights = []
#
#    if not kwargs.get('no_plot', False):
#        for i, d in zip(ddata['icoord'], ddata['dcoord']):
#            x = 0.5 * sum(i[1:3])
#            print(i[1:3])
#            y = d[1]
#            heights.append(y)
#            plt.plot(x, y, 'ro')
#            plt.annotate("%.3g" % y, (x, y), xytext=(0, -8),
#                         textcoords='offset points',
#                         va='top', ha='center')
#
#    return ddata, heights
#
#plt.figure(figsize=(30,30))
#ddendo, heights = augmented_dendrogram(z, labels=URIs, distance_sort=True)
#plt.savefig(f'C:\\Users\\JVM\\Downloads\\AugDendo.jpg', bbox_inches='tight')
#plt.close()

##dict_keys(['icoord', 'dcoord', 'ivl', 'leaves', 'color_list'])
#heights = []
#for i, d in zip(dendo['icoord'], dendo['dcoord']):
#    heights.append(d[1])

#clusters2 = []
#clusters3 = []
#for counter, row in enumerate(df['Sequences']):
#    print(f'{counter+1}/{lendf}')
#    for counter2, row2 in enumerate(df['Sequences']):
#        if counter2 > counter:
#            seq=difflib.SequenceMatcher(None, row,row2)
#            d=seq.ratio()*100
#            if d > cutoff:
#                clusters2.append([counter,counter2,d])
#                clusters3.append([df['URI'][counter],df['URI'][counter2],d])
                

    

#matrix = pd.DataFrame(clusters)
#matrix2 = matrix.where(matrix>cutoff)
#matrix2.dropna(axis=0, how='all', inplace=True)
#matrix2.dropna(axis=1, how='all', inplace=True)




#a = matrix2.shape[0]*matrix2.shape[1]
#b = matrix2.isna().sum().sum()
#
#c = a-b