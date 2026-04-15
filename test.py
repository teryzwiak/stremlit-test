import streamlit as st

def generate_voss_config(start_port, end_port, vlan_id, hostname):
    config = [
        f"!",
        f"! Configuration for {hostname}",
        f"!",
        "vlan members add {vlan} {ports}".format(vlan=vlan_id, ports=f"1/{start_port}-1/{end_port}"),
        f"interface gigabitEthernet 1/{start_port}-1/{end_port}"
    ]
    
    # W VOSS zazwyczaj ustawiamy domyślny VLAN (untagged) i włączamy discard-tagged jeśli to port dostępowy
    config.append(f"  untagged-vlan {vlan_id}")
    config.append("  exit")
    
    return "\n".join(config)

# --- UI ---
st.set_page_config(page_title="VOSS Config Generator", page_icon="🌐")

st.title("🚀 Extreme VOSS Port Configurator")
st.markdown("Generator konfiguracji dla przełączników serii VSP/Universal (VOSS).")

with st.sidebar:
    st.header("Ustawienia Ogólne")
    hostname = st.text_input("Nazwa switcha", "Extreme-VSP-01")
    vlan_id = st.number_input("ID VLANu", min_value=1, max_value=4094, value=10)

st.subheader("Zakres portów (48-portowy switch)")
col1, col2 = st.columns(2)

with col1:
    start_p = st.number_input("Pierwszy port", min_value=1, max_value=48, value=1)
with col2:
    end_p = st.number_input("Ostatni port", min_value=1, max_value=48, value=1)

if start_p > end_p:
    st.error("Błąd: Port początkowy nie może być większy niż końcowy!")
else:
    config_result = generate_voss_config(start_p, end_p, vlan_id, hostname)

    st.markdown("### Wygenerowany Config:")
    st.code(config_result, language="bash")

    st.download_button(
        label="Pobierz jako .txt",
        data=config_result,
        file_name=f"config_{hostname}.txt",
        mime="text/plain"
    )

st.info("💡 Wskazówka: W VOSS komenda `vlan members add` jest wymagana globalnie lub w kontekście VLANu, aby port mógł przesyłać ruch.")