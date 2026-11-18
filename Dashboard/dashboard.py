from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

sns.set_theme(style="whitegrid")
st.set_page_config(page_title="Dashboard Bike Sharing", page_icon="🚲", layout="wide")

BASE_DIR = Path(__file__).parent
WARNA = {"Hari Kerja": "#1f77b4", "Akhir Pekan/Libur": "#ff7f0e"}
URUTAN_CUACA = ["Cerah", "Berkabut/Berawan", "Hujan/Salju Ringan"]
URUTAN_MUSIM = ["Spring", "Summer", "Fall", "Winter"]
URUTAN_KATEGORI = ["Rendah", "Sedang", "Tinggi"]


@st.cache_data
def load_data():
    hour_df = pd.read_csv(BASE_DIR / "main_data.csv", parse_dates=["dteday"])
    day_df = pd.read_csv(BASE_DIR / "day_data.csv", parse_dates=["dteday"])
    return hour_df, day_df


hour_df, day_df = load_data()

# ---------------- Sidebar: filter rentang tanggal
st.sidebar.header("Filter Data")
tgl_min, tgl_max = day_df["dteday"].min().date(), day_df["dteday"].max().date()
rentang = st.sidebar.date_input("Rentang tanggal", value=(tgl_min, tgl_max), min_value=tgl_min, max_value=tgl_max)

if isinstance(rentang, (tuple, list)) and len(rentang) == 2:
    mulai, selesai = rentang
else:
    st.sidebar.info("Pilih tanggal awal dan tanggal akhir.")
    st.stop()

mulai, selesai = pd.Timestamp(mulai), pd.Timestamp(selesai)
hour_f = hour_df[(hour_df["dteday"] >= mulai) & (hour_df["dteday"] <= selesai)]
day_f = day_df[(day_df["dteday"] >= mulai) & (day_df["dteday"] <= selesai)].copy()

# ---------------- Judul dan ringkasan
st.title("🚲 Dashboard Analisis Bike Sharing")
st.caption("Capital Bikeshare, Washington D.C. | Data 2011–2012")

kol1, kol2, kol3 = st.columns(3)
kol1.metric("Total penyewaan", f"{day_f['cnt'].sum():,.0f}")
kol2.metric("Rata-rata per hari", f"{day_f['cnt'].mean():,.0f}")
kol3.metric("Jumlah hari", f"{day_f['dteday'].nunique():,}")

# ---------------- Pertanyaan 1
st.subheader("Pertanyaan 1: Pola penyewaan per jam, hari kerja vs akhir pekan/libur")
pola_jam = hour_f.groupby(["hr", "tipe_hari"])["cnt"].mean().unstack()

fig, ax = plt.subplots(figsize=(12, 5))
for tipe in pola_jam.columns:
    ax.plot(pola_jam.index, pola_jam[tipe], marker="o", linewidth=2.2, color=WARNA[tipe], label=tipe)
    jam_puncak = pola_jam[tipe].idxmax()
    ax.annotate(f"Puncak jam {jam_puncak:02d}.00 ({pola_jam[tipe].max():.0f})",
                xy=(jam_puncak, pola_jam[tipe].max()), xytext=(jam_puncak, pola_jam[tipe].max() + 45),
                ha="center", color=WARNA[tipe], fontsize=10, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=WARNA[tipe]))
ax.set_title("Rata-rata Penyewaan Sepeda per Jam", fontsize=13, fontweight="bold", loc="left")
ax.set_xlabel("Jam dalam sehari")
ax.set_ylabel("Rata-rata penyewaan per jam")
ax.set_xticks(range(0, 24))
ax.set_ylim(0, pola_jam.max().max() * 1.25)
ax.grid(axis="x", visible=False)
ax.legend(title="Tipe hari", loc="upper left")
sns.despine()
st.pyplot(fig)

# ---------------- Pertanyaan 2
st.subheader("Pertanyaan 2: Pengaruh cuaca dan musim terhadap penyewaan harian")
cuaca_stat = day_f.groupby("cuaca")["cnt"].agg(jumlah_hari="count", rata2="mean").reindex(URUTAN_CUACA).dropna()
musim_stat = day_f.groupby("musim")["cnt"].agg(jumlah_hari="count", rata2="mean").reindex(URUTAN_MUSIM).dropna()
rata_total = day_f["cnt"].mean()

fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
bar1 = axes[0].bar(cuaca_stat.index, cuaca_stat["rata2"], color="#9aa5b1")
bar1[cuaca_stat["rata2"].values.argmax()].set_color("#2ca02c")
axes[0].set_title("Berdasarkan Kondisi Cuaca", fontsize=12, fontweight="bold")
axes[0].set_xlabel("Kondisi cuaca")
axes[0].set_ylabel("Rata-rata penyewaan per hari")
for batang, n in zip(bar1, cuaca_stat["jumlah_hari"]):
    axes[0].text(batang.get_x() + batang.get_width() / 2, batang.get_height() + 80,
                 f"{batang.get_height():,.0f}\n(n={int(n)} hari)", ha="center", fontsize=10)

bar2 = axes[1].bar(musim_stat.index, musim_stat["rata2"], color="#9aa5b1")
bar2[musim_stat["rata2"].values.argmax()].set_color("#2ca02c")
axes[1].set_title("Berdasarkan Musim", fontsize=12, fontweight="bold")
axes[1].set_xlabel("Musim")
for batang in bar2:
    axes[1].text(batang.get_x() + batang.get_width() / 2, batang.get_height() + 80,
                 f"{batang.get_height():,.0f}", ha="center", fontsize=10)

for ax in axes:
    ax.axhline(rata_total, color="red", linestyle="--", linewidth=1, zorder=0, label=f"Rata-rata keseluruhan: {rata_total:,.0f}")
    ax.set_ylim(0, max(cuaca_stat["rata2"].max(), musim_stat["rata2"].max()) * 1.3)
    ax.grid(axis="x", visible=False)
axes[1].legend(loc="upper left")
sns.despine()
plt.tight_layout()
st.pyplot(fig)

# ---------------- Analisis lanjutan
st.subheader("Analisis Lanjutan: Manual Grouping")
kiri, kanan = st.columns(2)

with kiri:
    hour_f = hour_f.copy()
    hour_f["periode"] = pd.cut(hour_f["hr"], bins=[-1, 5, 9, 15, 19, 23],
                               labels=["Dini Hari (00-05)", "Pagi (06-09)", "Siang (10-15)", "Sore (16-19)", "Malam (20-23)"])
    periode_stat = hour_f.groupby(["periode", "tipe_hari"], observed=True)["cnt"].mean().unstack()
    fig, ax = plt.subplots(figsize=(7, 5))
    periode_stat.plot(kind="bar", ax=ax, color=[WARNA[c] for c in periode_stat.columns], width=0.75)
    ax.set_title("Rata-rata Penyewaan per Jam menurut Periode Waktu", fontsize=12, fontweight="bold", loc="left")
    ax.set_xlabel("Periode waktu")
    ax.set_ylabel("Rata-rata penyewaan per jam")
    ax.tick_params(axis="x", rotation=20)
    ax.legend(title="Tipe hari")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)

with kanan:
    day_f["kategori_permintaan"] = pd.cut(day_f["cnt"], bins=[0, 3000, 6000, 10000], labels=URUTAN_KATEGORI)
    komposisi = (pd.crosstab(day_f["musim"], day_f["kategori_permintaan"], normalize="index")
                 .reindex(index=URUTAN_MUSIM, columns=URUTAN_KATEGORI).dropna(how="all") * 100)
    fig, ax = plt.subplots(figsize=(7, 5))
    komposisi.plot(kind="bar", stacked=True, ax=ax, color=["#d9534f", "#f0ad4e", "#5cb85c"])
    ax.set_title("Kategori Permintaan Harian per Musim", fontsize=12, fontweight="bold", loc="left")
    ax.set_xlabel("Musim")
    ax.set_ylabel("Persentase hari (%)")
    ax.tick_params(axis="x", rotation=0)
    ax.legend(title="Kategori permintaan", bbox_to_anchor=(1.02, 1), loc="upper left")
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)

st.caption("Kategori permintaan: Rendah (< 3.000), Sedang (3.000–6.000), Tinggi (> 6.000 penyewaan per hari).")