# ⚽ FIFA World Cup 2026 Optimisation Project

## 📌 Overview
This project develops an optimisation framework for planning the FIFA World Cup 2026, focusing on:
- Balanced group formation  
- Optimal group letter assignment  
- Efficient stadium allocation  

The approach integrates real-world data with optimisation models based on Ghoniem et al. (2017) to improve competitive balance, spectator engagement, and stadium utilisation.

---

## 🎯 Objectives
- Ensure fair distribution of team strength across groups  
- Distribute high-profile matches evenly  
- Assign matches to stadiums to maximise spectator value  

---

## ⚙️ Models Implemented

### 1. Group Formation Model
- Integer Programming (Pyomo)
- Objective: Maximise minimum group strength (Chebyshev objective)
- Constraints:
  - 4 teams per group  
  - One team per pot  
  - Confederation restrictions  
  - Host nation pre-assignment  

---

### 2. Group Letter Assignment Model
- Assigns groups to letters (A–L)
- Uses:
  - Match schedule structure  
  - Spectator index  
- Objective:
  - Maximise (w_min + w_max)  
- Ensures balanced match popularity distribution  

---

### 3. Stadium Assignment Model
- Assignment optimisation model  
- Objective:  

  max ∑r ∑s (y_r × Capacity_s × x_rs)

- Matches high-demand games to large stadiums  
- Includes host-country constraints  

---

## 📊 Data Sources
- FIFA rankings (2026)  
- Match attendance (Kaggle dataset)  
- GDP per capita (World Bank, 2024 data)  
- Stadium capacities:
  - 2026: US National Soccer Players  
  - 2022: Statista  

---

## 📈 Key Results
- Balanced groups (spread ≈ 51.85 points)  
- Row-set popularity range: 10.67 – 20.00  
- Improved stadium utilisation  
- High-demand matches assigned to high-capacity stadiums  

---

## 🔄 Key Modifications (2026 Format)
- Teams increased: 32 → 48  
- Groups increased: 8 → 12  
- Stadiums increased: 12 → 16  
- Introduced tri-host constraints (USA, Canada, Mexico)  

---

## 🛠️ Tools & Technologies
- Python  
- Pyomo  
- GLPK Solver  
- Pandas, NumPy  
- Excel  

---

## ▶️ How to Run

Install dependencies:
```bash
pip install pyomo pandas numpy
