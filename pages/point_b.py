import streamlit as st
from utils.system import System

st.title("🎯 K-out-of-N System Optimization")

st.header("System Parameters")
failure_rate = st.number_input("Failure Rate (λ)", value=0.1, min_value=0.0)
repair_rate = st.number_input("Repair Rate (μ)", value=0.5, min_value=0.0)
cold_standby = st.selectbox("Cold Standby?", ["Yes", "No"]) == "Yes"
k = st.number_input("Minimum Working Components (k)", min_value=1, value=3)
repairmen = st.number_input("Number of Repairmen", min_value=1, value=2)

st.header("Cost Parameters for Optimization")

comp_cost = st.number_input("Component Cost", value=10.0, min_value=0.0)
repair_cost = st.number_input("Repairman Cost", value=50.0, min_value=0.0)
downtime_cost = st.number_input("Downtime Cost", value=100.0, min_value=0.0)

max_n = st.slider("Max Number of Components (n)", k, 3*k, value=2*k)
max_r = st.slider("Max Repairmen", 1, 3*k, value=k)

if st.button("Find Optimal Configuration"):
    sys = System(max_n,k,repairmen,failure_rate, repair_rate, cold_standby)
    result = sys.optimize()
    if result:
        st.subheader("🧠 Optimal Configuration")
        st.write(f"**Components**: {result['components']}")
        st.write(f"**Repairmen**: {result['repairmen']}")
        st.write(f"**Availability**: {result['availability']:.4f}")
        st.write(f"**Total Cost**: {result['total_cost']:.2f}")
    else:
        st.error("No configuration found.")