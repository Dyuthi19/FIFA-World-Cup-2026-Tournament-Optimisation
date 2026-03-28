#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 11:33:32 2026

@author: dyuthibopparaju
"""

from pyomo.environ import *
import pandas as pd

file_name = "fifa_data.xlsx"
stadiums = pd.read_excel(file_name, sheet_name="Stadiums", header=1)


stadiums_2026 = stadiums[stadiums["Year"] == 2026]

stadium_names = stadiums_2026["Stadium"].tolist()
capacities = stadiums_2026["Capacity"].tolist()
countries = stadiums_2026["Country"].tolist()

canada_stadiums = [i for i, c in enumerate(countries) if c == 'Canada']
mexico_stadiums = [i for i, c in enumerate(countries) if c == 'Mexico']
usa_stadiums = [i for i, c in enumerate(countries) if c == 'USA']

can_rows = [0, 1]    # Contains matches B1/2, B1/3, B1/4
mex_rows = [2, 3]    # Contains matches A1/2, A1/3, A1/4
usa_rows = [11, 15]  # Contains matches D1/2, D1/3, D1/4

# Row-set popularity values calculated from 03_group_letter_assignment.py
yr = [
    17.16, 15.03, 12.28, 10.67,
    10.95, 17.88, 16.83, 20.00,
    16.74, 20.00, 15.24, 17.72,
    16.00, 18.56, 16.82, 14.46
]

numofstadiums = stadiums_2026.shape[0]
numofrowsets = len(yr)

model = ConcreteModel()

# Decision variables
model.xij = Var(range(numofrowsets), range(numofstadiums), domain=Binary)

# Objective
model.objective = Objective(
    expr=sum(yr[i] * capacities[j] * model.xij[i, j]
             for i in range(numofrowsets)
             for j in range(numofstadiums)),
    sense=maximize
)

# Each row-set assigned to exactly one stadium
def rowset_stadium_rule(model, i):
    return sum(model.xij[i, j] for j in range(numofstadiums)) == 1

model.rowset = Constraint(range(numofrowsets), rule=rowset_stadium_rule)

# Each stadium assigned exactly one row-set
def stadium_rowset_rule(model, j):
    return sum(model.xij[i, j] for i in range(numofrowsets)) == 1

model.stadium = Constraint(range(numofstadiums), rule=stadium_rowset_rule)

# Canada row-sets → Canada stadiums
def canada_stadiums_rule(model, r):
    return sum(model.xij[r, s] for s in canada_stadiums) == 1

model.host_can = Constraint(can_rows, rule=canada_stadiums_rule)

# Mexico row-sets → Mexico stadiums
def mexico_stadiums_rule(model, r):
    return sum(model.xij[r, s] for s in mexico_stadiums) == 1

model.host_mex = Constraint(mex_rows, rule=mexico_stadiums_rule)

# USA row-sets → USA stadiums
def usa_stadiums_rule(model, r):
    return sum(model.xij[r, s] for s in usa_stadiums) == 1

model.host_usa = Constraint(usa_rows, rule=usa_stadiums_rule)


solver = SolverFactory('glpk')
results = solver.solve(model, tee=False)


print(f"\nMaximum Total Popularity Value: {value(model.objective):.2f}\n")

print("Optimal Stadium Assignments:")

for i in range(numofrowsets):
    for j in range(numofstadiums):
        if value(model.xij[i, j]) > 0.5:
            print(f"Row-set {i} (Popularity: {yr[i]:.2f}) → {stadium_names[j]} (Capacity: {capacities[j]})")