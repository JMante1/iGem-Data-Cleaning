import os, sbol2
import pandas as pd

cwd = os.getcwd()
sbol_file_names = os.listdir(os.path.join(cwd, 'subpartcheck', 'SBOL'))

an_sequences = set()
an_dict = {}
for ind, file in enumerate(sbol_file_names):
    if ind > -1:
        doc = sbol2.Document()
        doc.read(os.path.join(cwd, 'subpartcheck', 'SBOL', file))
        annotation_ranges = []
        for seq in doc.sequences:
            seq_atgc = seq.elements
            len_seq = len(seq.elements)
        for defin in doc.componentDefinitions:
            for an in defin.sequenceAnnotations:
                for loc in an.locations:
                    an_seq = seq_atgc[loc.start-1:loc.end-1]
                    percent_cover = '{:.2f}'.format(len(an_seq)/ (len_seq-1))
                    # if an_seq == 'ttgtttaactttaagaagga':
                    #     print(file)
                    if len(an_seq)< len_seq-1:
                        if an_seq in an_dict:
                            an_dict[an_seq]['count'] +=1
                            an_dict[an_seq]['percent_cover'].append(percent_cover)
                        else:
                            an_sequences.add(an_seq)
                            an_dict[an_seq] = {'an_name':an.name, 'an_len':len(an_seq), 'count':1, 'percent_cover':[percent_cover]}
print (an_sequences)
print(an_dict)
df = pd.DataFrame.from_dict(an_dict, orient='index')
# df.to_excel(os.path.join(cwd, 'subparts_set.xlsx'))
