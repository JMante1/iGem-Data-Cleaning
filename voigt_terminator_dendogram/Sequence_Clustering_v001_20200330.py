# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 18:22:09 2020

@author: JVM
"""

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
import pandas as pd
import difflib
import matplotlib.pyplot as plt
from scipy import spatial, cluster
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def seqdist(df, seq_col_name, uri_col_name, drop_dupe=True, progress = True):
    """Takes in a dataframe with a bunch of sequences and returns pairwise
    distance matrix suitable for use in clustering methods.
    
    Requires
    ---------
    Pandas
    difflib
    
    Parameters
    -----------
    df : Pandas dataframe (m*n)
        Contains at least one column with str formatted sequence data
        and one column with str formatted names for the sequence data
        
    seq_col_name : str 
        Name of the column in df containing the str formatted sequence data
        
    uri_col_name : str 
        Name of the column in df containing the str formatted sequence names
        
    drop_dupe : Boolean, default: True
        If true only the first of a duplicate sequence will be used
        
    progress : Boolean, default: True
        If true will print out percentage done intermittantly

    Returns
    --------
    clusters : list of lists (p*p)
        Returns a symmetrical pairwise distance matrix where
        clusters[0][1] = clusters[1][0] = distance between sequence 0 
        and sequence 1 (note p<=n as NaN and possibly duplicate values
        are dropped)
        
    URIs: list (1*p+1)
        List of the names of the nodes used in the pairwise distance matrix

    Example
    --------
    data = {'Names':['RBS', '1887', 'RibosomeBindingSite', 'RibosomeEntrySite','Barcode187'],
            'Sequence':['atgcaaa', 'tgcccga', 'atgcaat', 'ccatctgc', 'aagggggcg']} 
  
    # Create DataFrame 
    df = pd.DataFrame(data) 
  
    
    distance_matrix, URIs = seqdist(df, 'Sequence', 'Names')
    square_form = spatial.distance.squareform(clusters)
    z = cluster.hierarchy.linkage(square_form, method='centroid')
    """
    #drop any rows which have NaN in the sequence column
    df = df.dropna(subset=[seq_col_name]) 
    
    #Drop duplicate sequences if the flag is set to true
    if drop_dupe:
        df = df.drop_duplicates(subset=[seq_col_name])
    
    #reset the index
    df.reset_index(drop=True, inplace = True)
    
    #create URI names
    URIs = df[uri_col_name]
    
    #create blank clusters list
    clusters =[]
    
    #define the length of the dataframe
    lendf = len(df)
    
    #cycle through each column
    for counter, row in enumerate(df[seq_col_name]):
        
        #create blank list for the column
        cluster1 = []
        
        #output progress
        if progress:
            print(f'{counter+1}/{lendf}')
        
        #For every column cycle again through every column
        for counter2, row2 in enumerate(df[seq_col_name]):
            
            #for elements on the diagonal distance is set to zero
            if counter == counter2:
                d = 0
                
            #for the upper triangle of the matrix calculate the distance
            #between the sequences
            elif counter2 > counter:
                seq=difflib.SequenceMatcher(None, row,row2)
                d= 100 - seq.ratio()*100
                
            #for the lower triangle fill in the distances using the 
            #upper triangle
            else:
                d = clusters[counter2][counter]
                
            #add the distance to the list of distances for the column
            cluster1.append(d)
        
        #add list of column distances to the list of columns
        clusters.append(cluster1)
        
    return(clusters, URIs)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def clustering(z, URIs, cutoff = 80):
    """Takes in a linkage array and returns a table with clusters over
    a specified cutoff.
    
    Requires
    ---------
    Pandas
    
    Parameters
    -----------
    z : numpy array (4*n)
        The linkage array generated by cluster.hierarchy.linkage
        
    URIs: numpy array (1*n+1)
        An array containing the names of the original nodes
        
    cutoff : int, default:80
        Only show clusters where the maximum distance to the centroid is 
        <100-cutoff, i.e. the similarity of the sequences to the centroid
        is >= cutoff.
        

    Returns
    --------
    df_clustered : Pandas df (6*m)
        Returns a pandas data frame witht the columns:
        ['clustnum', 'height', 'similarity', 'node_index','node_uri', 'numnodes']
        Clustnum indicates the index of the cluster, height the distance
        apart the last two centroids joined were, similarity the similarity
        of the last two centroids, node_index is the index of each of the 
        nodes in the cluster,node_uri is the names of the nodes contained
        in the cluster, and numnodes is the number of nodes contained in the
        cluster

    Example
    --------
    cutoff = 90
    out_path = '"C:\\Users\\Test\\Documents\\"
    SeqCol = 'Sequence'
    URICol = 'URI'
    
    distance_matrix, URIs = seqdist(df, SeqCol, URICol)
    
    square_form = spatial.distance.squareform(distance_matrix)
    
    z = cluster.hierarchy.linkage(square_form, method='centroid')
    
    df_clustered = clustering(z, cutoff)
    
    print(df_clustered[['similarity','node_uri']])
    """
    
    
    #convert linkage to pandas DataFrame
    #dftree has columns: 0:cluster one, 1:cluster 2, 2:Distance between Clusters,
    #3:Number of points in the cluster. dftree is sorted on column from smallest
    # distance to greatest distance
    dftree = pd.DataFrame(z, columns=['point1','point2','dist','num_points'])
    
    
    """Add a column to dftree with the names of the new clusters being created"""
    #indicates how many clusters were originally present (all original clusters
    #are singeltons)
    points = len(z) + 1
    
    #creates a list of all the new clusters created
    cluck = list(range(points, points+len(z)))
    
    #Makes the new list of clusters the index for dftree
    dftree.index = cluck
    
    #create column with list of column 0 and 1
    dftree['list'] = dftree.apply(lambda row: [row[0], row[1]], axis=1)
    
    """Create Clustered URIs"""
    #removes all rows creating clusters of a distance greater than the cutoff
    #as distance is 100-similarity and the cutoff is for similarity 100-cutoff is
    #used.
    dftree2 = dftree.query('dist<(100 - @cutoff)')
    
    #create a dictionary with cluster name as key and points clustered as values
    dc2 = dftree2.to_dict(orient = 'series')['list']
        
    """Create flattened dictionary"""
    #for every key value pair in dc2
    for key, i in dc2.items():
        #temporary list initiated
        temp = []
        
        #if cluster1 is not original single cluster
        if i[0]>=points:
            temp += dc2[i[0]] #add sub cluster to temp list
            del dc2[i[0]] #delete the subcluster from the list
        else:
            temp += [i[0]] #if original singelton there is no subcluster so just
                           #add the singelton to the temp list
        
        #if cluster2 is not original single cluster
        if i[1]>=points: 
            temp += dc2[i[1]] #add the sub cluster to temp list
            del dc2[i[1]] #dlete the subcluster from the list
        else:
            temp += [i[1]] #if original singelton there is no subcluster so just
                           #add the singelton to the temp list
        dc2[key] = temp #replace cluster pair with flattened cluster list
        
    """Add names to dict"""
    df_clustered = []  # define new element
    for key, value in dc2.items():
        height = dftree2['dist'].loc[key] #height is found using the clustnum
        sim = 100-height # similarity is 100- height
       
        Unode = []
        for j in value:
            Unode.append(URIs[int(j)]) #go through and find singelton names
                                       #based on their clustnum
        
        df_clustered.append([key, height, sim, value, Unode, len(Unode)])  #add row to dfrows
    
    #create a pandas df with the information
    df_clustered = pd.DataFrame(df_clustered, columns=['clustnum','height', 'similarity','node_index','node_uri','numnodes'])
    
    return(df_clustered)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  
def dendoclust(clustered_series, distance_matrix, URIs,
               out_path, cutoff = 80, method='complete', annotate = True):
    """Takes in a subset of clustered point based on a cutoff and returns
    a dendogram of how the nodes in those clusters cluster.
    
    Requires
    ---------
    import matplotlib.pyplot as plt
    import pandas as pd
    from scipy import spatial, cluster
    
    Parameters
    -----------
    clustered_series: pandas series
        Series containing lists of indices which grouped in clusters
        Can be generated using the function: clustering
        
    distance_matrix: list of lists (n*n)
        Returns a symmetrical pairwise distance matrix where
        clusters[0][1] = clusters[1][0] = distance between sequence 0 
        and sequence 1 (note p<=n as NaN and possibly duplicate values
        are dropped)
        
    URIs: numpy array (1*n+1)
        An array containing the names of the original nodes whose pairwise
        distance is recoreded in distance_matrix
        
    out_path: str
        A filepath indicating the folder where the output jpeg will be stored
       
    cutoff : int, default:80
        Only show clusters where the maximum distance to the centroid is 
        <100-cutoff, i.e. the similarity of the sequences to the centroid
        is >= cutoff.
        
 
    method: str, default:'complete'
        Methods used for clustering. Default is farthest point method
        For more methods see:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html
        
    annotate: boolean, default:True
        Whether or not to annotate the dendogram with similarities at all
        point where nodes are joined
        

    Returns
    --------
    Nothing is returned. The image Dendo.jpg is saved in the folder specified
    by out_path

    Example
    --------
    method = 'centroid'
    cutoff = 90
    out_path = '"C:\\Users\\Test\\Documents\\"
    SeqCol = 'Sequence'
    URICol = 'URI'
    
    distance_matrix, URIs = seqdist(df, SeqCol, URICol)
    
    square_form = spatial.distance.squareform(distance_matrix)

    z = cluster.hierarchy.linkage(square_form, method= method)

    df_clustered = clustering(z, cutoff)
    
    clustered_series = df_clustered['node_index']
    
    dendoclust(clustered_series, distance_matrix, URIs,
               out_path, cutoff = cutoff, method=method, annotate = True)
    """

    
    #Create and Array of all clustered point with a similarity greater
    #than the cutoff
    clustered_ind = []
    for point_list in clustered_series:
        clustered_ind += point_list
    
    #Subset the distance matrix to create a pairwise distance matrix
    #only for the points that clustered below the cutoff similarity
    reduced_distance_matrix = pd.DataFrame(distance_matrix) #distance matrix to pd data frame
    reduced_distance_matrix = reduced_distance_matrix.loc[clustered_ind,clustered_ind] #drop all non clustered items
    
    #change distance matrix to the correct form
    reduced_squareform = spatial.distance.squareform(reduced_distance_matrix)
    
    #complete linkage analysis
    linkage_array = cluster.hierarchy.linkage(reduced_squareform, method=method)
    
    #subset node labels (and reset the index to correspond to the reduced
    #distance matrix)
    labels = URIs[clustered_ind].reset_index(drop=True).values
    
    #Create the figure
    plt.figure(figsize=(90,30))
    dendo = cluster.hierarchy.dendrogram(
            linkage_array,
            color_threshold = 100-cutoff, #will color clusters individually below the threshold
            labels = labels,
            leaf_font_size=20,
            leaf_rotation=90) #node labels read from bottom to top
    
    #annotate with similarities where nodes join
    if annotate:
        for i, d, c in zip(dendo['icoord'], dendo['dcoord'], dendo['color_list']):
            x = 0.5 * sum(i[1:3]) #find the halfway point of the u drawn
            y = d[1] #find the height of the u drawn
            if y <= 100 - cutoff: #add labels if similarity is >= cutoff
                plt.plot(x, y, 'o', c=c) #add point in the colour of the u
                text = 100-y #text is similarity
                plt.annotate("%.3g" %text, (x, y), #format text for location x,y
                             xytext=(2, 25), #offset for the text
                             fontsize = 20,
                             textcoords='offset points',
                             va='top',
                             ha='left') #point left of text
    
    #only show dendrogram plot upto the cutoff point
    plt.ylim([0,100-cutoff])
    
    #relabel y with similarity rather than distance
    locs, labels = plt.yticks()
    ylabels = []
    for i in locs:
        ylabels += [100-i]
    plt.yticks(ticks =locs, labels = ylabels, size = 20)
    
    #Add y axis label
    plt.ylabel("Similarity", size=30)
    
    #save the figure
    plt.savefig(f'{out_path}Dendo.jpg', bbox_inches='tight')
    
    plt.close()
    
    return()
    
#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
def cluster_routine(df, seq_col_name, uri_col_name, out_path, cutoff = 80,
                    method='complete'):
    """Takes in a dataframe with a bunch of sequences and creates a 
    labelled dendrogram of clusters based on the cutoff.
    
    Requires
    ---------
    import pandas as pd
    from scipy import spatial, cluster
    seqdist, clustering, dendoclust
    
    Parameters
    -----------
    df : Pandas dataframe (m*n)
        Contains at least one column with str formatted sequence data
        and one column with str formatted names for the sequence data
        
    seq_col_name : str 
        Name of the column in df containing the str formatted sequence data
        
    uri_col_name : str 
        Name of the column in df containing the str formatted sequence names
        
    out_path: str
        A filepath indicating the folder where the output jpeg will be stored
       
    cutoff : int, default:80
        Only show clusters where the maximum distance to the centroid is 
        <100-cutoff, i.e. the similarity of the sequences to the centroid
        is >= cutoff.
        
    method: str, default:'complete'
        Methods used for clustering. Default is farthest point method
        For more methods see:
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html
        

    Returns
    --------
    Nothing is returned. The image Dendo.jpg is saved in the folder specified
    by out_path

    Example
    --------
    out_path = '"C:\\Users\\Test\\Documents\\"
    data = {'Names':['RBS', '1887', 'RibosomeBindingSite', 'RibosomeEntrySite','Barcode187'],
            'Sequence':['atgcaaa', 'tgcccga', 'atgcaat', 'ccatctgc', 'aagggggcg']} 
  
    # Create DataFrame 
    df = pd.DataFrame(data) 
  
    cluster_routine(df, 'Sequence', 'Names', out_path, cutoff = 90,
                    method='centroid')
    """
    
    """Create Distance Matrix"""
    distance_matrix, URIs = seqdist(df, seq_col_name, uri_col_name)
    
    """Cluster Points"""
    #convert clusters to correct form for linkage
    square_form = spatial.distance.squareform(distance_matrix)
    
    #Create linkag
    z = cluster.hierarchy.linkage(square_form, method= method)
    
    """Create table of groups""" 
    df_clustered = clustering(z, URIs, cutoff)
    
    #Output table
    df_clustered[['similarity','node_uri']].to_csv(f'{out_path}Clust.csv',index=False)
    
    """Dendogram"""
    clustered_series = df_clustered['node_index']
    
    dendoclust(clustered_series, distance_matrix, URIs,
                   out_path, cutoff, method=method, annotate = True)
    
    return()

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""Set Values"""
import os
cwd = os.getcwd() #get current working directory

