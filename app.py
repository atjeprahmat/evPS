import warnings

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

warnings.filterwarnings('ignore')


def konversi_skor(teks):
    # Handle NaN, None, dan empty values
    if pd.isna(teks) or teks == '':
        return None

    teks = str(teks).lower().strip()

    if any(x in teks for x in ['sangat memuaskan', 'sangat mudah', 'sangat baik', 'sangat membantu', 'sangat profesional', 'sangat efektif']):
        return 4
    elif any(x in teks for x in ['cukup memuaskan', 'cukup mudah', 'cukup baik', 'cukup membantu', 'cukup profesional', 'cukup efektif']):
        return 3
    elif any(x in teks for x in ['kurang memuaskan', 'kurang mudah', 'kurang baik', 'kurang membantu', 'kurang profesional', 'kurang efektif']):
        return 2
    elif any(x in teks for x in ['tidak memuaskan', 'sangat sulit', 'tidak ada pemantauan', 'tidak ada bantuan', 'tidak profesional', 'tidak efektif']):
        return 1
    else:
        return None


def kategori_kepuasan(skor):
    if pd.isna(skor):
        return "Data tidak tersedia"
    if skor >= 3.5:
        return "Sangat Memuaskan"
    if skor >= 3.0:
        return "Cukup Baik"
    if skor >= 2.0:
        return "Perlu Perhatian"
    return "Kritis"


def cari_kolom_apresiasi(df):
    prioritas_keywords = [
        "hal apa saja",
        "sangat memuaskan",
        "dipertahankan",
        "layanan sekolah di rayon"
    ]

    for col in df.columns:
        nama_kolom = str(col).lower().strip()
        if all(keyword in nama_kolom for keyword in ["sangat memuaskan", "dipertahankan"]):
            return col
        if sum(keyword in nama_kolom for keyword in prioritas_keywords) >= 3:
            return col

    if len(df.columns) > 8:
        return df.columns[8]
    return None


def petakan_apresiasi_ke_indikator(teks, keyword_map):
    if pd.isna(teks) or str(teks).strip() == "":
        return []

    teks = str(teks).lower().strip()
    indikator_ditemukan = []
    for indikator, keywords in keyword_map.items():
        if any(keyword in teks for keyword in keywords):
            indikator_ditemukan.append(indikator)

    if not indikator_ditemukan:
        return ["Belum Terpetakan"]
    return indikator_ditemukan


