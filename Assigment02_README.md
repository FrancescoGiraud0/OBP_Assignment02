---
Authors: Giraudo Francesco (2852527) & Viet Hang Tran (2838944)
Exam: Optimization of Business Processes
Type: Assignment 2
Note: Project description
---
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

My idea is creating two python classes (one per exercise) in order to define the system (parameters and related functions). We can create a  [python class](https://www.w3schools.com/python/python_classes.asp) object for defining and solving the system for point a, then we can use [class inheritance](https://www.w3schools.com/python/python_inheritance.asp)  to define and solving the system in point b. After testing these, we can create the respective streamlit pages, we can see the Hello Example App [[Assigment02_README#^d35fe8]]

- pages >
  - PointA.py : Code for point a page visualization
  - PointB.py : Code for point b page visualization
- utils >
  - system.py : Code for definition of the maintenance system (possibly using Object Oriented approach)
  - test1.py : Code for testing system.py / utils.py for solving point a requirements
  - test2.py : Code for testing system.py / utils.py for solving point b requirements
- app.py :  Code for main app to run

## References

Streamlit API reference -> <https://docs.streamlit.io/>

Streamlit example app Github repository (try it > streamlit hello) -> <https://github.com/streamlit/hello/tree/main> ^d35fe8
