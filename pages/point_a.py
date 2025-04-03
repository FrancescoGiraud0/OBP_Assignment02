import streamlit as st
from utils.system import System

st.title("🔧 K-out-of-N System Availability")

st.header("System Parameters")
failure_rate = st.number_input("Failure Rate (λ)", value=0.1, min_value=0.0)
repair_rate = st.number_input("Repair Rate (μ)", value=0.5, min_value=0.0)
cold_standby = st.selectbox("Cold Standby?", ["Yes", "No"]) == "Yes"
n = st.number_input("Number of Components (n)", min_value=1, value=5)
k = st.number_input("Minimum Working Components (k)", min_value=1, value=3)
repairmen = st.number_input("Number of Repairmen", min_value=1, value=2)

if st.button("Calculate Availability"):
    sys = System(n,k,repairmen,failure_rate, repair_rate, cold_standby)
    availability = sys.active_time_fraction()
    st.success(f"System Availability (Fraction of time UP): {availability:.4f}")