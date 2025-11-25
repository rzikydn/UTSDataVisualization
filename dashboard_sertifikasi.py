# ==========================================================
# Streamlit Dashboard Sertifikasi - Supabase
# Layout: Tabs (Overview, By Institution, By Notion)
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
from supabase import create_client
import plotly.graph_objs as go

# =========================
# 1. Konfigurasi Supabase
# =========================
SUPABASE_URL = "https://gxcnwbsigttvnrcflbhf.supabase.co"
# ⚠️ GANTI dengan anon key Anda (bukan publishable key)
# Cek di: Supabase Dashboard → Project Settings → API → anon (public) key
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd4Y253YnNpZ3R0dm5yY2ZsYmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMjk4MDEsImV4cCI6MjA3OTYwNTgwMX0.pKkVAXvHR5qtT7fO_LcFMwKLU-jd8twKIH0rNf9bxak"  # Biasanya diawali eyJhbGc...
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# =========================
# 2. Fungsi Load Data
# =========================
def load_bigdata():
    """Load data dari tabel DataVisualisation1 (sebagai pengganti bigdata)"""
    all_data, offset, page_size = [], 0, 1000
    while True:
        response = supabase.table("DataVisualisation1").select("*").range(offset, offset+page_size-1).execute()
        if not response.data: break
        all_data.extend(response.data)
        offset += page_size
    df = pd.DataFrame(all_data)
    if not df.empty:
        # Konversi kolom tanggal
        df["date certification"] = pd.to_datetime(df["tanggal_sertifikasi"])
        # Kolom lainnya sudah sesuai, tinggal buat alias
        df["jenis sertifikasi"] = df["jenis_sertifikasi"]
        df["nama sertifikasi"] = df["nama_sertifikasi"]
        df["on progress"] = df["on_progress"]
        df["pengajuan awal"] = df["pengajuan_awal"]
    return df

def load_notion():
    """Load data dari tabel DataVisualisation1 (untuk simulasi data notion)"""
    # Karena hanya ada 1 tabel, kita pakai data yang sama
    all_data, offset, page_size = [], 0, 1000
    while True:
        response = supabase.table("DataVisualisation1").select("*").range(offset, offset+page_size-1).execute()
        if not response.data: break
        all_data.extend(response.data)
        offset += page_size
    df = pd.DataFrame(all_data)
    if not df.empty:
        df["date certification"] = pd.to_datetime(df["tanggal_sertifikasi"])
        df["nama sertifikasi"] = df["nama_sertifikasi"]
        # Untuk simulasi data notion, kita anggap "pendaftar" sebagai "peserta"
        df["peserta"] = df["pendaftar"]
    return df

# =========================
# 3. Load Source Data
# =========================
st.cache_data.clear()
df_bigdata = load_bigdata()
df_notion = load_notion()

# Debug sudah tidak diperlukan, bisa dihapus atau dikomentari
# st.write("Kolom yang tersedia:", df_bigdata.columns.tolist())

