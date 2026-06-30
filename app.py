import streamlit as st
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

st.set_page_config(
    page_title="Home Alert App",
    page_icon="🏠",
    layout="wide"
)

# -----------------------------
# Fuzzy Systems
# -----------------------------
@st.cache_resource
def create_intrusion_system():
    movement = ctrl.Antecedent(np.arange(0, 101, 1), "movement")
    sound = ctrl.Antecedent(np.arange(0, 101, 1), "sound")
    light = ctrl.Antecedent(np.arange(0, 101, 1), "light")
    risk = ctrl.Consequent(np.arange(0, 101, 1), "intrusion_risk")

    movement["low"] = fuzz.trimf(movement.universe, [0, 0, 40])
    movement["medium"] = fuzz.trimf(movement.universe, [30, 50, 70])
    movement["high"] = fuzz.trimf(movement.universe, [60, 100, 100])

    sound["quiet"] = fuzz.trimf(sound.universe, [0, 0, 35])
    sound["normal"] = fuzz.trimf(sound.universe, [25, 50, 70])
    sound["loud"] = fuzz.trimf(sound.universe, [60, 100, 100])

    light["low"] = fuzz.trimf(light.universe, [0, 0, 40])
    light["medium"] = fuzz.trimf(light.universe, [30, 50, 70])
    light["high"] = fuzz.trimf(light.universe, [60, 100, 100])

    risk["safe"] = fuzz.trimf(risk.universe, [0, 0, 40])
    risk["suspicious"] = fuzz.trimf(risk.universe, [30, 50, 70])
    risk["high_alert"] = fuzz.trimf(risk.universe, [60, 100, 100])

    rules = [
        ctrl.Rule(movement["low"] & sound["quiet"], risk["safe"]),
        ctrl.Rule(movement["medium"] & sound["normal"], risk["suspicious"]),
        ctrl.Rule(movement["high"] & sound["loud"], risk["high_alert"]),
        ctrl.Rule(movement["high"] & light["high"], risk["high_alert"]),
        ctrl.Rule(movement["medium"] & light["medium"], risk["suspicious"]),
        ctrl.Rule(sound["loud"] & light["high"], risk["suspicious"]),
        ctrl.Rule(movement["low"] & sound["loud"], risk["suspicious"]),
    ]

    return ctrl.ControlSystem(rules)


@st.cache_resource
def create_safety_system():
    temperature = ctrl.Antecedent(np.arange(0, 101, 1), "temperature")
    gas = ctrl.Antecedent(np.arange(0, 101, 1), "gas")
    water = ctrl.Antecedent(np.arange(0, 101, 1), "water")
    risk = ctrl.Consequent(np.arange(0, 101, 1), "safety_risk")

    temperature["normal"] = fuzz.trimf(temperature.universe, [0, 0, 40])
    temperature["warm"] = fuzz.trimf(temperature.universe, [30, 50, 70])
    temperature["hot"] = fuzz.trimf(temperature.universe, [60, 100, 100])

    gas["safe"] = fuzz.trimf(gas.universe, [0, 0, 40])
    gas["warning"] = fuzz.trimf(gas.universe, [30, 50, 70])
    gas["dangerous"] = fuzz.trimf(gas.universe, [60, 100, 100])

    water["dry"] = fuzz.trimf(water.universe, [0, 0, 40])
    water["wet"] = fuzz.trimf(water.universe, [30, 50, 70])
    water["flood"] = fuzz.trimf(water.universe, [60, 100, 100])

    risk["safe"] = fuzz.trimf(risk.universe, [0, 0, 40])
    risk["warning"] = fuzz.trimf(risk.universe, [30, 50, 70])
    risk["emergency"] = fuzz.trimf(risk.universe, [60, 100, 100])

    rules = [
        ctrl.Rule(temperature["hot"], risk["emergency"]),
        ctrl.Rule(gas["dangerous"], risk["emergency"]),
        ctrl.Rule(water["flood"], risk["emergency"]),
        ctrl.Rule(gas["warning"] & temperature["warm"], risk["warning"]),
        ctrl.Rule(water["wet"], risk["warning"]),
        ctrl.Rule(temperature["normal"] & gas["safe"], risk["safe"]),
        ctrl.Rule(water["dry"] & gas["safe"], risk["safe"]),
    ]

    return ctrl.ControlSystem(rules)


def classify_intrusion(score):
    if score < 40:
        return "Safe", "No alarm needed"
    elif score < 70:
        return "Suspicious", "Monitor the area"
    else:
        return "High Alert", "Activate alarm"


