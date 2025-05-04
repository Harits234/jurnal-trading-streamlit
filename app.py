# Re-run the code after code execution state reset
code = """
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Jurnal Trading Canggih", layout="wide")
st.title("Jurnal Trading Canggih")

# Load or initialize session state
if 'data' not in st.session_state:
    st.session_state.data = pd.DataFrame(columns=[
        "Tanggal", "Pair", "Tipe", "Lot", "Entry", "SL", "TP",
        "Exit", "Komisi", "Swap", "Keterangan", "P/L"
    ])

# Form input
with st.form("trade_form"):
    col1, col2, col3 = st.columns(3)
    tanggal = col1.date_input("Tanggal")
    pair = col1.text_input("Pair", "XAUUSD")
    tipe = col1.selectbox("Tipe", ["Buy", "Sell"])
    lot = col2.number_input("Lot", 0.01, step=0.01)
    entry = col2.number_input("Harga Entry")
    exit_price = col2.number_input("Harga Exit")
    sl = col3.number_input("SL")
    tp = col3.number_input("TP")
    komisi = col3.number_input("Komisi", value=0.0)
    swap = col3.number_input("Swap", value=0.0)
    ket = st.text_input("Keterangan")
    submit = st.form_submit_button("Tambah Data")

    if submit:
        pl = (exit_price - entry) * 100 if tipe == "Buy" else (entry - exit_price) * 100
        pl = pl * lot - komisi - swap
        new_row = {
            "Tanggal": tanggal,
            "Pair": pair,
            "Tipe": tipe,
            "Lot": lot,
            "Entry": entry,
            "SL": sl,
            "TP": tp,
            "Exit": exit_price,
            "Komisi": komisi,
            "Swap": swap,
            "Keterangan": ket,
            "P/L": round(pl, 2)
        }
        st.session_state.data = pd.concat([st.session_state.data, pd.DataFrame([new_row])], ignore_index=True)
        st.success("Data berhasil ditambahkan!")

# Show table
st.subheader("Data Trading")
st.dataframe(st.session_state.data, use_container_width=True)

# Equity curve
if not st.session_state.data.empty:
    st.subheader("Equity Curve")
    st.session_state.data["Equity"] = st.session_state.data["P/L"].cumsum()
    st.line_chart(st.session_state.data.set_index("Tanggal")[["Equity"]])

    # Statistik
    st.subheader("Statistik")
    total_pl = st.session_state.data["P/L"].sum()
    win = st.session_state.data[st.session_state.data["P/L"] > 0].shape[0]
    loss = st.session_state.data[st.session_state.data["P/L"] <= 0].shape[0]
    total = win + loss
    win_rate = (win / total) * 100 if total > 0 else 0
    st.write(f"Total Profit/Loss: {total_pl:.2f}")
    st.write(f"Win: {win} | Loss: {loss} | Win Rate: {win_rate:.2f}%")
"""

file_path = "/mnt/data/app.py"
with open(file_path, "w") as f:
    f.write(code)

file_path
