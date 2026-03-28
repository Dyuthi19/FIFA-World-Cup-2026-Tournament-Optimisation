#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 24 15:49:06 2026

@author: dyuthibopparaju
"""

import numpy as np
import pandas as pd
from pyomo.environ import *

file_name = "fifa_data.xlsx"

# Read and sort data
fifa_teams = pd.read_excel(file_name, "Teams", header = 1)
fifa_teams = fifa_teams.sort_values(by="FIFA Points", ascending=False).reset_index(drop=True)

# Parameters
teams = fifa_teams["Participating Nation"].tolist()
N = len(teams)
pi = pd.to_numeric(fifa_teams["FIFA Points"], errors='coerce').to_numpy()
ci = fifa_teams["Confederation"].to_numpy()
num_pots = 4
G = 12

hosts = ["Canada", "United States", "Mexico"]

# Top 9 non-host teams
top_teams = [t for t in teams if t not in hosts][:9]
pot1_teams = hosts + top_teams

# Remaining teams
remaining = [t for t in teams if t not in pot1_teams]
pot2_teams = remaining[:12]
pot3_teams = remaining[12:24]
pot4_teams = remaining[24:36]

pot_dict = {
    0: pot1_teams,
    1: pot2_teams,
    2: pot3_teams,
    3: pot4_teams
}


model = ConcreteModel()

# Decision Variables
model.xig = Var(range(N), range(G), domain=Binary)
model.w = Var(domain=NonNegativeReals)

# Objective Function
model.objective = Objective(expr=model.w, sense=maximize)

# Constraints
def w_points(model, j):
    return sum(model.xig[i,j]*pi[i] for i in range(N)) >= model.w 
model.wpoints_const = Constraint(range(G), rule=w_points)

def group_size(model, j):
    return sum(model.xig[i,j] for i in range(N)) == 4
model.groupsize_const = Constraint(range(G), rule=group_size)

def single_assignment(model, i):
    return sum(model.xig[i,j] for j in range(G)) == 1
model.singleassignment_const = Constraint(range(N), rule=single_assignment)

# Updated Pot Rule using the corrected dictionaries
def pot_rule(model, j, k):
    indices = [i for i in range(N) if teams[i] in pot_dict[k]]
    return sum(model.xig[i, j] for i in indices) <= 1
model.potrule_const = Constraint(range(G), range(num_pots), rule=pot_rule)

unique_confederations = np.unique(ci)

def confederation_rule(model, j, confed):
    indices = [i for i in range(N) if ci[i] == confed]
    if confed == "UEFA":
        return sum(model.xig[i, j] for i in indices) <= 2
    else:
        return sum(model.xig[i, j] for i in indices) <= 1
model.confed_constraint = Constraint(range(G), unique_confederations, rule=confederation_rule)

# Fix assignments for hosts
mexico_index = teams.index("Mexico")
canada_index = teams.index("Canada")
usa_index = teams.index("United States")

model.xig[mexico_index, 0].fix(1)   # Group A (0)
model.xig[canada_index, 1].fix(1)   # Group B (1)
model.xig[usa_index, 3].fix(1)      # Group D (3)

# ==============================
# SOLVE
# ==============================
from pyomo.opt import TerminationCondition

solver = SolverFactory('glpk')
solver.options['tmlim'] = 720   # 12 minutes

results = solver.solve(model, tee=False)

if results.solver.termination_condition in [
        TerminationCondition.optimal,
        TerminationCondition.maxTimeLimit,
        TerminationCondition.feasible]:
    model.solutions.load_from(results)
else:
    raise RuntimeError("Solver failed.")


print("\nBest Minimum Group Points (w):", round(value(model.w), 2))

group_totals = []

for j in range(G):
    print(f"\nGroup {j+1}:")
    print("-" * 55)
    print(f"{'Team Name':<25} | {'Confed':<10} | {'FIFA Points':>12}")
    print("-" * 55)
    
    members = []
    for i in range(N):
        if value(model.xig[i, j]) > 0.5:
            members.append((teams[i], pi[i], ci[i]))

    # Sort inside group: Hosts first, then by FIFA points (descending)
    members.sort(key=lambda x: (x[0] not in hosts, -x[1]))

    total = 0
    for team, pts, conf in members:
        print(f"{team:<25} | {conf:<10} | {pts:>12.2f}")
        total += pts

    group_totals.append(total)
    print("-" * 55)
    print(f"{'Total Points:':<38} | {total:>12.2f}")

print("\n" + "=" * 55)
print("SUMMARY")
print("=" * 55)
print(f"{'Max Group Points:':<38} | {max(group_totals):>12.2f}")
print(f"{'Min Group Points:':<38} | {min(group_totals):>12.2f}")
print(f"{'Spread:':<38} | {max(group_totals) - min(group_totals):>12.2f}")