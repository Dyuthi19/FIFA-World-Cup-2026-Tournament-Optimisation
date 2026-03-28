#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 10:50:55 2026

@author: dyuthibopparaju
"""
from pyomo.environ import *
import pandas as pd

file_name = "fifa_data.xlsx"
stadiums = pd.read_excel(file_name, sheet_name="Stadiums",header=1)
stadiums_2026 = stadiums[stadiums["Year"] == 2026]

# Match popularities calculated from 02_match_poopularity_calculation.py
match_popularity = {
    0: [4.0, 1.11, 3.17, 2.67, 2.67, 3.17],
    1: [4.0, 1.97, 3.61, 2.87, 2.87, 3.61],
    2: [4.0, 2.85, 4.0, 2.85, 2.85, 4.0],
    3: [4.0, 2.85, 2.85, 4.0, 4.0, 2.85],
    4: [4.0, 3.35, 4.0, 3.35, 3.35, 4.0],
    5: [4.0, 3.89, 4.0, 3.89, 3.89, 4.0],
    6: [4.0, 2.81, 4.0, 2.81, 2.81, 4.0],
    7: [4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
    8: [4.0, 2.58, 4.0, 2.58, 2.58, 4.0],
    9: [4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
    10: [4.0, 4.0, 4.0, 4.0, 4.0, 4.0],
    11: [4.0, 3.21, 3.21, 4.0, 4.0, 3.21],
}

numofsubsets = len(match_popularity)  
numofletters = len(match_popularity)    
numofstadiums = stadiums_2026.shape[0] 

# The 2026 Schedule Template (J_r) maps 16 stadiums to tuples of (group_letter_index, match_index)
# group_letter_index: A=0, B=1, C=2, D=3, E=4, F=5, G=6, H=7, I=8, J=9, K=10, L=11
# match_index: 1/2=0, 3/4=1, 1/3=2, 2/4=3, 1/4=4, 2/3=5

matches_in_row = {
    0: [(1,0), (11,1), (4,2), (11,3), (8,5)],      # Toronto
    1: [(3,1), (1,2), (6,3), (1,4), (6,4)],        # Vancouver
    2: [(0,1), (0,2), (10,3), (7,4)],              # Guadalajara
    3: [(0,0), (10,1), (0,4)],                     # Mexico City
    4: [(5,1), (5,3), (0,5)],                      # Monterrey
    5: [(7,0), (0,3), (7,2), (2,5), (10,5)],       # Atlanta
    6: [(2,1), (8,1), (2,3), (11,2), (8,4)],       # Boston
    7: [(5,0), (11,0), (9,2), (5,5), (9,4)],       # Dallas
    8: [(2,0), (8,0), (8,3), (4,4), (11,4)],       # New York / New Jersey
    9: [(4,0), (10,0), (5,2), (10,2), (7,5)],      # Houston
    10: [(9,0), (4,3), (5,4), (9,5)],              # Kansas City
    11: [(3,0), (6,1), (1,3), (6,2), (3,4)],       # Los Angeles
    12: [(7,1), (7,3), (2,4), (10,4)],             # Miami
    13: [(4,1), (2,2), (8,2), (4,5), (11,5)],      # Philadelphia
    14: [(1,1), (9,1), (3,3), (9,3), (3,5)],       # San Francisco
    15: [(6,0), (3,2), (1,5), (6,5)]               # Seattle
}

model = ConcreteModel()


# Decision Variables
# zgl[g, l] = 1 if subset g is assigned to group letter l
model.zgl = Var(range(numofsubsets), range(numofletters), domain=Binary)

# vr[r] = binary switch variable for calculating the maximum row-set popularity
model.vr = Var(range(numofstadiums), domain=Binary)

# Row-set popularity variables
model.yr = Var(range(numofstadiums), domain=NonNegativeReals)
model.wmin = Var(domain=NonNegativeReals)
model.wmax = Var(domain=NonNegativeReals)

# Objective Function
# (2a) Maximize the sum of the minimum and maximum row-set popularity
model.obj = Objective(expr=model.wmin + model.wmax, sense=maximize)

# Constraints 

# (2b & 2c) wmin and wmax bounding constraints
model.wmin_bound = Constraint(range(numofstadiums), rule=lambda m, r: m.wmin <= m.yr[r])
model.wmax_bound1 = Constraint(range(numofstadiums), rule=lambda m, r: m.wmax >= m.yr[r])

# (2d & 2e) Big-M formulation to lock in wmax
model.vr_sum = Constraint(expr=sum(model.vr[r] for r in range(numofstadiums)) == 1)

model.wmax_bound2 = Constraint(range(numofstadiums), rule=lambda m, r: m.wmax <= m.yr[r] + 20 * (1 - m.vr[r]))

# (2f) Calculate Row-Set Popularity (y_r)
def yr_rule(m, r):
    return m.yr[r] == sum(match_popularity[g][match_idx] * m.zgl[g, l] 
                         for (l, match_idx) in matches_in_row[r] 
                         for g in range(numofsubsets))
model.calc_popularity = Constraint(range(numofstadiums), rule=yr_rule)

# (2g & 2h) Assignment: Each subset gets exactly 1 letter, and each letter gets exactly 1 subset
model.assign_g = Constraint(range(numofsubsets), rule=lambda m, g: sum(m.zgl[g, l] for l in range(numofletters)) == 1)
model.assign_l = Constraint(range(numofletters), rule=lambda m, l: sum(m.zgl[g, l] for g in range(numofsubsets)) == 1)

# (2i) Host Pre-assignments
model.hostA = Constraint(expr=model.zgl[0, 0] == 1) # Subset 0 (Mexico) to Group A
model.hostB = Constraint(expr=model.zgl[1, 1] == 1) # Subset 1 (Canada) to Group B
model.hostD = Constraint(expr=model.zgl[3, 3] == 1) # Subset 3 (USA) to Group D


solver = SolverFactory('glpk') 
results = solver.solve(model, tee=False)

print(f"\nObjective Value (wmin + wmax): {value(model.obj):.2f}")
print(f"Minimum Row-Set Popularity: {value(model.wmin):.2f}")
print(f"Maximum Row-Set Popularity: {value(model.wmax):.2f}\n")

print("Group Letter Assignments:")
letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L']
for g in range(numofsubsets):
    for l in range(numofletters):
        if value(model.zgl[g, l]) > 0.5:
            print(f"Subset {g} is assigned to Group {letters[l]}")

print("\nRow-Set (Stadium) Popularities (y_r):")
for r in range(numofstadiums):
    print(f"Row-set {r}: {value(model.yr[r]):.2f}")