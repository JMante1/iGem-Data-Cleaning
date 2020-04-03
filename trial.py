# -*- coding: utf-8 -*-
"""
Created on Mon Mar 16 12:47:14 2020

@author: JVM
"""

import pandas as pd

df = pd.read_csv("C:\\Users\\JVM\\Downloads\\Book1.csv")
df1 = df.sort_values('equal')
df2 = df1.drop_duplicates(['uri'],keep='first')


print(df2)