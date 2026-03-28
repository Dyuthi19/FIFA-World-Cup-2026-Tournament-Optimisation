#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 3 23:29:02 2026

@author: dyuthibopparaju
"""

import pandas as pd
from pyomo.environ import *

file_name = "fifa_data.xlsx"

fifa_teams = pd.read_excel(file_name, sheet_name="Teams", header=1)
stadium_assignment = pd.read_excel(file_name, sheet_name="Group Formation(Table-4)",header=None)

spectator_index_dict = (fifa_teams.set_index("Participating Nation")["Spectator Index"].to_dict())

optimal_df = stadium_assignment.iloc[4:16, 3:8]
optimal_groups_dict = {int(row.iloc[0]): row.iloc[1:5].tolist() for _, row in optimal_df.iterrows()}

match_index = [(0,1),(2,3),(0,2),(1,3),(0,3),(1,2)]

match_popularity = {}

for subset, group in optimal_groups_dict.items():

    group_match_scores = []

    for (i1, i2) in match_index:

        team1 = group[i1]
        team2 = group[i2]

      
        f1 = spectator_index_dict.get(team1, 0)
        f2 = spectator_index_dict.get(team2, 0)

        
        f_other = (f1 + f2) / 2

        
        if max(f1, f2) == 1:
            f_officials = 1
        else:
            f_officials = (f1 + f2) / 2

     
        p = f1 + f2 + f_other + f_officials

        group_match_scores.append(round(p,2))

    match_popularity[subset] = group_match_scores


print("\nmatch_popularity = {")

for g, scores in match_popularity.items():
    print(f"    {g-1}: {scores},")
print("}")
