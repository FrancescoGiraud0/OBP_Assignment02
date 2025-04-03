---
Authors: Giraudo Francesco (2852527) & Viet Hang Tran (2838944)
Exam: Optimization of Business Processes
Type: Assignment 2
Note: Project description
---

> [!NOTE] Open this with Obsidian for better viewing.
> 

# Assignment 02 OBP

## Requirements

Write a python program with an online streamlit interface that calculates the stationary distribution of a k-out-of-n maintenance system.

Life times and repair times are exponential.

a. Calculate the fraction of time the system is up based on the following input:

- failure rate (of components)
- repair rate
- whether components that are not used are in warm or cold stand-by (yes/no)
- number of components
- number of components for the system to function
- number of repairmen

b. Find the optimal number of components and repairmen using the following additional input (all per unit of time): 

- cost per component
- cost per repairman
- downtime costs

## Grading

- start with 1
- a 6 (correct b-d process 2, correct algorithm 2, correct outcome 2)  
- b 3 (method 2, correct outcome 1)

## Project structure

- pages >
  - point_a.py : Code for point a page visualization
  - point_b.py : Code for point b page visualization
- utils >
  - system.py : Code for definition of the maintenance system class
  - test1.py : Code for testing system.py,  only for point a requirements
- app.py :  Code for main app to run

## References

Streamlit API reference -> <https://docs.streamlit.io/>

Streamlit example app Github repository (for trying it > streamlit hello) -> <https://github.com/streamlit/hello/tree/main> ^d35fe8