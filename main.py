from data import drill_pipe_specifications
import calculations as calc
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Drill Pipe Tension Analyzer", layout="wide")
st.title("Drill Pipe Torque-Tension Limits Visualizer")
st.sidebar.header("Pipe Specifications")

# Pipe selection
selected_size = st.sidebar.selectbox(
    "Nominal Size [in]",
    options=list(drill_pipe_specifications.keys()),
    format_func=lambda x: drill_pipe_specifications[x]["label"]
    )

weights = list(drill_pipe_specifications[selected_size]["type"].keys())
selected_weight = st.sidebar.selectbox("Nominal Weight [lb/ft]", options=weights)
pipe_label = drill_pipe_specifications[selected_size]["label"]

# Safety Factor
sf_percent = st.sidebar.slider("Safety Factor [%]", 0, 90, step=5)

st.sidebar.header("Units Selection")
torque_unit = st.sidebar.radio("Torque Unit", ["kft-lb", "kNm"])
tension_unit = st.sidebar.radio("Tension Unit", ["klb", "mT"])

# Calculate button logic

if "calculated" not in st.session_state:
    st.session_state.calculated = False

current_params = f"{selected_size}-{selected_weight}-{sf_percent}-{torque_unit}-{tension_unit}"
if "last_params" not in st.session_state or st.session_state.last_params != current_params:
    st.session_state.calculated = False
    st.session_state.last_params = current_params

calc_button = st.sidebar.button(
    "Calculate", 
    on_click=lambda: st.session_state.update({"calculated": True}), 
    disabled=st.session_state.calculated
    )

# App logic

if calc_button or st.session_state.calculated:
    st.session_state.calculated = True
    
    wall = drill_pipe_specifications[selected_size]["type"][selected_weight]
    yield_psi = drill_pipe_specifications[selected_size]["yield"]
    
    # inner diameter calculation
    id_in = calc.calculate_internal_diameter(selected_size, wall)
    area_in2 = calc.calculate_cross_section_area(selected_size, id_in)
    inertia_in4 = calc.calculate_moment_of_inertia(selected_size, id_in)
    
    # generating data points for plot
    torsional_limit_ftlb = (yield_psi * 0.09167 * inertia_in4) / selected_size

    if torque_unit == "kft-lb":
        limit_display = torsional_limit_ftlb / 1000
    else: # kNm
        limit_display = torsional_limit_ftlb / 737.56

    torque_range = np.linspace(0, limit_display, 200)
    
    t_max_list = []
    t_sf_list = []
    
    for q in torque_range:
        # Convert params to base units (ft-lb)
        q_ftlb = q * 1000 if torque_unit == "kft-lb" else q * 737.56
        
        # calculating max tension
        tension_lb = calc.calculate_max_tension(area_in2, yield_psi, q_ftlb, selected_size, inertia_in4)
        
        # conversion to output unit
        if tension_unit == "klb":
            val = tension_lb / 1000
        else: # mT
            val = tension_lb * 0.00045359
            
        t_max_list.append(val)
        t_sf_list.append(val * (1 - sf_percent/100))

    st.success("Calculations up to date")

    # params visualization    
    c1, c2, c3 = st.columns(3)
    c1.metric("Cross section area", f"{area_in2:.3f} in²")
    c2.metric("Moment of inertia", f"{inertia_in4:.3f} in⁴")
    c3.metric("Drill pipe inside diameter", f"{id_in:.3f} in")

    # plot
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(torque_range, t_max_list, 'r-', label="Max Allowable Tension", linewidth=2)
    ax.plot(torque_range, t_sf_list, 'g--', label=f"Safe Tension ({sf_percent}%)", linewidth=2)
    
    ax.set_title(f"Torque-Tension Limit for {pipe_label} {selected_weight} lb/ft", fontsize=12)
    ax.set_xlabel(f"Torque [{torque_unit}]")
    ax.set_ylabel(f"Tension [{tension_unit}]")
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.legend()

    st.pyplot(fig)
else:
    st.info("Calculations NOT up to date.")