# =========================
# 4. Helper
# =========================
def stat_card(label, value, icon):
    st.markdown(f"""
        <div style="display:flex;align-items:center;padding:10px;background-color:white;
        border-radius:10px;box-shadow:0px 2px 8px rgba(0,0,0,0.1);margin-bottom:10px">
            <div style="font-size:30px;margin-right:15px;">{icon}</div>
            <div>
                <div style="font-size:14px;color:gray;">{label}</div>
                <div style="font-size:24px;font-weight:bold;color:black;">{value}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

def get_status(row):
    if row["selesai"] > 0:         return "Selesai"
    elif row["on progress"] > 0:   return "On Progress"
    elif row["dibatalkan"] > 0:    return "Dibatalkan"
    else:                          return "Pengajuan Awal"

def dual_date_input(label_prefix, min_date, max_date, key_prefix):
    """2 input tanggal (mulai & akhir) dengan default sama2 min_date"""
    col1, col2 = st.columns(2)
    start_date = col1.date_input(
        f"{label_prefix} - Mulai",
        min_value=min_date, max_value=max_date,
        value=min_date, key=f"{key_prefix}_start"
    )
    end_date = col2.date_input(
        f"{label_prefix} - Akhir",
        min_value=min_date, max_value=max_date,
        value=min_date,   # default ke min_date
        key=f"{key_prefix}_end"
    )
    if start_date > end_date:
        st.warning("⚠️ Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
    return start_date, end_date

# =========================
# 5. Tabs Layout
# =========================
st.title("📊 DASHBOARD SERTIFIKASI")
st.markdown("---")
tab1, tab2, tab3, tab4 = st.tabs(["📈 Overview", "🏆 Top 5 Institutions", "📊 Trends & Analytics", "🎯 Status Distribution"])

# ===== Tab 1: Overview =====
with tab1:
    st.subheader("VISUALISASI DATA SERTIFIKASI BY BASYS")

    #-- Filter Tanggal--#
    min_date = df_bigdata["date certification"].min().date()
    max_date = df_bigdata["date certification"].max().date()
    start_date, end_date = dual_date_input("Pilih tanggal", min_date, max_date, key_prefix="overview")

    jenis_list = ["All"] + sorted(df_bigdata["jenis sertifikasi"].dropna().unique())
    instansi_list = ["All"] + sorted(df_bigdata["instansi"].dropna().unique())
    col1, col2 = st.columns(2)
    sel_jenis = col1.selectbox("Jenis Sertifikasi", jenis_list, key="jenis_overview")
    sel_instansi = col2.selectbox("Pilih nama instansi", instansi_list, key="instansi_overview")

    # Filter data
    filtered_df = df_bigdata[
        (df_bigdata["date certification"].dt.date >= start_date) &
        (df_bigdata["date certification"].dt.date <= end_date)
    ]
    if sel_jenis != "All":
        filtered_df = filtered_df[filtered_df["jenis sertifikasi"] == sel_jenis]
    if sel_instansi != "All":
        filtered_df = filtered_df[filtered_df["instansi"] == sel_instansi]
    filtered_df["status"] = filtered_df.apply(get_status, axis=1)

    # Stat cards
    stat_card("Total Pendaftar", int(filtered_df["pendaftar"].sum()), "👥")
    stat_card("Pengajuan Awal", int(filtered_df["pengajuan awal"].sum()), "📌")
    stat_card("On Progress", int(filtered_df["on progress"].sum()), "⏳")
    stat_card("Total Dibatalkan", int(filtered_df["dibatalkan"].sum()), "❌")
    stat_card("Selesai", int(filtered_df["selesai"].sum()), "✅")

    # Chart
    df_month = (
        filtered_df
        .groupby(filtered_df["date certification"].dt.to_period("M"))["pendaftar"]
        .sum().reset_index(name="Jumlah")
    )
    df_month["date certification"] = df_month["date certification"].astype(str)
    fig_over = px.bar(df_month, x="date certification", y="Jumlah", text="Jumlah",
                      title="TOTAL PENDAFTAR SERTIFIKASI PERBULAN BERDASARKAN DATA BASYS", height=500)
    fig_over.update_traces(textposition="outside")
    st.plotly_chart(fig_over, use_container_width=True)


# ===== Tab 2: Top 5 Institutions =====
with tab2:
    st.subheader("🏆 ANALISIS TOP 5 INSTANSI")

    min_date_top = df_bigdata["date certification"].min().date()
    max_date_top = df_bigdata["date certification"].max().date()
    start_date, end_date = dual_date_input("Pilih tanggal", min_date_top, max_date_top, key_prefix="top5")

    jenis_list_top = ["All"] + sorted(df_bigdata["jenis sertifikasi"].dropna().unique())
    sel_jenis_top = st.selectbox("Jenis Sertifikasi", jenis_list_top, key="jenis_top5")

    # Filter data
    filtered_df_top = df_bigdata[
        (df_bigdata["date certification"].dt.date >= start_date) &
        (df_bigdata["date certification"].dt.date <= end_date)
    ]
    if sel_jenis_top != "All":
        filtered_df_top = filtered_df_top[filtered_df_top["jenis sertifikasi"] == sel_jenis_top]

    # Top 5 instansi berdasarkan pendaftar
    top5 = (
        filtered_df_top.groupby("instansi").agg({
            "pendaftar": "sum",
            "selesai": "sum",
            "dibatalkan": "sum",
            "on_progress": "sum"
        }).reset_index()
        .sort_values("pendaftar", ascending=False).head(5)
    )
    top5["completion_rate"] = (top5["selesai"] / top5["pendaftar"] * 100).round(1)

    # Stat cards untuk top 5
    col1, col2, col3 = st.columns(3)
    with col1:
        stat_card("Total Pendaftar (Top 5)", int(top5["pendaftar"].sum()), "👥")
    with col2:
        stat_card("Total Selesai (Top 5)", int(top5["selesai"].sum()), "✅")
    with col3:
        avg_completion = top5["completion_rate"].mean()
        stat_card("Avg Completion Rate", f"{avg_completion:.1f}%", "📈")

    # Chart 1: Bar chart horizontal top 5
    fig_top5_bar = px.bar(
        top5.sort_values("pendaftar", ascending=True),
        y="instansi",
        x="pendaftar",
        title="TOP 5 INSTANSI BERDASARKAN JUMLAH PENDAFTAR",
        text="pendaftar",
        color="pendaftar",
        color_continuous_scale="Blues",
        orientation='h',
        height=400
    )
    fig_top5_bar.update_traces(textposition="outside")
    fig_top5_bar.update_layout(showlegend=False, xaxis_title="Jumlah Pendaftar", yaxis_title="Instansi")
    st.plotly_chart(fig_top5_bar, use_container_width=True)

    # Chart 2: Comparison stacked bar (Selesai vs Dibatalkan vs On Progress)
    top5_melted = top5.melt(
        id_vars=["instansi"],
        value_vars=["selesai", "on_progress", "dibatalkan"],
        var_name="Status",
        value_name="Jumlah"
    )

    fig_comparison = px.bar(
        top5_melted,
        x="instansi",
        y="Jumlah",
        color="Status",
        title="DISTRIBUSI STATUS SERTIFIKASI - TOP 5 INSTANSI",
        barmode="stack",
        height=400,
        color_discrete_map={
            "selesai": "#28a745",
            "on_progress": "#ffc107",
            "dibatalkan": "#dc3545"
        }
    )
    fig_comparison.update_layout(xaxis_tickangle=-30)
    st.plotly_chart(fig_comparison, use_container_width=True)

    # Table detail top 5
    st.subheader("Detail Top 5 Instansi")
    top5_display = top5[["instansi", "pendaftar", "selesai", "on_progress", "dibatalkan", "completion_rate"]]
    top5_display.columns = ["Instansi", "Pendaftar", "Selesai", "On Progress", "Dibatalkan", "Completion Rate (%)"]
    st.dataframe(top5_display, use_container_width=True, hide_index=True)

# ===== Tab 3: Trends & Analytics =====
with tab3:
    st.subheader("📊 ANALISIS TREND SERTIFIKASI")

    min_date_trend = df_bigdata["date certification"].min().date()
    max_date_trend = df_bigdata["date certification"].max().date()
    start_date, end_date = dual_date_input("Pilih tanggal", min_date_trend, max_date_trend, key_prefix="trends")

    filtered_df_trend = df_bigdata[
        (df_bigdata["date certification"].dt.date >= start_date) &
        (df_bigdata["date certification"].dt.date <= end_date)
    ]

    # Trend line chart (Pendaftar vs Selesai per bulan)
    df_trend_month = (
        filtered_df_trend
        .groupby(filtered_df_trend["date certification"].dt.to_period("M"))
        .agg({
            "pendaftar": "sum",
            "selesai": "sum",
            "dibatalkan": "sum",
            "on_progress": "sum"
        }).reset_index()
    )
    df_trend_month["date certification"] = df_trend_month["date certification"].astype(str)

    fig_trend_line = px.line(
        df_trend_month,
        x="date certification",
        y=["pendaftar", "selesai", "on_progress", "dibatalkan"],
        title="TREND SERTIFIKASI PER BULAN",
        markers=True,
        height=450,
        color_discrete_map={
            "pendaftar": "#3498db",
            "selesai": "#28a745",
            "on_progress": "#ffc107",
            "dibatalkan": "#dc3545"
        }
    )
    fig_trend_line.update_layout(
        xaxis_title="Bulan",
        yaxis_title="Jumlah",
        legend_title="Kategori"
    )
    st.plotly_chart(fig_trend_line, use_container_width=True)

    # Pie chart: Jenis Sertifikasi
    col1, col2 = st.columns(2)

    with col1:
        jenis_dist = filtered_df_trend.groupby("jenis sertifikasi")["pendaftar"].sum().reset_index()
        fig_jenis_pie = px.pie(
            jenis_dist,
            values="pendaftar",
            names="jenis sertifikasi",
            title="DISTRIBUSI BERDASARKAN JENIS SERTIFIKASI",
            height=400
        )
        st.plotly_chart(fig_jenis_pie, use_container_width=True)

    with col2:
        # Success rate pie
        total_pendaftar = filtered_df_trend["pendaftar"].sum()
        total_selesai = filtered_df_trend["selesai"].sum()
        total_belum = total_pendaftar - total_selesai

        success_data = pd.DataFrame({
            "Status": ["Selesai", "Belum Selesai"],
            "Jumlah": [total_selesai, total_belum]
        })

        fig_success_pie = px.pie(
            success_data,
            values="Jumlah",
            names="Status",
            title="SUCCESS RATE KESELURUHAN",
            height=400,
            color="Status",
            color_discrete_map={
                "Selesai": "#28a745",
                "Belum Selesai": "#dc3545"
            }
        )
        st.plotly_chart(fig_success_pie, use_container_width=True)

    # Completion rate per instansi (Top 10)
    completion_by_inst = (
        filtered_df_trend.groupby("instansi")
        .agg({"pendaftar": "sum", "selesai": "sum"})
        .reset_index()
    )
    completion_by_inst = completion_by_inst[completion_by_inst["pendaftar"] > 0]
    completion_by_inst["completion_rate"] = (
        completion_by_inst["selesai"] / completion_by_inst["pendaftar"] * 100
    ).round(1)
    top10_completion = completion_by_inst.nlargest(10, "pendaftar")

    fig_completion = px.bar(
        top10_completion.sort_values("completion_rate", ascending=True),
        y="instansi",
        x="completion_rate",
        title="COMPLETION RATE TOP 10 INSTANSI (berdasarkan jumlah pendaftar)",
        text="completion_rate",
        orientation='h',
        height=450,
        color="completion_rate",
        color_continuous_scale="RdYlGn"
    )
    fig_completion.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_completion.update_layout(xaxis_title="Completion Rate (%)", yaxis_title="Instansi")
    st.plotly_chart(fig_completion, use_container_width=True)

# ===== Tab 4: Status Distribution =====
with tab4:
    st.subheader("🎯 DISTRIBUSI STATUS SERTIFIKASI")

    min_date_status = df_bigdata["date certification"].min().date()
    max_date_status = df_bigdata["date certification"].max().date()
    start_date, end_date = dual_date_input("Pilih tanggal", min_date_status, max_date_status, key_prefix="status")

    filtered_df_status = df_bigdata[
        (df_bigdata["date certification"].dt.date >= start_date) &
        (df_bigdata["date certification"].dt.date <= end_date)
    ]

    # Stat cards untuk status
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card("Total Pendaftar", int(filtered_df_status["pendaftar"].sum()), "👥")
    with col2:
        stat_card("Selesai", int(filtered_df_status["selesai"].sum()), "✅")
    with col3:
        stat_card("On Progress", int(filtered_df_status["on_progress"].sum()), "⏳")
    with col4:
        stat_card("Dibatalkan", int(filtered_df_status["dibatalkan"].sum()), "❌")

    # Status breakdown by jenis sertifikasi
    status_by_jenis = filtered_df_status.groupby("jenis sertifikasi").agg({
        "pendaftar": "sum",
        "selesai": "sum",
        "on_progress": "sum",
        "dibatalkan": "sum",
        "pengajuan_awal": "sum"
    }).reset_index()

    status_melted = status_by_jenis.melt(
        id_vars=["jenis sertifikasi"],
        value_vars=["selesai", "on_progress", "dibatalkan", "pengajuan_awal"],
        var_name="Status",
        value_name="Jumlah"
    )

    fig_status_grouped = px.bar(
        status_melted,
        x="jenis sertifikasi",
        y="Jumlah",
        color="Status",
        title="DISTRIBUSI STATUS PER JENIS SERTIFIKASI",
        barmode="group",
        height=400,
        color_discrete_map={
            "selesai": "#28a745",
            "on_progress": "#ffc107",
            "dibatalkan": "#dc3545",
            "pengajuan_awal": "#6c757d"
        }
    )
    st.plotly_chart(fig_status_grouped, use_container_width=True)

    # Funnel chart untuk conversion
    total_awal = filtered_df_status["pengajuan_awal"].sum()
    total_progress = filtered_df_status["on_progress"].sum()
    total_selesai = filtered_df_status["selesai"].sum()
    total_batal = filtered_df_status["dibatalkan"].sum()

    funnel_data = pd.DataFrame({
        "Stage": ["Pengajuan Awal", "On Progress", "Selesai"],
        "Jumlah": [total_awal if total_awal > 0 else total_progress, total_progress, total_selesai]
    })

    fig_funnel = px.funnel(
        funnel_data,
        x="Jumlah",
        y="Stage",
        title="CONVERSION FUNNEL SERTIFIKASI",
        height=400
    )
    st.plotly_chart(fig_funnel, use_container_width=True)

    # Table summary status
    st.subheader("Summary Status per Instansi")
    status_summary = (
        filtered_df_status.groupby("instansi")
        .agg({
            "pendaftar": "sum",
            "selesai": "sum",
            "on_progress": "sum",
            "dibatalkan": "sum",
            "pengajuan_awal": "sum"
        }).reset_index()
        .sort_values("pendaftar", ascending=False)
        .head(15)
    )
    status_summary["completion_rate"] = (
        status_summary["selesai"] / status_summary["pendaftar"] * 100
    ).round(1)

    status_summary.columns = ["Instansi", "Pendaftar", "Selesai", "On Progress", "Dibatalkan", "Pengajuan Awal", "Completion Rate (%)"]
    st.dataframe(status_summary, use_container_width=True, hide_index=True)