#name of the column containing sequences
SeqCol = 'Sequence'

#name of the column contianing URIs/sequence names
URICol = 'Part Name'

#cutoff for sequence similarity (e.g. only group sequences with a
#similarity >= cutoff value)
cutoff = 80

#input file data path
in_path = f'{cwd}\\voigt_terminator_dendogram\\voigt_terminators_v002.csv'

#out file data path
out_path = f'{cwd}\\voigt_terminator_dendogram\\'

#method of clustering to use
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html#scipy.cluster.hierarchy.linkage )
method = 'complete' #farthest point clustering method

"""Run"""
#import dataframe
df_all = pd.read_csv(in_path)

# #Read in the minimum lengths to use for each part type
# role_names = pd.read_csv(f'{cwd}\\Min_Len\\Min_Len.csv', index_col = 0)
# #create a dictionary
# role_names = role_names.to_dict()

# df_all1 = df_all[df_all['U_Basic_Min_Len'] == True]

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
"""

 'http://identifiers.org/so/SO:0000340': 'Chromosome',
 'http://identifiers.org/so/SO:0000316': 'CDS',
 'http://identifiers.org/so/SO:0000110': 'Sequence feature',
  'http://identifiers.org/so/SO:0000804': 'Engineered Region',
   'http://identifiers.org/so/SO:0000167': 'Promoter',

"""


# role_name = 'Primer'
# df = df_all1[df_all1['Role_Name']== role_name]

cluster_routine(df_all, SeqCol, URICol,
                out_path = f'{out_path}_BasicUnique_Voigtterminators.jpg',
                cutoff = cutoff, method=method)



#for role_name in role_names['Role_Name'].values():
#    df = df_all[df_all['Role_Name']== role_name]
#    
#    cluster_routine(df, SeqCol, URICol,
#                    out_path = f'{out_path}{role_name}_',
#                    cutoff = cutoff, method=method)

