import streamlit as st
import pandas as pd
import altair as alt
import io
import sys
import numpy as np 
from decimal import Decimal

# --- Konfigurasi Halaman ---
st.set_page_config(layout="wide", page_title="Kalkulator Dana Pensiun Aktuaria", initial_sidebar_state="expanded")

# --- 1. INISIALISASI PARAMETER DEFAULT ---
if "widget_gender" not in st.session_state:
    st.session_state.widget_gender = "Laki-Laki"
    st.session_state.widget_entry_age = 30
    st.session_state.widget_valuation_age = 40
    st.session_state.widget_retirement_age = 65
    st.session_state.widget_initial_salary = 36_000_000
    st.session_state.widget_interest_rate = 4.0
    st.session_state.widget_benefit_prop = 2.5
    st.session_state.widget_salary_increase = 4.0

# --- Fungsi Reset ---
def reset_defaults():
    st.session_state.widget_gender = "Laki-Laki"
    st.session_state.widget_entry_age = 30
    st.session_state.widget_valuation_age = 40
    st.session_state.widget_retirement_age = 65
    st.session_state.widget_initial_salary = 36_000_000
    st.session_state.widget_interest_rate = 4.0
    st.session_state.widget_benefit_prop = 2.5
    st.session_state.widget_salary_increase = 4.0
    if st.session_state.widget_valuation_age < st.session_state.widget_entry_age:
         st.session_state.widget_valuation_age = st.session_state.widget_entry_age

# --- 2. FUNGSI MEMUAT DATA ---
@st.cache_data
def load_mortality_data():
    # Data TMI IV 2019 Laki-Laki (x, qx)
    data_laki_str = """x,qx
0,0.00524
1,0.00053
2,0.00042
3,0.00034
4,0.00029
5,0.00026
6,0.00023
7,0.00021
8,0.00020
9,0.00020
10,0.00019
11,0.00019
12,0.00019
13,0.00020
14,0.00023
15,0.00027
16,0.00031
17,0.00037
18,0.00043
19,0.00047
20,0.00049
21,0.00049
22,0.00049
23,0.00049
24,0.00050
25,0.00052
26,0.00055
27,0.00060
28,0.00065
29,0.00070
30,0.00075
31,0.00081
32,0.00087
33,0.00093
34,0.00099
35,0.00107
36,0.00116
37,0.00127
38,0.00139
39,0.00155
40,0.00173
41,0.00193
42,0.00216
43,0.00241
44,0.00270
45,0.00302
46,0.00338
47,0.00377
48,0.00418
49,0.00461
50,0.00508
51,0.00556
52,0.00609
53,0.00667
54,0.00727
55,0.00789
56,0.00847
57,0.00898
58,0.00939
59,0.00971
60,0.00999
61,0.01024
62,0.01046
63,0.01071
64,0.01104
65,0.01146
66,0.01199
67,0.01260
68,0.01329
69,0.01405
70,0.01485
71,0.01574
72,0.01670
73,0.01777
74,0.01895
75,0.02026
76,0.02369
77,0.02738
78,0.03130
79,0.03693
80,0.04518
81,0.05527
82,0.06732
83,0.08228
84,0.09478
85,0.10465
86,0.11533
87,0.12698
88,0.13947
89,0.15271
90,0.16659
91,0.17991
92,0.19390
93,0.20874
94,0.22451
95,0.24126
96,0.25715
97,0.27419
98,0.29249
99,0.31215
100,0.33331
101,0.35163
102,0.37132
103,0.39250
104,0.41527
105,0.43973
106,0.46602
107,0.49429
108,0.52467
109,0.55733
110,0.59244
111,1.0"""

    # Data TMI IV 2019 Perempuan (x, qx)
    data_perempuan_str = """x,qx
0,0.00266
1,0.00041
2,0.00031
3,0.00024
4,0.00021
5,0.00020
6,0.00022
7,0.00023
8,0.00022
9,0.00021
10,0.00019
11,0.00018
12,0.00020
13,0.00022
14,0.00023
15,0.00023
16,0.00024
17,0.00024
18,0.00025
19,0.00026
20,0.00027
21,0.00028
22,0.00030
23,0.00032
24,0.00034
25,0.00038
26,0.00042
27,0.00046
28,0.00049
29,0.00052
30,0.00056
31,0.00060
32,0.00064
33,0.00069
34,0.00074
35,0.00080
36,0.00086
37,0.00093
38,0.00100
39,0.00108
40,0.00118
41,0.00128
42,0.00141
43,0.00154
44,0.00169
45,0.00187
46,0.00209
47,0.00230
48,0.00253
49,0.00277
50,0.00305
51,0.00335
52,0.00368
53,0.00403
54,0.00442
55,0.00483
56,0.00524
57,0.00563
58,0.00601
59,0.00636
60,0.00671
61,0.00707
62,0.00746
63,0.00788
64,0.00833
65,0.00883
66,0.00940
67,0.01005
68,0.01076
69,0.01150
70,0.01229
71,0.01314
72,0.01406
73,0.01508
74,0.01620
75,0.01743
76,0.01879
77,0.02030
78,0.02326
79,0.02880
80,0.03569
81,0.04208
82,0.04907
83,0.05520
84,0.06086
85,0.06715
86,0.07318
87,0.08155
88,0.09045
89,0.10001
90,0.10913
91,0.11521
92,0.12499
93,0.13826
94,0.15451
95,0.17429
96,0.19155
97,0.20596
98,0.22227
99,0.23736
100,0.25810
101,0.28068
102,0.30562
103,0.33315
104,0.36369
105,0.39318
106,0.42883
107,0.46604
108,0.50427
109,0.54477
110,0.58702
111,1.0"""

    try:
        df_laki = pd.read_csv(io.StringIO(data_laki_str))
        df_perempuan = pd.read_csv(io.StringIO(data_perempuan_str))
        df_laki['qx'] = df_laki['qx'].clip(upper=1.0)
        df_perempuan['qx'] = df_perempuan['qx'].clip(upper=1.0)
        return df_laki, df_perempuan
    except Exception as e:
        st.error(f"Terjadi kesalahan internal saat membaca data TMI: {e}")
        return None, None

