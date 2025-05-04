import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Jurnal Trading", layout="centered")
st.title("Jurnal Trading - RissInvest")

CSV_FILE = "jurnal_trading.csv"

# Load data atau inisialisasi baru
try:
    df = pd.read_csv(CSV_FILE)
except:
    df = pd.DataFrame(columns=[
        "Tanggal", "Waktu", "Pair", "Arah", "Entry Price", "SL (pips)", "TP (pips)",
        "Lot", "Status", "P/L (pip)"
    ])

# Input form
with st.form("input_trade"):
    tanggal = st.date_input("Tanggal", datetime.today())
    waktu = st.time_input("Waktu", datetime.now().time())
    pair = st.selectbox("Pair", ["XAUUSD", "USDJPY", "EURUSD", "BTCUSD", "Lainnya"])
    arah = st.radio("Arah", ["Buy", "Sell"])
    entry_price = st.number_input("Entry Price", format="%.2f")
    sl_pips = st.number_input("SL (pips)", min_value=0.0)
    tp_pips = st.number_input("TP (pips)", min_value=0.0)
    lot = st.number_input("Lot", min_value=0.01, step=0.01)
    status = st.selectbox("Status", ["Running", "Hit TP", "Hit SL"])
    submit = st.form_submit_button("Simpan Trade")

    if submit:
        pl = tp_pips if status == "Hit TP" else -sl_pips if status == "Hit SL" else 0

        new_trade = {
            "Tanggal": tanggal,
            "Waktu": waktu,
            "Pair": pair,
            "Arah": arah,
            "Entry Price": entry_price,
            "SL (pips)": sl_pips,
            "TP (pips)": tp_pips,
            "Lot": lot,
            "Status": status,
            "P/L (pip)": pl
        }

        df = df.append(new_trade, ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("Trade berhasil disimpan!")

# Histori Trading
st.subheader("Histori Trading")
st.dataframe(df)

# Download
st.download_button("Download CSV", data=df.to_csv(index=False), file_name="jurnal_trading.csv")

# Grafik P/L dan Cumulative (pakai bawaan Streamlit)
st.subheader("Grafik P/L dan Akumulasi")

df_done = df[df["Status"].isin(["Hit TP", "Hit SL"])].copy()
if not df_done.empty:
    df_done["Tanggal"] = pd.to_datetime(df_done["Tanggal"])
    df_done = df_done.sort_values("Tanggal")
    df_done["Cumulative Pips"] = df_done["P/L (pip)"].cumsum()

    st.markdown("**P/L per Trade**")
    st.bar_chart(df_done[["Tanggal", "P/L (pip)"]].set_index("Tanggal"))

    st.markdown("**Cumulative Pips**")
    st.line_chart(df_done[["Tanggal", "Cumulative Pips"]].set_index("Tanggal"))

    win = (df_done["P/L (pip)"] > 0).sum()
    lose = (df_done["P/L (pip)"] < 0).sum()
    st.markdown(f"**Winrate: {win} / {win + lose} = {round(100 * win / (win + lose), 1) if win + lose > 0 else 0}%**")
else:
    st.info("Belum ada trade yang selesai (Hit TP/SL).")
