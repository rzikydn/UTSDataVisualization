# ==========================================================
# Streamlit Dashboard Sertifikasi - Supabase
# Layout: Tabs (Overview, By Institution, By Notion)
# ==========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import time
import requests

# =========================
# 1. Konfigurasi Supabase
# =========================
SUPABASE_URL = "https://gxcnwbsigttvnrcflbhf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imd4Y253YnNpZ3R0dm5yY2ZsYmhmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQwMjk4MDEsImV4cCI6MjA3OTYwNTgwMX0.pKkVAXvHR5qtT7fO_LcFMwKLU-jd8twKIH0rNf9bxak"

# Gunakan REST API langsung karena httpx di Python 3.14 ada issue
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# =========================
# 2. Fungsi Load Data
# =========================
def load_bigdata():
    """Load data dari tabel DataVisualisation1 menggunakan REST API"""
    all_data = []
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Gunakan REST API Supabase langsung
            url = f"{SUPABASE_URL}/rest/v1/DataVisualisation1"
            params = {"select": "*"}

            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()

            all_data = response.json()
            break  # Sukses, keluar dari retry loop

        except Exception as e:
            if attempt < max_retries - 1:
                st.warning(f"Koneksi gagal (percobaan {attempt + 1}/{max_retries}), mencoba lagi...")
                time.sleep(2)
            else:
                st.error(f"Error saat load data dari Supabase: {str(e)}")
                st.error(f"URL: {url}")
                st.error(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
                if 'response' in locals():
                    st.error(f"Response text: {response.text}")
                st.info("Menggunakan data kosong. Pastikan koneksi internet dan konfigurasi Supabase sudah benar.")

    df = pd.DataFrame(all_data)

    # Selalu buat kolom yang dibutuhkan, bahkan jika df kosong
    if df.empty:
        # Jika data kosong, buat DataFrame dengan struktur yang benar
        df = pd.DataFrame(columns=[
            "id", "created_at", "nama_sertifikasi", "jenis_sertifikasi",
            "tanggal_sertifikasi", "instansi", "pendaftar", "pengajuan_awal",
            "dibatalkan", "on_progress", "selesai", "no"
        ])
        df["date certification"] = pd.to_datetime([])
        df["jenis sertifikasi"] = []
        df["nama sertifikasi"] = []
        df["on progress"] = []
        df["pengajuan awal"] = []
    else:
        # Konversi kolom tanggal
        df["date certification"] = pd.to_datetime(df["tanggal_sertifikasi"], errors='coerce')
        # Kolom lainnya sudah sesuai, tinggal buat alias
        df["jenis sertifikasi"] = df["jenis_sertifikasi"]
        df["nama sertifikasi"] = df["nama_sertifikasi"]
        df["on progress"] = df["on_progress"]
        df["pengajuan awal"] = df["pengajuan_awal"]
    return df

def load_notion():
    """Load data dari tabel DataVisualisation1 menggunakan REST API"""
    all_data = []
    max_retries = 3

    for attempt in range(max_retries):
        try:
            # Gunakan REST API Supabase langsung
            url = f"{SUPABASE_URL}/rest/v1/DataVisualisation1"
            params = {"select": "*"}

            response = requests.get(url, headers=HEADERS, params=params, timeout=10)
            response.raise_for_status()

            all_data = response.json()
            break  # Sukses, keluar dari retry loop

        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                st.error(f"Error saat load data notion: {str(e)}")

    df = pd.DataFrame(all_data)

    if df.empty:
        # Jika data kosong, buat DataFrame dengan struktur yang benar
        df = pd.DataFrame(columns=[
            "id", "created_at", "nama_sertifikasi", "jenis_sertifikasi",
            "tanggal_sertifikasi", "instansi", "pendaftar", "pengajuan_awal",
            "dibatalkan", "on_progress", "selesai", "no"
        ])
        df["date certification"] = pd.to_datetime([])
        df["nama sertifikasi"] = []
        df["peserta"] = []
    else:
        df["date certification"] = pd.to_datetime(df["tanggal_sertifikasi"], errors='coerce')
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

# =========================
# 4. Helper
# =========================
def stat_card(label, value, icon):
    st.markdown(f"""
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
        padding:20px 15px;background-color:white;border-radius:10px;
        box-shadow:0px 2px 6px rgba(0,0,0,0.1);margin-bottom:10px;min-height:120px;">
            <div style="font-size:40px;margin-bottom:8px;">{icon}</div>
            <div style="text-align:center;width:100%;">
                <div style="font-size:11px;color:gray;margin-bottom:4px;line-height:1.3;">{label}</div>
                <div style="font-size:22px;font-weight:bold;color:black;line-height:1.2;">{value}</div>
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
# 5. Layout dengan Sidebar
# =========================
st.title("📊 DASHBOARD SERTIFIKASI")

# Cek data kosong
if len(df_bigdata) == 0 or df_bigdata["date certification"].isna().all():
    st.warning("⚠️ Belum ada data di database. Silakan tambahkan data terlebih dahulu.")
    st.stop()

# Sidebar untuk Filters
with st.sidebar:
    st.header("🔍 Filters")

    # Pilih Tab/View
    selected_tab = st.selectbox(
        "📊 Pilih Visualisasi",
        ["📈 Overview", "🏆 Top 5 Institutions", "📊 Trends & Analytics", "🎯 Status Distribution"]
    )

    st.markdown("---")

    # Filter Tanggal
    st.subheader("📅 Filter Tanggal")
    min_date = df_bigdata["date certification"].min().date()
    max_date = df_bigdata["date certification"].max().date()

    start_date = st.date_input(
        "Tanggal Mulai",
        min_value=min_date,
        max_value=max_date,
        value=min_date
    )

    end_date = st.date_input(
        "Tanggal Akhir",
        min_value=min_date,
        max_value=max_date,
        value=max_date
    )

    if start_date > end_date:
        st.error("⚠️ Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")

    st.markdown("---")

    # Filter Jenis & Instansi (untuk Overview)
    if selected_tab == "📈 Overview":
        st.subheader("🏢 Filter Data")
        jenis_list = ["All"] + sorted(df_bigdata["jenis sertifikasi"].dropna().unique())
        instansi_list = ["All"] + sorted(df_bigdata["instansi"].dropna().unique())

        sel_jenis = st.selectbox("Jenis Sertifikasi", jenis_list)
        sel_instansi = st.selectbox("Pilih Instansi", instansi_list)

    # Filter Jenis untuk Top 5
    elif selected_tab == "🏆 Top 5 Institutions":
        st.subheader("🏢 Filter Data")
        jenis_list_top = ["All"] + sorted(df_bigdata["jenis sertifikasi"].dropna().unique())
        sel_jenis_top = st.selectbox("Jenis Sertifikasi", jenis_list_top)

# Main Content Area
st.markdown("---")

# ===== Tab 1: Overview =====
if selected_tab == "📈 Overview":
    st.subheader("VISUALISASI DATA SERTIFIKASI BY BASYS")

    # Filter data
    filtered_df = df_bigdata[
        (df_bigdata["date certification"].dt.date >= start_date) &
        (df_bigdata["date certification"].dt.date <= end_date)
    ].copy()
    if sel_jenis != "All":
        filtered_df = filtered_df[filtered_df["jenis sertifikasi"] == sel_jenis]
    if sel_instansi != "All":
        filtered_df = filtered_df[filtered_df["instansi"] == sel_instansi]
    filtered_df["status"] = filtered_df.apply(get_status, axis=1)

    # Stat cards dalam 5 kolom horizontal
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        stat_card("Total Pendaftar", int(filtered_df["pendaftar"].sum()), "👥")
    with col2:
        stat_card("Pengajuan Awal", int(filtered_df["pengajuan awal"].sum()), "📌")
    with col3:
        stat_card("On Progress", int(filtered_df["on progress"].sum()), "⏳")
    with col4:
        stat_card("Total Dibatalkan", int(filtered_df["dibatalkan"].sum()), "❌")
    with col5:
        stat_card("Selesai", int(filtered_df["selesai"].sum()), "✅")

    st.markdown("<br>", unsafe_allow_html=True)

    # Chart full width
    df_month = (
        filtered_df
        .groupby(filtered_df["date certification"].dt.to_period("M"))["pendaftar"]
        .sum().reset_index(name="Jumlah")
    )
    df_month["date certification"] = df_month["date certification"].astype(str)
    fig_over = px.bar(df_month, x="date certification", y="Jumlah", text="Jumlah",
                      title="TOTAL PENDAFTAR SERTIFIKASI PERBULAN", height=400)
    fig_over.update_traces(textposition="outside")
    st.plotly_chart(fig_over, use_container_width=True)


# ===== Tab 2: Top 5 Institutions =====
elif selected_tab == "🏆 Top 5 Institutions":
    st.subheader("🏆 ANALISIS TOP 5 INSTANSI")

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

    # Charts dalam 2 kolom
    col1, col2 = st.columns(2)

    with col1:
        # Chart 1: Bar chart horizontal top 5
        fig_top5_bar = px.bar(
            top5.sort_values("pendaftar", ascending=True),
            y="instansi",
            x="pendaftar",
            title="TOP 5 INSTANSI",
            text="pendaftar",
            color="pendaftar",
            color_continuous_scale="Blues",
            orientation='h',
            height=350
        )
        fig_top5_bar.update_traces(textposition="outside")
        fig_top5_bar.update_layout(showlegend=False, xaxis_title="Jumlah Pendaftar", yaxis_title="")
        st.plotly_chart(fig_top5_bar, use_container_width=True)

    with col2:
        # Chart 2: Comparison stacked bar
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
            title="DISTRIBUSI STATUS",
            barmode="stack",
            height=350,
            color_discrete_map={
                "selesai": "#28a745",
                "on_progress": "#ffc107",
                "dibatalkan": "#dc3545"
            }
        )
        fig_comparison.update_layout(xaxis_tickangle=-30, xaxis_title="")
        st.plotly_chart(fig_comparison, use_container_width=True)

    # Table detail top 5 (lebih compact)
    top5_display = top5[["instansi", "pendaftar", "selesai", "on_progress", "dibatalkan", "completion_rate"]]
    top5_display.columns = ["Instansi", "Pendaftar", "Selesai", "On Progress", "Dibatalkan", "Completion Rate (%)"]
    st.dataframe(top5_display, use_container_width=True, hide_index=True)

# ===== Tab 3: Trends & Analytics =====
elif selected_tab == "📊 Trends & Analytics":
    st.subheader("📊 ANALISIS TREND SERTIFIKASI")

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

    # Charts dalam 2 kolom
    col1, col2 = st.columns([2, 1])

    with col1:
        fig_trend_line = px.line(
            df_trend_month,
            x="date certification",
            y=["pendaftar", "selesai", "on_progress", "dibatalkan"],
            title="TREND SERTIFIKASI PER BULAN",
            markers=True,
            height=350,
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
            title="SUCCESS RATE",
            height=350,
            color="Status",
            color_discrete_map={
                "Selesai": "#28a745",
                "Belum Selesai": "#dc3545"
            }
        )
        st.plotly_chart(fig_success_pie, use_container_width=True)

    # Second row: 2 kolom untuk jenis pie dan completion bar
    col3, col4 = st.columns([1, 2])

    with col3:
        # Pie chart jenis sertifikasi
        jenis_dist = filtered_df_trend.groupby("jenis sertifikasi")["pendaftar"].sum().reset_index()
        fig_jenis_pie = px.pie(
            jenis_dist,
            values="pendaftar",
            names="jenis sertifikasi",
            title="DISTRIBUSI JENIS SERTIFIKASI",
            height=350
        )
        st.plotly_chart(fig_jenis_pie, use_container_width=True)

    with col4:
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
            title="COMPLETION RATE TOP 10 INSTANSI",
            text="completion_rate",
            orientation='h',
            height=350,
            color="completion_rate",
            color_continuous_scale="RdYlGn"
        )
        fig_completion.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig_completion.update_layout(xaxis_title="Completion Rate (%)", yaxis_title="")
        st.plotly_chart(fig_completion, use_container_width=True)

# ===== Tab 4: Status Distribution =====
elif selected_tab == "🎯 Status Distribution":
    st.subheader("🎯 DISTRIBUSI STATUS SERTIFIKASI")

    filtered_df_status = df_bigdata[
        (df_bigdata["date certification"].dt.date >= start_date) &
        (df_bigdata["date certification"].dt.date <= end_date)
    ]

    # Stat cards dalam 1 baris
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        stat_card("Total Pendaftar", int(filtered_df_status["pendaftar"].sum()), "👥")
    with col2:
        stat_card("Selesai", int(filtered_df_status["selesai"].sum()), "✅")
    with col3:
        stat_card("On Progress", int(filtered_df_status["on_progress"].sum()), "⏳")
    with col4:
        stat_card("Dibatalkan", int(filtered_df_status["dibatalkan"].sum()), "❌")

    st.markdown("<br>", unsafe_allow_html=True)

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

    # Charts dalam 2 kolom
    col1, col2 = st.columns(2)

    with col1:
        fig_status_grouped = px.bar(
            status_melted,
            x="jenis sertifikasi",
            y="Jumlah",
            color="Status",
            title="DISTRIBUSI STATUS PER JENIS",
            barmode="group",
            height=350,
            color_discrete_map={
                "selesai": "#28a745",
                "on_progress": "#ffc107",
                "dibatalkan": "#dc3545",
                "pengajuan_awal": "#6c757d"
            }
        )
        fig_status_grouped.update_layout(xaxis_title="")
        st.plotly_chart(fig_status_grouped, use_container_width=True)

    with col2:
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
            title="CONVERSION FUNNEL",
            height=350
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

    # Table summary status (Top 10 saja)
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
        .head(10)
    )
    status_summary["completion_rate"] = (
        status_summary["selesai"] / status_summary["pendaftar"] * 100
    ).round(1)

    status_summary.columns = ["Instansi", "Pendaftar", "Selesai", "On Progress", "Dibatalkan", "Pengajuan Awal", "Completion Rate (%)"]
    st.dataframe(status_summary, use_container_width=True, hide_index=True, height=400)