# --- 3. FUNGSI PERHITUNGAN KOMUTASI ---
@st.cache_data
def build_commutation_table(df_raw_mortality, i, l0=100000):
    if df_raw_mortality is None or 'qx' not in df_raw_mortality.columns:
        return pd.DataFrame() 
    df = df_raw_mortality.copy().set_index('x')
    df['px'] = 1 - df['qx']
    df['lx'] = 0.0
    df.loc[0, 'lx'] = float(l0)
    for x in range(1, len(df)):
        prev_x = df.index[x-1]
        curr_x = df.index[x]
        if prev_x in df.index and curr_x in df.index:
             df.loc[curr_x, 'lx'] = df.loc[prev_x, 'lx'] * df.loc[prev_x, 'px']
    v = Decimal(1) / (Decimal(1) + i)
    df['v^x'] = df.index.map(lambda x_val: v ** x_val)
    df['Dx'] = df['lx'].apply(Decimal) * df['v^x']
    df['Nx'] = Decimal(0)
    last_age = df.index.max()
    if last_age in df.index:
        df.loc[last_age, 'Nx'] = df.loc[last_age, 'Dx']
        for x in range(last_age - 1, -1, -1):
            if x in df.index and (x + 1) in df.index:
                df.loc[x, 'Nx'] = df.loc[x + 1, 'Nx'] + df.loc[x, 'Dx']
    return df.reset_index()

