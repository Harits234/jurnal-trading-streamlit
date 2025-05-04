import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Jurnal Trading", layout="centered")
st.title("Jurnal Trading - RissInvest")

CSV_FILE = "jurnal_trading.csv"

# Load atau inisialisasi data
try:
    df = pd.read_csv(CSV_FILE)
except:
    df = pd.DataFrame(columns=[
        "Tanggal", "Waktu", "Pair", "Arah", "Entry Price", "SL (pips)", "TP (pips)",
        "SL Harga", "TP Harga", "Lot", "Status", "P/L (pip)"
    ])

# Form input data trade
with st.form("form_trade"):
    tanggal = st.date_input("Tanggal", datetime.today())
    waktu = st.time_input("Waktu", datetime.now().time())
    pair = st.selectbox("Pair", ["XAUUSD", "USDJPY", "EURUSD", "BTCUSD", "Lainnya"])
    arah = st.radio("Arah", ["Buy", "Sell"])
    entry_price = st.number_input("Entry Price", format="%.2f")
    sl_pips = st.number_input("Stop Loss (pips)", min_value=0.0, format="%.1f")
    tp_pips = st.number_input("Take Profit (pips)", min_value=0.0, format="%.1f")
    lot = st.number_input("Lot", min_value=0.01, step=0.01, value=0.01)
    status = st.selectbox("Status", ["Running", "Hit TP", "Hit SL"])

    simpan = st.form_submit_button("Simpan")

    if simpan:
        pip_val = 0.01  # Bisa lo ubah sesuai pair, misal pair JPY pakai 0.01 juga
        if arah == "Buy":
            sl_harga = entry_price - sl_pips * pip_val
            tp_harga = entry_price + tp_pips * pip_val
        else:
            sl_harga = entry_price + sl_pips * pip_val
            tp_harga = entry_price - tp_pips * pip_val

        if status == "Hit TP":
            pl = tp_pips
        elif status == "Hit SL":
            pl = -sl_pips
        else:
            pl = 0.0

        new_data = {
            "Tanggal": tanggal,
            "Waktu": waktu,
            "Pair": pair,
            "Arah": arah,
            "Entry Price": entry_price,
            "SL (pips)": sl_pips,
            "TP (pips)": tp_pips,
            "SL Harga": round(sl_harga, 2),
            "TP Harga": round(tp_harga, 2),
            "Lot": lot,
            "Status": status,
            "P/L (pip)": pl
        }

        df = df.append(new_data, ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("Data trade berhasil disimpan!")

# Tampilkan histori
st.subheader("Histori Trading")
st.dataframe(df)

# Download data
st.download_button("Download CSV", df.to_csv(index=False), "jurnal_trading.csv")

# Grafik P/L dan Cumulative Pips
st.subheader("Grafik Performa Trading")

df_done = df[df["Status"].isin(["Hit TP", "Hit SL"])].copy()
df_done["Tanggal"] = pd.to_datetime(df_done["Tanggal"])

if not df_done.empty:
    df_done["Cumulative Pips"] = df_done["P/L (pip)"].cumsum()

    # Grafik P/L
    st.markdown("**Profit / Loss per Trade**")
    fig1, ax1 = plt.subplots()
    ax1.bar(df_done["Tanggal"], df_done["P/L (pip)"], color=df_done["P/L (pip)"].apply(lambda x: 'green' if x > 0 else 'red'))
    ax1.axhline(0, color='black')
    ax1.set_ylabel("P/L (pip)")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # Grafik Cumulative
    st.markdown("**Cumulative Pips**")
    fig2, ax2 = plt.subplots()
    ax2.plot(df_done["Tanggal"], df_done["Cumulative Pips"], marker='o', linestyle='-')
    ax2.set_ylabel("Total Pips")
    plt.xticks(rotation=45)
    st.pyplot(fig2)

    # Winrate
    win = (df_done["P/L (pip)"] > 0).sum()
    lose = (df_done["P/L (pip)"] < 0).sum()
    st.markdown(f"**Win: {win} | Loss: {lose} | Winrate: {round(100 * win / (win + lose), 2) if (win + lose) > 0 else 0}%**")
else:
    st.info("Belum ada trade selesai (TP/SL) untuk ditampilkan di grafik.")
