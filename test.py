import streamlit as st
import pandas as pd

st.set_page_config(page_title="VOSS Fabric Configurator", layout="wide")

st.title("🔌 VOSS Multi-Switch Configurator")
st.markdown("Zdefiniuj swoje przełączniki, a następnie przypisz VLANy do konkretnych portów.")

# --- KROK 1: Definiowanie Switchy ---
st.header("1. Twoja Infrastruktura")
if 'switches' not in st.session_state:
    st.session_state.switches = ["Switch-01"]

new_switch = st.text_input("Dodaj nowy switch (nazwa):")
if st.button("Dodaj do listy"):
    if new_switch and new_switch not in st.session_state.switches:
        st.session_state.switches.append(new_switch)
        st.rerun()

selected_switch = st.selectbox("Wybierz switch do konfiguracji:", st.session_state.switches)

# --- KROK 2: Tabela Portów ---
st.header(f"2. Konfiguracja portów dla: {selected_switch}")

# Tworzymy bazowy DataFrame dla 48 portów
if f"df_{selected_switch}" not in st.session_state:
    data = {
        "Port": [f"1/{i}" for i in range(1, 49)],
        "VLAN": [1] * 48,  # Domyślnie VLAN 1
        "Status": ["Access"] * 48
    }
    st.session_state[f"df_{selected_switch}"] = pd.DataFrame(data)

# Edytor tabeli
edited_df = st.data_editor(
    st.session_state[f"df_{selected_switch}"],
    column_config={
        "Port": st.column_config.TextColumn("Port (GigabitEthernet)", disabled=True),
        "VLAN": st.column_config.NumberColumn("VLAN ID", min_value=1, max_value=4094, step=1),
        "Status": st.column_config.SelectboxColumn("Tryb", options=["Access", "Disabled"])
    },
    hide_index=True,
    key=f"editor_{selected_switch}"
)

# Zapisujemy zmiany w stanie sesji
st.session_state[f"df_{selected_switch}"] = edited_df

# --- KROK 3: Generowanie Configu ---
st.header("3. Wynikowy Config (CLI)")

def generate_voss_script(df, hostname):
    lines = [f"!", f"! Config for {hostname}", f"!"]
    
    # Grupowanie portów po VLANie, żeby nie pisać komendy dla każdego portu osobno
    vlan_groups = df[df["Status"] == "Access"].groupby("VLAN")["Port"].apply(list)
    
    for vlan, ports in vlan_groups.items():
        port_range = ",".join(ports)
        lines.append(f"vlan members add {vlan} {port_range}")
        for p in ports:
            lines.append(f"interface gigabitEthernet {p}")
            lines.append(f"  untagged-vlan {vlan}")
            lines.append("  exit")
    
    return "\n".join(lines)

full_config = generate_voss_script(edited_df, selected_switch)

st.code(full_config, language="bash")

st.download_button(
    label="Pobierz konfigurację",
    data=full_config,
    file_name=f"{selected_switch}_config.txt"
)