import streamlit as st
from utils.system import System

st.set_page_config(
        page_title="K-out-of-N Maintenance",
        page_icon="🔧",
    )

st.title("🔧 K-out-of-N Maintenance System Availability & Optimization")

st.markdown(
        """
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
        """
    )

st.sidebar.success("Select the modality above.")