def susun_rencana_tindak_lanjut(rata_rata_df, df_summary_percentages, ringkasan_apresiasi=None):
    rencana_map = {
        "1. Interaksi & Responsivitas": {
            "Rencana Perbaikan": "Meningkatkan kecepatan dan kualitas respons layanan kepada orang tua dan siswa secara lebih konsisten.",
            "Strategi/Metode": "Menyusun standar waktu respons, melakukan briefing layanan secara berkala, dan memantau tindak lanjut komunikasi melalui kanal resmi.",
            "Dukungan yang Dibutuhkan": "Komitmen guru/staf, SOP komunikasi layanan, serta media komunikasi resmi yang aktif dan terpantau."
        },
        "2. Kemudahan Akses Konsultasi": {
            "Rencana Perbaikan": "Mempermudah akses konsultasi antara orang tua, siswa, dan pihak sekolah/rayon.",
            "Strategi/Metode": "Menetapkan jadwal konsultasi yang terpublikasi dengan baik, menyediakan jalur konsultasi daring/luring, dan memperjelas alur penghubung.",
            "Dukungan yang Dibutuhkan": "Jadwal layanan yang konsisten, admin penghubung, dan sarana komunikasi yang mudah diakses."
        },
        "3. Pendampingan Karakter": {
            "Rencana Perbaikan": "Memperkuat kualitas pendampingan karakter siswa secara terstruktur dan berkelanjutan.",
            "Strategi/Metode": "Melaksanakan mentoring rutin, memantau perkembangan karakter siswa, dan menyampaikan umpan balik berkala kepada orang tua.",
            "Dukungan yang Dibutuhkan": "Keterlibatan wali kelas/guru pembina, instrumen pemantauan karakter, dan kerja sama aktif dari orang tua."
        },
        "4. Penyelesaian Kendala": {
            "Rencana Perbaikan": "Meningkatkan kecepatan dan ketepatan penanganan kendala yang dihadapi siswa maupun orang tua.",
            "Strategi/Metode": "Menyusun alur penanganan masalah, menetapkan PIC yang jelas, dan membuat pemantauan status penyelesaian setiap kasus.",
            "Dukungan yang Dibutuhkan": "SOP penanganan kendala, koordinasi lintas pihak, dan dokumentasi tindak lanjut yang rapi."
        },
        "5. Administrasi Keuangan": {
            "Rencana Perbaikan": "Meningkatkan ketertiban, kejelasan, dan transparansi layanan administrasi keuangan.",
            "Strategi/Metode": "Menyajikan rincian tagihan yang mudah dipahami, mengirim pengingat pembayaran secara berkala, dan memperbaiki sistem pencatatan administrasi.",
            "Dukungan yang Dibutuhkan": "Admin keuangan yang responsif, sistem pencatatan yang tertib, serta format laporan/tagihan yang standar."
        },
        "6. Efektivitas Informasi": {
            "Rencana Perbaikan": "Meningkatkan kejelasan, kelengkapan, dan ketepatan waktu penyampaian informasi kepada orang tua dan siswa.",
            "Strategi/Metode": "Menyusun format informasi baku, menjadwalkan publikasi informasi penting, dan melakukan pengecekan keterbacaan pesan sebelum dikirim.",
            "Dukungan yang Dibutuhkan": "Template informasi resmi, koordinasi antarpetugas, dan media penyampaian informasi yang konsisten."
        }
    }

    penekanan_map = {
        "Kritis": {
            "prefix_rencana": "Menjadi prioritas utama untuk segera dibenahi melalui langkah perbaikan yang lebih intensif. ",
            "prefix_strategi": "Pelaksanaan perlu dilakukan dalam jangka dekat dengan pemantauan ketat. ",
            "prefix_keberhasilan": "Keberhasilan awal ditandai oleh perbaikan yang tampak nyata dalam waktu relatif cepat. ",
            "prefix_dukungan": "Diperlukan dukungan manajerial dan operasional secara penuh. "
        },
        "Perlu Perhatian": {
            "prefix_rencana": "Perlu diperkuat secara terarah agar mutu layanan tidak terus berada pada tingkat sedang. ",
            "prefix_strategi": "Pelaksanaan perlu difokuskan pada perbaikan proses yang paling sering dirasakan pengguna layanan. ",
            "prefix_keberhasilan": "Keberhasilan diharapkan terlihat dari peningkatan persepsi positif responden pada evaluasi berikutnya. ",
            "prefix_dukungan": "Diperlukan dukungan teknis dan koordinasi pelaksana yang konsisten. "
        },
        "Cukup Baik": {
            "prefix_rencana": "Perlu ditingkatkan secara selektif agar capaian indikator bergerak menuju kategori sangat memuaskan. ",
            "prefix_strategi": "Pelaksanaan dapat difokuskan pada penyempurnaan mutu layanan dan konsistensi implementasi. ",
            "prefix_keberhasilan": "Keberhasilan ditunjukkan oleh penguatan hasil yang sudah baik menjadi lebih optimal. ",
            "prefix_dukungan": "Diperlukan dukungan penguatan mutu dan monitoring berkala. "
        },
        "Sangat Memuaskan": {
            "prefix_rencana": "Tetap perlu dipertahankan sambil dilakukan penyempurnaan terbatas pada aspek yang masih dapat dioptimalkan. ",
            "prefix_strategi": "Pelaksanaan diarahkan pada pemeliharaan mutu dan pembakuan praktik baik. ",
            "prefix_keberhasilan": "Keberhasilan ditandai oleh kestabilan capaian tinggi pada periode berikutnya. ",
            "prefix_dukungan": "Diperlukan dukungan untuk menjaga konsistensi mutu layanan. "
        }
    }

    prioritas_df = (
        rata_rata_df.copy()
        .sort_values('Skor Rata-rata', ascending=True)
        .head(min(3, len(rata_rata_df)))
        .reset_index(drop=True)
    )

    summary_lookup = {}
    if not df_summary_percentages.empty:
        summary_lookup = df_summary_percentages.set_index('Indikator Layanan').to_dict('index')

    apresiasi_lookup = {}
    if ringkasan_apresiasi is not None and not ringkasan_apresiasi.empty:
        apresiasi_bersih = ringkasan_apresiasi[
            ringkasan_apresiasi['Indikator Layanan'] != "Belum Terpetakan"
        ].copy()
        if not apresiasi_bersih.empty:
            apresiasi_lookup = apresiasi_bersih.set_index('Indikator Layanan').to_dict('index')

    rencana_rows = []
    for _, row in prioritas_df.iterrows():
        indikator = row['Indikator Layanan']
        template = rencana_map.get(indikator)
        kategori = row.get('Kategori', kategori_kepuasan(row['Skor Rata-rata']))
        penekanan = penekanan_map.get(kategori, penekanan_map["Perlu Perhatian"])
        if template:
            distribusi = summary_lookup.get(indikator, {})
            skor_1 = distribusi.get('Skor 1 (%)', 0.0)
            skor_2 = distribusi.get('Skor 2 (%)', 0.0)
            skor_4 = distribusi.get('Skor 4 (%)', 0.0)
            data_kosong = distribusi.get('Data Kosong (%)', 0.0)
            proporsi_rendah = round(skor_1 + skor_2, 2)

            target_skor = min(
                4.0,
                max(
                    round(row['Skor Rata-rata'] + 0.35, 2),
                    3.0 if kategori == "Kritis" else 3.25 if kategori == "Perlu Perhatian" else 3.5
                )
            )
            target_proporsi_rendah = max(round(proporsi_rendah - 15, 2), 10.0 if proporsi_rendah > 10 else 0.0)
            target_skor_4 = min(round(max(skor_4 + 10, 25.0), 2), 100.0)

            catatan_apresiasi = "Belum tampak apresiasi dominan pada komentar terbuka untuk indikator ini."
            aspek_pertahankan = "Belum ada tema dominan dari indikator 7 yang secara spesifik terpetakan pada indikator ini."
            if indikator in apresiasi_lookup:
                apresiasi = apresiasi_lookup[indikator]
                catatan_apresiasi = (
                    f"Komentar terbuka juga menunjukkan kekuatan yang perlu dipertahankan pada indikator ini, "
                    f"dengan {apresiasi['Jumlah Komentar Positif']} komentar positif "
                    f"({apresiasi['Persentase dari Respons Apresiasi (%)']:.2f}% dari respons apresiasi)."
                )
                contoh_komentar = str(apresiasi.get('Contoh Komentar', '')).strip()
                aspek_pertahankan = (
                    f"Aspek yang sudah dinilai sangat memuaskan dan perlu dipertahankan adalah "
                    f"tema {indikator.lower()} dengan dukungan {apresiasi['Jumlah Komentar Positif']} komentar positif "
                    f"({apresiasi['Persentase dari Respons Apresiasi (%)']:.2f}%)."
                )
                if contoh_komentar and contoh_komentar.lower() != "nan":
                    aspek_pertahankan += f" Contoh masukan responden: {contoh_komentar}."

            catatan_kelengkapan = ""
            if data_kosong > 0:
                catatan_kelengkapan = (
                    f" Kelengkapan isian juga perlu dijaga karena masih terdapat {data_kosong:.2f}% data kosong."
                )

            rencana_rows.append({
                "Prioritas": (
                    f"Skor {row['Skor Rata-rata']:.2f} | Skor 1-2: {proporsi_rendah:.2f}%"
                ),
                "Indikator yang perlu ditingkatkan": indikator,
                "Aspek yang Tetap Dipertahankan (Indikator 7)": aspek_pertahankan,
                "Rencana Perbaikan": (
                    f"{penekanan['prefix_rencana']}Berdasarkan isian Excel, indikator ini memperoleh "
                    f"skor rata-rata {row['Skor Rata-rata']:.2f} dengan proporsi skor 1-2 sebesar "
                    f"{proporsi_rendah:.2f}%. Karena itu, fokus perbaikan diarahkan untuk {template['Rencana Perbaikan'].lower()}"
                ),
                "Strategi/Metode": (
                    f"{penekanan['prefix_strategi']}{template['Strategi/Metode']} "
                    f"Dalam pelaksanaannya, sekolah perlu mempertahankan kekuatan yang muncul pada indikator 7 "
                    f"sambil memperbaiki aspek yang masih lemah. {catatan_apresiasi}"
                ),
                "Indikator Keberhasilan": (
                    f"{penekanan['prefix_keberhasilan']}Target perbaikan pada evaluasi berikutnya adalah "
                    f"skor rata-rata minimal {target_skor:.2f}, proporsi skor 1-2 turun dari "
                    f"{proporsi_rendah:.2f}% menjadi paling tinggi {target_proporsi_rendah:.2f}%, "
                    f"serta skor 4 meningkat dari {skor_4:.2f}% menjadi minimal {target_skor_4:.2f}%."
                ),
                "Dukungan yang Dibutuhkan": (
                    f"{penekanan['prefix_dukungan']}{template['Dukungan yang Dibutuhkan']}{catatan_kelengkapan}"
                )
            })

    return pd.DataFrame(rencana_rows)