def classify_safety(score):
    if score < 40:
        return "Safe", "No action needed"
    elif score < 70:
        return "Warning", "Check the affected area"
    else:
        return "Emergency", "Activate alarm immediately"


# -----------------------------
# App Layout
# -----------------------------
st.sidebar.title("🏠 Home Alert App")
page = st.sidebar.radio(
    "Choose page",
    ["Dashboard", "Intrusion Check", "Safety Check", "About"]
)

intrusion_system = create_intrusion_system()
safety_system = create_safety_system()

if page == "Dashboard":
    st.title("Smart Home Intrusion and Safety Alert System")
    st.write("This app uses fuzzy logic to estimate home intrusion and safety risks.")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Intrusion Sensors")
        movement = st.slider("Movement Level", 0, 100, 50)
        sound = st.slider("Sound / Voice Level", 0, 100, 50)
        light = st.slider("Light Change Level", 0, 100, 50)

    with col2:
        st.subheader("Safety Sensors")
        temperature = st.slider("Temperature Level", 0, 100, 50)
        gas = st.slider("Gas Level", 0, 100, 50)
        water = st.slider("Water / Flood Level", 0, 100, 50)

    if st.button("Check Overall Risk"):
        intrusion_sim = ctrl.ControlSystemSimulation(intrusion_system)
        intrusion_sim.input["movement"] = movement
        intrusion_sim.input["sound"] = sound
        intrusion_sim.input["light"] = light
        intrusion_sim.compute()

        safety_sim = ctrl.ControlSystemSimulation(safety_system)
        safety_sim.input["temperature"] = temperature
        safety_sim.input["gas"] = gas
        safety_sim.input["water"] = water
        safety_sim.compute()

        intrusion_score = intrusion_sim.output["intrusion_risk"]
        safety_score = safety_sim.output["safety_risk"]

        intrusion_status, intrusion_action = classify_intrusion(intrusion_score)
        safety_status, safety_action = classify_safety(safety_score)

        st.subheader("Results")

        r1, r2 = st.columns(2)

        with r1:
            st.metric("Intrusion Risk", f"{intrusion_score:.2f}/100")
            st.progress(int(intrusion_score))
            st.write(f"Status: **{intrusion_status}**")
            st.write(f"Action: {intrusion_action}")

        with r2:
            st.metric("Safety Risk", f"{safety_score:.2f}/100")
            st.progress(int(safety_score))
            st.write(f"Status: **{safety_status}**")
            st.write(f"Action: {safety_action}")

elif page == "Intrusion Check":
    st.title("Intrusion Risk Check")

    movement = st.slider("Movement Level", 0, 100, 50)
    sound = st.slider("Sound / Voice Level", 0, 100, 50)
    light = st.slider("Light Change Level", 0, 100, 50)

    if st.button("Check Intrusion Risk"):
        sim = ctrl.ControlSystemSimulation(intrusion_system)
        sim.input["movement"] = movement
        sim.input["sound"] = sound
        sim.input["light"] = light
        sim.compute()

        score = sim.output["intrusion_risk"]
        status, action = classify_intrusion(score)

        st.metric("Intrusion Risk Score", f"{score:.2f}/100")
        st.progress(int(score))

        if status == "Safe":
            st.success(f"{status}: {action}")
        elif status == "Suspicious":
            st.warning(f"{status}: {action}")
        else:
            st.error(f"{status}: {action}")

elif page == "Safety Check":
    st.title("Home Safety Risk Check")

    temperature = st.slider("Temperature Level", 0, 100, 50)
    gas = st.slider("Gas Level", 0, 100, 50)
    water = st.slider("Water / Flood Level", 0, 100, 50)

    if st.button("Check Safety Risk"):
        sim = ctrl.ControlSystemSimulation(safety_system)
        sim.input["temperature"] = temperature
        sim.input["gas"] = gas
        sim.input["water"] = water
        sim.compute()

        score = sim.output["safety_risk"]
        status, action = classify_safety(score)

        st.metric("Safety Risk Score", f"{score:.2f}/100")
        st.progress(int(score))

        if status == "Safe":
            st.success(f"{status}: {action}")
        elif status == "Warning":
            st.warning(f"{status}: {action}")
        else:
            st.error(f"{status}: {action}")

elif page == "About":
    st.title("About This Project")
    st.write("""
    This project is a fuzzy logic based smart home alert system.
    
    It contains two fuzzy modules:
    
    1. Intrusion alert system  
    2. Home safety alert system  
    
    The app uses sensor values between 0 and 100 to calculate risk levels.
    """)