# --- 4. FUNGSI PERHITUNGAN AKTUARIA UTAMA ---
@st.cache_data
def calculate_actuarial_values_excel_logic(comm_table, x_entry, x_now, r, i, k, gaji_masuk, s):
    '''
    Menghitung nilai aktuaria sesuai Teori Skripsi dan Koreksi Excel.
    
    1. EAN NC: Dihitung pada x_entry (Level Cost), hasilnya tetap.
    2. AAN NC: Dihitung dinamis per tahun (PVFB sisa / Anuitas sisa).
    3. EAN AL: Metode Rasio (0 di awal).
    4. AAN AL: PVFB_x - PVFB_entry (Harus 0 di awal).
    '''
    if comm_table is None or comm_table.empty:
         return {}, pd.DataFrame() 

    # --- Mapping Data ---
    D = comm_table.set_index('x')['Dx'].to_dict()
    N = comm_table.set_index('x')['Nx'].to_dict()
    
    def get_D(x): return D.get(x, Decimal(0))
    def get_N(x): return N.get(x, Decimal(0))
    
    metrics = {}
    actuarial_data = []
    
    # --- Parameter Kunci ---
    D_entry = get_D(x_entry)
    N_entry = get_N(x_entry)
    D_r = get_D(r)
    N_r = get_N(r)

    # --- Hitung PVFB Awal ---
    Sr_minus_1 = ((Decimal(1) + s)**(r - x_entry - 1)) * gaji_masuk
    metrics['Sr_minus_1'] = Sr_minus_1
    B_r = k * Decimal(r - x_entry) * Sr_minus_1
    metrics['B_r'] = B_r
    
    if D_entry > 0:
        PVFB_at_entry = B_r * (D_r / D_entry)
    else:
        PVFB_at_entry = Decimal(0)
        
    metrics['PVFB_entry_AAN'] = PVFB_at_entry 

    # --- Hitung NC EAN (FIXED) ---
    if D_entry > 0:
        anuitas_entry = (N_entry - N_r) / D_entry
        if anuitas_entry > 0:
            NC_EAN_FIXED = PVFB_at_entry / anuitas_entry
        else:
            NC_EAN_FIXED = Decimal(0)
    else:
        NC_EAN_FIXED = Decimal(0)

    # --- Loop Perhitungan Tahunan ---
    for x_loop in range(x_entry, r):
        D_x = get_D(x_loop)
        N_x = get_N(x_loop)
        
        if D_x > 0:
            PVFB_x = B_r * (D_r / D_x)
            anuitas_x_term = (N_x - N_r) / D_x
        else:
            PVFB_x = Decimal(0)
            anuitas_x_term = Decimal(0)
        
        # 1. METODE EAN
        nc_ean_x = NC_EAN_FIXED 
        if (N_entry - N_r) != 0:
            ratio_progress = (N_entry - N_x) / (N_entry - N_r)
            al_ean_x = PVFB_x * ratio_progress
        else:
            al_ean_x = Decimal(0)

        # 2. METODE AAN
        if anuitas_x_term > 0:
            nc_aan_x = PVFB_at_entry / anuitas_x_term
        else:
            nc_aan_x = Decimal(0)
            
        # AL AAN: PVFB_x - PVFB_entry (Pasti 0 di x_entry)
        al_aan_x = PVFB_x - PVFB_at_entry

        actuarial_data.append({
            "Usia": x_loop,
            "Iuran Normal (EAN)": nc_ean_x, 
            "Iuran Normal (AAN)": nc_aan_x,
            "Kewajiban Aktuaria (EAN)": al_ean_x,
            "Kewajiban Aktuaria (AAN)": al_aan_x,
            "PVFB": PVFB_x
        })

    df_actuarial_full = pd.DataFrame(actuarial_data)
    
    # --- Metrics Dashboard ---
    metrics['PVFB_x_now'] = B_r * (get_D(r) / get_D(x_now)) if get_D(x_now) > 0 else Decimal(0)
    
    try:
        row_now = df_actuarial_full[df_actuarial_full['Usia'] == x_now]
        if not row_now.empty:
            metrics['NC_ean_now'] = row_now['Iuran Normal (EAN)'].values[0]
            metrics['AL_ean_now'] = row_now['Kewajiban Aktuaria (EAN)'].values[0]
            metrics['AL_aan_now'] = row_now['Kewajiban Aktuaria (AAN)'].values[0]
            metrics['NC_aan_x_now'] = row_now['Iuran Normal (AAN)'].values[0]
        else:
            raise IndexError
    except IndexError:
        metrics['NC_ean_now'] = Decimal(0)
        metrics['AL_ean_now'] = Decimal(0)
        metrics['AL_aan_now'] = Decimal(0)
        metrics['NC_aan_x_now'] = Decimal(0)

    # --- Nilai Akhir ---
    NA_ean = Decimal(0)
    NA_aan = Decimal(0)
    if not df_actuarial_full.empty:
        for index, row in df_actuarial_full.iterrows():
            umur_iuran = row['Usia']
            if umur_iuran < r:
                interest_factor = (Decimal(1) + i)**(r - umur_iuran)
                NA_ean += row['Iuran Normal (EAN)'] * interest_factor
                NA_aan += row['Iuran Normal (AAN)'] * interest_factor
    metrics['NA_ean_total'] = NA_ean
    metrics['NA_aan_total'] = NA_aan

    # --- Data Formula ---
    try:
        row_first = df_actuarial_full.iloc[0]
        row_last = df_actuarial_full.iloc[-1]
        x_first = int(row_first['Usia'])
        metrics['NA_ean_term_first'] = row_first['Iuran Normal (EAN)'] * ((Decimal(1) + i)**(r - x_first))
        metrics['NA_ean_term_last'] = row_last['Iuran Normal (EAN)'] * ((Decimal(1) + i)**1) 
        metrics['NA_aan_term_first'] = row_first['Iuran Normal (AAN)'] * ((Decimal(1) + i)**(r - x_first))
        metrics['NA_aan_term_last'] = row_last['Iuran Normal (AAN)'] * ((Decimal(1) + i)**1)
        if len(df_actuarial_full) > 1:
             row_second = df_actuarial_full.iloc[1]
             x_second = int(row_second['Usia'])
             metrics['NA_ean_term_second'] = row_second['Iuran Normal (EAN)'] * ((Decimal(1) + i)**(r - x_second))
             metrics['NA_aan_term_second'] = row_second['Iuran Normal (AAN)'] * ((Decimal(1) + i)**(r - x_second))
        else:
            metrics['NA_ean_term_second'] = Decimal(0)
            metrics['NA_aan_term_second'] = Decimal(0)
    except:
        pass 

    return metrics, df_actuarial_full

