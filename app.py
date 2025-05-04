import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Jurnal Trading RissInvest", layout="centered")
st.title("Jurnal Trading - RissInvest")

CSV_FILE = "jurnal_trading.csv"

# Load data jika ada
try:
    df = pd.read_csv(CSV_FILE)
except:
    df = pd.DataFrame(columns=[
        "Tanggal", "Waktu", "Pair", "Arah", "Entry Price", "SL (pips)", "TP (pips)",
        "SL Harga", "TP Harga", "Lot", "Status", "P/L (pip)"
    ])

# Form input
with st.form("trade_form"):
    col1, col2 = st.columns(2)
    tanggal = col1.date_input("Tanggal", datetime.today())
    waktu = col2.time_input("Waktu", datetime.now().time())
    pair = st.selectbox("Pair", ["XAUUSD", "USDJPY", "EURUSD", "BTCUSD", "Lainnya"])
    arah = st.radio("Arah", ["Buy", "Sell"])
    entry_price = st.number_input("Entry Price", format="%.2f")
    sl_pips = st.number_input("Stop Loss (pips)", min_value=0.0, format="%.1f")
    tp_pips = st.number_input("Take Profit (pips)", min_value=0.0, format="%.1f")
    lot = st.number_input("Lot", min_value=0.01, value=0.01, step=0.01)
    status = st.selectbox("Status", ["Running", "Hit TP", "Hit SL"])

    submit = st.form_submit_button("Simpan Trade")

    if submit:
        pip_value = 0.01 if "JPY" not in pair else 0.01
        if arah == "Buy":
            sl_harga = entry_price - sl_pips * pip_value
            tp_harga = entry_price + tp_pips * pip_value
        else:
            sl_harga = entry_price + sl_pips * pip_value
            tp_harga = entry_price - tp_pips * pip_value

        if status == "Hit TP":
            pl = tp_pips
        elif status == "Hit SL":
            pl = -sl_pips
        else:
            pl = 0.0

        new_row = {
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

        df = df.append(new_row, ignore_index=True)
        df.to_csv(CSV_FILE, index=False)
        st.success("Trade berhasil disimpan!")

# Tampilkan histori
st.subheader("Histori Trading")
st.dataframe(df)

# Download tombol
st.download_button("Download CSV", df.to_csv(index=False), "jurnal_trading.csv", "text/csv")

# Grafik Analisa
st.subheader("Analisa Grafik")

# Filter hanya trade yang sudah selesai
df_done = df[df["Status"].isin(["Hit TP", "Hit SL"])].copy()
df_done["Tanggal"] = pd.to_datetime(df_done["Tanggal"])
df_done["Cumulative Pips"] = df_done["P/L (pip)"].cumsum()

if not df_done.empty:
    # Grafik P/L per trade
    fig1 = px.bar(df_done, x="Tanggal", y="P/L (pip)", color="Status", title="P/L per Trade")
    st.plotly_chart(fig1, use_container_width=True)

    # Grafik Cumulative Pips
    fig2 = px.line(df_done, x="Tanggal", y="Cumulative Pips", title="Cumulative Profit (Pips)")
    st.plotly_chart(fig2, use_container_width=True)

    # Winrate Pie Chart
    win_count = (df_done["P/L (pip)"] > 0).sum()
    loss_count = (df_done["P/L (pip)"] < 0).sum()
    pie_fig = go.Figure(data=[go.Pie(
        labels=["Menang", "Kalah"],
        values=[win_count, loss_count],
        hole=0.4
    )])
    pie_fig.update_layout(title="Rasio Menang vs Kalah")
    st.plotly_chart(pie_fig, use_container_width=True)
else:
    st.info("Belum ada trade selesai (TP/SL) untuk ditampilkan di grafik.")
