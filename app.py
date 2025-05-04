import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Jurnal Trading", layout="centered")
st.title("Jurnal Trading - SL/TP pakai Pips")

CSV_FILE = "jurnal_trading.csv"

# Load data
try:
    df = pd.read_csv(CSV_FILE)
except:
    df = pd.DataFrame(columns=[
        "Tanggal", "Waktu", "Pair", "Arah", "Entry Price", "SL (pips)", "TP (pips)",
        "SL Harga", "TP Harga", "Lot", "Status", "P/L (pip)"
    ])

# Form input
with st.form("form_trade"):
    col1, col2 = st.columns(2)
    tanggal = col1.date_input("Tanggal", datetime.today())
    waktu = col2.time_input("Waktu", datetime.now().time())
    pair = st.selectbox("Pair", ["XAUUSD", "USDJPY", "EURUSD", "BTCUSD", "Lainnya"])
    arah = st.radio("Arah", ["Buy", "Sell"])
    entry = st.number_input("Entry Price", format="%.2f")
    sl_pip = st.number_input("Stop Loss (pips)", min_value=0.0, format="%.1f")
    tp_pip = st.number_input("Take Profit (pips)", min_value=0.0, format="%.1f")
    lot = st.number_input("Lot", min_value=0.01, step=0.01, value=0.01)
    status = st.selectbox("Status", ["Running", "Hit TP", "Hit SL"])

    submit = st.form_submit_button("Simpan Trade")

    if submit:
        pip_val = 0.01  # as default, bisa disesuaikan kalau pair JPY
        if arah == "Buy":
            sl_harga = entry - sl_pip * pip_val
            tp_harga = entry + tp_pip * pip_val
        else:
            sl_harga = entry + sl_pip * pip_val
            tp_harga = entry - tp_pip * pip_val

        if status == "Hit TP":
            pl = tp_pip
        elif status == "Hit SL":
            pl = -sl_pip
        else:
            pl = 0.0

        new_row = {
            "Tanggal": tanggal,
            "Waktu": waktu,
            "Pair": pair,
            "Arah": arah,
            "Entry Price": entry,
            "SL (pips)": sl_pip,
            "TP (pips)": tp_pip,
            "SL Harga": round(sl_harga, 2),
            "TP Harga": round(tp_harga, 2),
            "Lot": lot,
            "Status": status,
            "P/L (pip)": pl
        }

        df = df.append(new_row, ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("Trade berhasil disimpan!")

# Tabel histori
st.subheader("Histori Trading")
st.dataframe(df)

# Download
st.download_button("Download CSV", df.to_csv(index=False), "jurnal_trading.csv", "text/csv")

# Grafik Analisa
st.subheader("Grafik Hasil Trading")
df_done = df[df["Status"].isin(["Hit TP", "Hit SL"])].copy()
df_done["Tanggal"] = pd.to_datetime(df_done["Tanggal"])

if not df_done.empty:
    # Grafik P/L per trade
    st.markdown("**P/L per Trade**")
    fig, ax = plt.subplots()
    ax.bar(df_done["Tanggal"], df_done["P/L (pip)"], color=["green" if x > 0 else "red" for x in df_done["P/L (pip)"]])
    ax.axhline(0, color='black', linewidth=0.8)
    ax.set_ylabel("P/L (pip)")
    ax.set_xlabel("Tanggal")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Grafik cumulative
    st.markdown("**Cumulative Profit (Pips)**")
    df_done["Cumulative Pips"] = df_done["P/L (pip)"].cumsum()
    fig2, ax2 = plt.subplots()
    ax2.plot(df_done["Tanggal"], df_done["Cumulative Pips"], marker='o')
    ax2.set_ylabel("Total Pips")
    ax2.set_xlabel("Tanggal")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # Winrate
    win = (df_done["P/L (pip)"] > 0).sum()
    lose = (df_done["P/L (pip)"] < 0).sum()
    st.markdown(f"**Winrate: {win} Menang / {lose} Kalah**")
else:
    st.info("Belum ada trade selesai untuk grafik.")