# --- 5. UI STREAMLIT ---
df_laki_raw, df_perempuan_raw = load_mortality_data()

st.title("📊 Dashboard Perhitungan Dana Pensiun")
st.caption("Dashboard interaktif untuk menghitung nilai-nilai aktuaria program dana pensiun.")

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ Parameter Simulasi")
    st.subheader("👤 Data Peserta")
    jenis_kelamin = st.selectbox("Jenis Kelamin", options=["Perempuan", "Laki-Laki"], key="widget_gender") 
    col1, col2 = st.columns(2)
    with col1:
        x_entry = st.number_input("Usia Masuk (e)", min_value=18, max_value=60, step=1, help="Usia saat peserta terdaftar program.", key="widget_entry_age") 
    with col2:
        x_now_min = st.session_state.get('widget_entry_age', 18) 
        x_now = st.number_input("Usia Valuasi (x)", min_value=x_now_min, max_value=64, step=1, help="Usia saat perhitungan dilakukan.", key="widget_valuation_age")
    st.subheader("💰 Asumsi Ekonomi & Pensiun")
    r = st.number_input("Usia Pensiun (r)", min_value=55, max_value=65, step=1, help="Usia pensiun normal.", key="widget_retirement_age")
    gaji_masuk = st.number_input("Gaji Pokok Awal (Rp) (Se)", min_value=1_000_000, step=1_000_000, format="%d", help="Gaji tahunan saat usia masuk (e).", key="widget_initial_salary") 
    i_percent = st.slider("Suku Bunga (i) %", min_value=0.0, max_value=15.0, step=0.1, help="Asumsi tingkat hasil investasi per tahun.", key="widget_interest_rate") 
    s_percent = st.slider("Kenaikan Gaji (s) %", min_value=0.0, max_value=15.0, step=0.1, help="Asumsi kenaikan gaji tahunan.", key="widget_salary_increase") 
    k_percent = st.slider("Proporsi Gaji (k) %", min_value=0.0, max_value=10.0, step=0.1, help="Persentase dari gaji yang menjadi manfaat pensiun tahunan.", key="widget_benefit_prop") 

    i = Decimal(str(i_percent)) / Decimal(100)
    s = Decimal(str(s_percent)) / Decimal(100)
    k = Decimal(str(k_percent)) / Decimal(100)
    st.divider()
    st.button("Reset ke Default", on_click=reset_defaults, use_container_width=True)

    current_x_now = st.session_state.get('widget_valuation_age', 40)
    current_r = st.session_state.get('widget_retirement_age', 65)
    valid = True
    if current_x_now >= current_r:
        st.error("Usia Valuasi (x) harus lebih kecil dari Usia Pensiun (r).")
        valid = False
    if current_x_now < x_entry: 
        st.error("Usia Valuasi (x) tidak boleh lebih kecil dari Usia Masuk (e).")
        valid = False
    if current_r <= x_entry: 
        st.error("Usia Pensiun (r) harus lebih besar dari Usia Masuk (e).")
        valid = False
    if not valid: st.stop()