def main():
    st.set_page_config(
        page_title="Aplikasi Analisis Kepuasan Layanan Rayon",
        page_icon=":bar_chart:",
        layout="wide")

    st.title("Aplikasi Analisis Kepuasan Layanan Rayon")
    st.subheader("Unggah File Excel")
    st.caption("Pilih file Excel (.xlsx) pada bagian ini agar langsung terlihat saat aplikasi dibuka di desktop maupun mobile.")
    uploaded_file = st.file_uploader("Pilih file Excel (.xlsx)", type=["xlsx"])
    st.markdown("---")

    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file, sheet_name='Sheet1')

            if df.empty:
                st.error("File Excel kosong. Silakan unggah file dengan data.")
                return

            st.success(f"File berhasil diunggah! ({len(df)} baris data, {len(df.columns)} kolom)")

            if len(df.columns) < 8:
                st.warning(f"File hanya memiliki {len(df.columns)} kolom. Direkomendasikan minimal 8 kolom.")

            kolom_pertanyaan = df.columns[2:8]
            nama_indikator = [
                "1. Interaksi & Responsivitas",
                "2. Kemudahan Akses Konsultasi",
                "3. Pendampingan Karakter",
                "4. Penyelesaian Kendala",
                "5. Administrasi Keuangan",
                "6. Efektivitas Informasi"
            ]

            df_skor = pd.DataFrame()
            for i, col in enumerate(kolom_pertanyaan):
                df_skor[nama_indikator[i]] = df[col].apply(konversi_skor)

            rata_rata = df_skor.mean().reset_index()
            rata_rata.columns = ['Indikator Layanan', 'Skor Rata-rata']
            if rata_rata['Skor Rata-rata'].dropna().empty:
                st.error("Tidak ada skor valid yang bisa dianalisis. Periksa kembali isi jawaban pada kolom pertanyaan.")
                return

            rata_rata['Kategori'] = rata_rata['Skor Rata-rata'].apply(kategori_kepuasan)
            skor_keseluruhan = df_skor.stack().mean()
            rata_rata_valid = rata_rata.dropna(subset=['Skor Rata-rata'])
            indikator_terbaik = rata_rata_valid.loc[rata_rata_valid['Skor Rata-rata'].idxmax()]
            indikator_terendah = rata_rata_valid.loc[rata_rata_valid['Skor Rata-rata'].idxmin()]
            ranking_teratas = rata_rata_valid.sort_values('Skor Rata-rata', ascending=False).head(min(3, len(rata_rata_valid)))
            ranking_terbawah = rata_rata_valid.sort_values('Skor Rata-rata', ascending=True).head(min(3, len(rata_rata_valid)))

            st.markdown("---")
            st.header("Analisis Skor Kepuasan Layanan")
            col1, col2, col3 = st.columns(3)
            col1.metric("Skor Kepuasan Keseluruhan", f"{skor_keseluruhan:.2f}", kategori_kepuasan(skor_keseluruhan))
            col2.metric("Indikator Terbaik", f"{indikator_terbaik['Skor Rata-rata']:.2f}", indikator_terbaik['Indikator Layanan'])
            col3.metric("Indikator Terendah", f"{indikator_terendah['Skor Rata-rata']:.2f}", indikator_terendah['Indikator Layanan'])

            col4, col5 = st.columns(2)
            with col4:
                st.subheader("3 Indikator Terbaik")
                st.dataframe(
                    ranking_teratas[['Indikator Layanan', 'Skor Rata-rata', 'Kategori']].reset_index(drop=True),
                    use_container_width=True
                )
            with col5:
                st.subheader("3 Indikator Terendah")
                st.dataframe(
                    ranking_terbawah[['Indikator Layanan', 'Skor Rata-rata', 'Kategori']].reset_index(drop=True),
                    use_container_width=True
                )

            st.dataframe(rata_rata, use_container_width=True)

            fig_bar, ax_bar = plt.subplots(figsize=(12, 6))
            colors = [
                '#d4af37' if x >= 3.5 else '#4CAF50' if x >= 3.0 else '#FFC107' if x >= 2.0 else '#f44336'
                for x in rata_rata['Skor Rata-rata']
            ]
            sns.barplot(
                data=rata_rata,
                x='Skor Rata-rata',
                y='Indikator Layanan',
                palette=colors,
                hue='Indikator Layanan',
                dodge=False,
                legend=False,
                ax=ax_bar
            )
            ax_bar.set_title(
                'Rata-rata Skor Kepuasan Layanan Rayon (Skala 1-4)',
                fontsize=14,
                fontweight='bold',
                pad=15
            )
            ax_bar.set_xlabel('Skor Rata-rata (1 = Terburuk, 4 = Terbaik)', fontsize=12)
            ax_bar.set_ylabel('')
            ax_bar.set_xlim(0, 4.3)
            ax_bar.grid(axis='x', alpha=0.3, linestyle='--')

            for index, value in enumerate(rata_rata['Skor Rata-rata']):
                ax_bar.text(value + 0.05, index, f'{value:.2f}', va='center', fontsize=12, fontweight='bold')

            plt.tight_layout()
            st.pyplot(fig_bar)
            plt.close(fig_bar)

            st.subheader("Kesimpulan Analisis Indikator Layanan:")
            for _, row in rata_rata.iterrows():
                skor = row['Skor Rata-rata']
                if skor >= 3.5:
                    status = "SANGAT MEMUASKAN (Pertahankan!)"
                elif skor >= 3.0:
                    status = "CUKUP BAIK (Tingkatkan sedikit lagi)"
                elif skor >= 2.0:
                    status = "PERLU PERHATIAN (Evaluasi)"
                else:
                    status = "KRITIS (Perbaikan Segera)"
                st.write(f"- {row['Indikator Layanan']}: {skor:.2f} -> {status}")

            st.markdown("---")
            st.header("Ringkasan Distribusi Persentase Skor")
            summary_percentages = []
            total_responden = len(df_skor)

            for col_name in df_skor.columns:
                valid_scores = df_skor[col_name].dropna()
                percentages = (
                    valid_scores.value_counts(normalize=True)
                    .reindex([4, 3, 2, 1], fill_value=0)
                    .mul(100)
                    .round(2)
                )
                data_kosong_percentage = (
                    round(((total_responden - len(valid_scores)) / total_responden) * 100, 2)
                    if total_responden > 0 else 0.0
                )

                indicator_summary = {
                    'Indikator Layanan': col_name,
                    'Skor 4 (%)': percentages[4],
                    'Skor 3 (%)': percentages[3],
                    'Skor 2 (%)': percentages[2],
                    'Skor 1 (%)': percentages[1],
                    'Data Kosong (%)': data_kosong_percentage
                }
                summary_percentages.append(indicator_summary)

            df_summary_percentages = pd.DataFrame(summary_percentages)
            st.dataframe(df_summary_percentages, use_container_width=True)

            st.subheader("Visualisasi Distribusi Skor per Indikator")
            distribusi_chart = (
                df_summary_percentages[
                    ['Indikator Layanan', 'Skor 1 (%)', 'Skor 2 (%)', 'Skor 3 (%)', 'Skor 4 (%)']
                ]
                .set_index('Indikator Layanan')
            )
            fig_dist, ax_dist = plt.subplots(figsize=(12, 6))
            distribusi_chart.plot(
                kind='barh',
                stacked=True,
                color=['#f44336', '#FFC107', '#4CAF50', '#d4af37'],
                ax=ax_dist
            )
            ax_dist.set_title(
                'Distribusi Persentase Skor per Indikator',
                fontsize=14,
                fontweight='bold',
                pad=15
            )
            ax_dist.set_xlabel('Persentase Responden (%)', fontsize=12)
            ax_dist.set_ylabel('')
            ax_dist.set_xlim(0, 100)
            ax_dist.grid(axis='x', alpha=0.3, linestyle='--')
            ax_dist.legend(title='Skor', bbox_to_anchor=(1.02, 1), loc='upper left')
            plt.tight_layout()
            st.pyplot(fig_dist)
            plt.close(fig_dist)

            st.markdown("---")
            st.header("Analisis Apresiasi Layanan dari Kolom Nomor 7")
            kolom_apresiasi = cari_kolom_apresiasi(df)
            ringkasan_apresiasi = pd.DataFrame()
            keyword_indikator = {
                "1. Interaksi & Responsivitas": [
                    "ramah", "cepat tanggap", "tanggap", "responsif", "respon", "komunikatif",
                    "komunikasi", "sopan", "pelayanan", "sigap"
                ],
                "2. Kemudahan Akses Konsultasi": [
                    "mudah dihubungi", "mudah di kontak", "mudah diakses", "konsultasi", "akses",
                    "tersedia", "siap membantu", "mudah", "terjangkau"
                ],
                "3. Pendampingan Karakter": [
                    "pendampingan", "karakter", "pembinaan", "motivasi", "perhatian", "akhlak",
                    "adab", "sikap", "pembentukan"
                ],
                "4. Penyelesaian Kendala": [
                    "solusi", "menyelesaikan", "penyelesaian", "kendala", "masalah", "membantu",
                    "bantuan", "menangani", "problem"
                ],
                "5. Administrasi Keuangan": [
                    "keuangan", "administrasi", "pembayaran", "tagihan", "transparan", "biaya",
                    "pencatatan", "uang sekolah"
                ],
                "6. Efektivitas Informasi": [
                    "informasi", "jelas", "update", "pemberitahuan", "pengumuman", "koordinasi",
                    "terinformasi", "detail", "tepat waktu"
                ]
            }

            if kolom_apresiasi is not None:
                df_apresiasi = df[[kolom_apresiasi]].copy()
                df_apresiasi.columns = ['Komentar Apresiasi']
                df_apresiasi['Komentar Apresiasi'] = df_apresiasi['Komentar Apresiasi'].astype(str).str.strip()
                df_apresiasi = df_apresiasi[
                    df_apresiasi['Komentar Apresiasi'].notna() &
                    (df_apresiasi['Komentar Apresiasi'] != "") &
                    (df_apresiasi['Komentar Apresiasi'].str.lower() != "nan")
                ]

                if not df_apresiasi.empty:
                    df_apresiasi['Indikator Terdeteksi'] = df_apresiasi['Komentar Apresiasi'].apply(
                        lambda teks: petakan_apresiasi_ke_indikator(teks, keyword_indikator)
                    )

                    hasil_explode = df_apresiasi.explode('Indikator Terdeteksi')
                    jumlah_respons_apresiasi = len(df_apresiasi)

                    ringkasan_apresiasi = (
                        hasil_explode.groupby('Indikator Terdeteksi')
                        .size()
                        .reset_index(name='Jumlah Komentar Positif')
                        .rename(columns={'Indikator Terdeteksi': 'Indikator Layanan'})
                    )
                    ringkasan_apresiasi['Persentase dari Respons Apresiasi (%)'] = (
                        ringkasan_apresiasi['Jumlah Komentar Positif']
                        .div(jumlah_respons_apresiasi)
                        .mul(100)
                        .round(2)
                    )
                    ringkasan_apresiasi = ringkasan_apresiasi.sort_values(
                        'Jumlah Komentar Positif',
                        ascending=False
                    ).reset_index(drop=True)

                    contoh_komentar = (
                        hasil_explode.groupby('Indikator Terdeteksi')['Komentar Apresiasi']
                        .apply(lambda komentar: " | ".join(pd.Series(komentar).drop_duplicates().head(2)))
                        .reset_index()
                        .rename(columns={
                            'Indikator Terdeteksi': 'Indikator Layanan',
                            'Komentar Apresiasi': 'Contoh Komentar'
                        })
                    )
                    ringkasan_apresiasi = ringkasan_apresiasi.merge(
                        contoh_komentar,
                        on='Indikator Layanan',
                        how='left'
                    )

                    indikator_apresiasi_utama = ringkasan_apresiasi.iloc[0]
                    col_ap1, col_ap2 = st.columns(2)
                    col_ap1.metric("Jumlah Respons Apresiasi", jumlah_respons_apresiasi)
                    col_ap2.metric(
                        "Tema Positif Terbanyak",
                        indikator_apresiasi_utama['Indikator Layanan'],
                        f"{indikator_apresiasi_utama['Persentase dari Respons Apresiasi (%)']:.2f}%"
                    )
                    st.caption(
                        "Catatan: satu komentar dapat terpetakan ke lebih dari satu indikator "
                        "jika mengandung beberapa kata kunci sekaligus."
                    )

                    st.info(
                        f"Kolom apresiasi yang dianalisis: {kolom_apresiasi}"
                    )
                    st.dataframe(ringkasan_apresiasi, use_container_width=True)

                    ringkasan_chart = ringkasan_apresiasi[
                        ringkasan_apresiasi['Indikator Layanan'] != "Belum Terpetakan"
                    ]
                    if not ringkasan_chart.empty:
                        fig_apresiasi, ax_apresiasi = plt.subplots(figsize=(12, 6))
                        sns.barplot(
                            data=ringkasan_chart,
                            x='Jumlah Komentar Positif',
                            y='Indikator Layanan',
                            palette='Blues_r',
                            hue='Indikator Layanan',
                            dodge=False,
                            legend=False,
                            ax=ax_apresiasi
                        )
                        ax_apresiasi.set_title(
                            'Tema Positif yang Paling Sering Muncul pada Kolom Nomor 7',
                            fontsize=14,
                            fontweight='bold',
                            pad=15
                        )
                        ax_apresiasi.set_xlabel('Jumlah Komentar Positif', fontsize=12)
                        ax_apresiasi.set_ylabel('')
                        ax_apresiasi.grid(axis='x', alpha=0.3, linestyle='--')

                        for index, value in enumerate(ringkasan_chart['Jumlah Komentar Positif']):
                            ax_apresiasi.text(value + 0.05, index, str(value), va='center', fontsize=11)

                        plt.tight_layout()
                        st.pyplot(fig_apresiasi)
                        plt.close(fig_apresiasi)

                    st.subheader("Narasi Singkat")
                    if indikator_apresiasi_utama['Indikator Layanan'] == "Belum Terpetakan":
                        st.write(
                            "Mayoritas komentar positif belum cocok dengan kamus keyword saat ini, sehingga "
                            "perlu penyesuaian kata kunci agar pemetaan indikator lebih akurat."
                        )
                    else:
                        st.write(
                            f"Indikator yang paling sering diapresiasi adalah "
                            f"{indikator_apresiasi_utama['Indikator Layanan']} dengan "
                            f"{indikator_apresiasi_utama['Jumlah Komentar Positif']} komentar positif "
                            f"atau {indikator_apresiasi_utama['Persentase dari Respons Apresiasi (%)']:.2f}% "
                            f"dari seluruh respons apresiasi yang terisi."
                        )
                else:
                    st.info("Kolom nomor 7 ditemukan, tetapi belum ada isi komentar yang bisa dianalisis.")
            else:
                st.warning(
                    "Kolom nomor 7 tidak ditemukan otomatis. Pastikan judul kolom mengandung kata "
                    "'sangat memuaskan' atau 'dipertahankan'."
                )

            st.markdown("---")
            st.header("Rencana Tindak Lanjut")
            st.caption(
                "Tabel berikut disusun otomatis berdasarkan tiga indikator dengan skor rata-rata "
                "paling rendah, sehingga setiap isian difokuskan pada capaian yang paling kecil "
                "serta menggunakan bukti dari isian Excel seperti skor, distribusi jawaban, dan komentar terbuka "
                "yang relevan. Temuan dari pertanyaan indikator 7 juga digabungkan untuk menunjukkan "
                "aspek layanan yang sudah sangat memuaskan dan tetap perlu dipertahankan."
            )
            df_rencana_tindak_lanjut = susun_rencana_tindak_lanjut(
                rata_rata_valid,
                df_summary_percentages,
                ringkasan_apresiasi
            )
            st.dataframe(df_rencana_tindak_lanjut, use_container_width=True, hide_index=True)

        except FileNotFoundError:
            st.error("File tidak ditemukan. Silakan unggah file Excel terlebih dahulu.")
        except pd.errors.ParserError as e:
            st.error(f"Error membaca file Excel: {str(e)}")
            st.error("Pastikan file dalam format .xlsx yang valid.")
        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {str(e)}")
            st.error("Petunjuk:")
            st.error("1. Gunakan file Excel (.xlsx) dengan Sheet1")
            st.error("2. Kolom pertanyaan harus berada di indeks 2-7 (dengan jawaban Likert skala 1-4)")
            st.error("3. Pastikan tidak ada karakter spesial yang tidak valid dalam data")


if __name__ == '__main__':
    main()