# --- 6. PROSES UTAMA ---
if df_laki_raw is not None and df_perempuan_raw is not None:
    # Ambil State
    jenis_kelamin_state = st.session_state.widget_gender
    x_entry_state = st.session_state.widget_entry_age
    x_now_state = st.session_state.widget_valuation_age
    r_state = st.session_state.widget_retirement_age
    gaji_masuk_state = Decimal(st.session_state.widget_initial_salary)
    i_state = Decimal(str(st.session_state.widget_interest_rate)) / Decimal(100)
    k_state = Decimal(str(st.session_state.widget_benefit_prop)) / Decimal(100)
    s_state = Decimal(str(st.session_state.widget_salary_increase)) / Decimal(100)
    
    df_raw = df_perempuan_raw if jenis_kelamin_state == "Perempuan" else df_laki_raw
    comm_table = build_commutation_table(df_raw, i_state, l0=100000)

    metrics, df_actuarial_full = calculate_actuarial_values_excel_logic(
        comm_table, x_entry_state, x_now_state, r_state, i_state, k_state, gaji_masuk_state, s_state
    )

    # Unwrap Metrics
    B_r = metrics.get('B_r', Decimal(0))
    Sr_minus_1 = metrics.get('Sr_minus_1', Decimal(0))
    PVFB_x_now = metrics.get('PVFB_x_now', Decimal(0))
    PVFB_entry_AAN = metrics.get('PVFB_entry_AAN', Decimal(0))
    NC_ilp_now = metrics.get('NC_ean_now', Decimal(0))
    NC_aan_x_now = metrics.get('NC_aan_x_now', Decimal(0))
    NA_ean_total = metrics.get('NA_ean_total', Decimal(0))
    NA_aan_total = metrics.get('NA_aan_total', Decimal(0))
    AL_ilp_x_now = metrics.get('AL_ean_now', Decimal(0))
    AL_aan_x_now = metrics.get('AL_aan_now', Decimal(0))
    
    # Komutasi Values untuk Tampilan
    if comm_table is not None and not comm_table.empty:
        comm_table_dict_D = comm_table.set_index('x')['Dx'].to_dict()
        comm_table_dict_N = comm_table.set_index('x')['Nx'].to_dict()
        Dx_now = comm_table_dict_D.get(x_now_state, Decimal(0))
        Nx_now = comm_table_dict_N.get(x_now_state, Decimal(0))
        Dx_entry = comm_table_dict_D.get(x_entry_state, Decimal(0))
        Nx_entry = comm_table_dict_N.get(x_entry_state, Decimal(0))
        Dx_r = comm_table_dict_D.get(r_state, Decimal(0))
        Nx_r = comm_table_dict_N.get(r_state, Decimal(0))
    else:
        Dx_now, Nx_now, Dx_entry, Nx_entry, Dx_r, Nx_r = (Decimal(0),) * 6

    # Helper Format
    def format_rp(val): return f"Rp {Decimal(str(val)):,.2f}" 
    def format_calc(val): return f"{Decimal(str(val)):,.7f}"
    def format_latex_num(val): return f"{Decimal(str(val)):.7f}"

    tab_summary, tab_formula, tab_commutation = st.tabs(["📊 Ringkasan & Detail", "🔬 Formula Perhitungan", "🧮 Tabel Komutasi"])

    # --- TAB SUMMARY ---
    with tab_summary:
        st.header(f"📈 Ringkasan Hasil Perhitungan (Usia Valuasi: {x_now_state})")
        st.caption(f"Perhitungan menggunakan metode **Entry Age Normal (EAN)** dan **Attained Age Normal (AAN)**.")
        st.divider()
        st.subheader("Nilai Aktuaria Utama")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Manfaat Pensiun Tahunan (Br)", format_rp(B_r), help=f"Dihitung: {k_state*100:.1f}% x {r_state-x_entry_state} thn x Gaji Akhir.")
            st.metric(f"Nilai Sekarang Manfaat (PVFB)", format_rp(PVFB_x_now), help=f"Present value manfaat pensiun di usia {x_now_state}.")
        with col_s2:
            st.metric("Nilai Akhir Total Iuran EAN", format_rp(NA_ean_total), help=f"Akumulasi iuran EAN hingga usia {r_state}.")
            st.metric("Nilai Akhir Total Iuran AAN", format_rp(NA_aan_total), help=f"Akumulasi iuran AAN hingga usia {r_state}.")
        
        st.divider()
        st.subheader(f"Detail Metode di Usia {x_now_state}")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### Entry Age Normal (EAN)")
            st.metric(f"Iuran Normal (NC)", format_rp(NC_ilp_now), help="Iuran tahunan pada usia valuasi (Tetap).") 
            st.metric(f"Kewajiban Aktuaria (AL)", format_rp(AL_ilp_x_now), help="Target dana terkumpul saat ini.")
        with col_m2:
            st.markdown("##### Attained Age Normal (AAN)")
            st.metric(f"Iuran Normal (NC)", format_rp(NC_aan_x_now), help="Iuran tahunan saat ini (Naik tiap tahun).")
            st.metric(f"Kewajiban Aktuaria (AL)", format_rp(AL_aan_x_now), help="Target dana terkumpul saat ini.")

        st.divider()
        st.subheader("📊 Visualisasi & Detail Perhitungan")
        
        if not df_actuarial_full.empty:
            df_chart_data = df_actuarial_full.astype(float)
            st.markdown("##### Perbandingan Pola Iuran Normal Tahunan")
            df_chart_nc = df_chart_data[['Usia', 'Iuran Normal (AAN)', 'Iuran Normal (EAN)']].melt('Usia', var_name='Metode', value_name='Iuran Tahunan')
            chart_nc = alt.Chart(df_chart_nc).mark_line(point=True).encode(
                x=alt.X('Usia', axis=alt.Axis(title='Usia Peserta')), 
                y=alt.Y('Iuran Tahunan', axis=alt.Axis(title='Iuran Tahunan (Rp)')), 
                color='Metode',
                tooltip=['Usia', 'Metode', alt.Tooltip('Iuran Tahunan', format=',.2f')]
            ).interactive()
            st.altair_chart(chart_nc, use_container_width=True)

            st.markdown("##### Perbandingan Grafik Kewajiban Aktuaria")
            df_chart_al = df_chart_data[['Usia', 'Kewajiban Aktuaria (AAN)', 'Kewajiban Aktuaria (EAN)']].melt('Usia', var_name='Metode', value_name='Kewajiban Aktuaria')
            chart_al = alt.Chart(df_chart_al).mark_line(point=True).encode(
                x=alt.X('Usia', axis=alt.Axis(title='Usia Peserta')), 
                y=alt.Y('Kewajiban Aktuaria', axis=alt.Axis(title='Kewajiban Aktuaria (Rp)')), 
                color='Metode',
                tooltip=['Usia', 'Metode', alt.Tooltip('Kewajiban Aktuaria', format=',.2f')]
            ).interactive()
            st.altair_chart(chart_al, use_container_width=True)

            st.markdown("##### Tabel Rinci Perhitungan per Usia")
            cols_to_show = ['PVFB', 'Iuran Normal (EAN)', 'Kewajiban Aktuaria (EAN)', 'Iuran Normal (AAN)', 'Kewajiban Aktuaria (AAN)']
            df_display = df_actuarial_full.set_index('Usia')[cols_to_show]
            def highlight_row(row):
                if row.name == x_now_state: return ['background-color: #2b6aca; color: white;'] * len(row) 
                return [''] * len(row) 
            st.dataframe(df_display.style.apply(highlight_row, axis=1).format("Rp {:,.2f}"), use_container_width=True, height=600)

    # --- ISI TAB FORMULA ---
    with tab_formula:
        st.header("🔬 Detail Formula Perhitungan")
        st.info(f"Asumsi: Suku Bunga (i) = {i_percent_state}%, Kenaikan Gaji (s) = {s_percent_state}%.")
        
        st.subheader("1. Manfaat Pensiun Tahunan ($B_r$)")
        st.metric("Hasil", format_rp(B_r))
        st.latex(rf"B_r = k \times (r-e) \times S_{{r-1}} = {format_calc(B_r)}")
        
        st.divider()
        st.subheader("2. Iuran Normal (NC)")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**EAN (Level Cost)**")
            st.metric("NC EAN", format_rp(NC_ilp_now))
            st.latex(r"^{EAN}NC = \frac{^{r}(PVFB)_{e}}{\ddot{a}_{e:\overline{r-e|}}}")
        with col2:
            st.markdown("**AAN (Dinamis)**")
            st.metric("NC AAN", format_rp(NC_aan_x_now))
            st.latex(r"^{AAN}NC_x = \frac{^{r}(PVFB)_{e}}{\ddot{a}_{x:\overline{r-x|}}}")

        st.divider()
        st.subheader("3. Kewajiban Aktuaria (AL)")
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("**EAN (Metode Rasio)**")
            st.metric("AL EAN", format_rp(AL_ilp_x_now))
            st.latex(r"^{EAN}AL_x = {}^{r}(PVFB)_{x} \times \frac{N_e - N_x}{N_e - N_r}")
        with col4:
            st.markdown("**AAN (Metode Selisih)**")
            st.metric("AL AAN", format_rp(AL_aan_x_now))
            st.latex(r"^{AAN}AL_x = {}^{r}(PVFB)_{x} - {}^{r}(PVFB)_{e}")

    # --- ISI TAB KOMUTASI ---
    with tab_commutation:
        st.header("🧮 Tabel Komutasi")
        if comm_table is not None:
            st.dataframe(comm_table[['x', 'lx', 'Dx', 'Nx']].set_index('x').style.format("{:,.2f}"), use_container_width=True)
else:
    st.error("Gagal memuat data.")