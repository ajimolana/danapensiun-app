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
    """Mengembalikan semua input ke nilai defaultnya."""
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
    """Memuat data TMI 2023 untuk Laki-laki dan Perempuan dari string."""
 
    # Data TMI 2023 Laki-Laki (x, qx)
    data_laki_str = """x,qx
0,0.00979
1,0.00253
2,0.00108
3,0.0007
4,0.0006
5,0.00058
6,0.00057
7,0.00057
8,0.00055
9,0.00052
10,0.00051
11,0.0005
12,0.00052
13,0.00054
14,0.00058
15,0.00062
16,0.00066
17,0.0007
18,0.00073
19,0.00078
20,0.00082
21,0.00087
22,0.00091
23,0.00097
24,0.00102
25,0.00108
26,0.00113
27,0.0012
28,0.00126
29,0.00133
30,0.00139
31,0.00147
32,0.00155
33,0.00163
34,0.00173
35,0.00185
36,0.00198
37,0.00212
38,0.00228
39,0.00247
40,0.00268
41,0.00291
42,0.00317
43,0.00348
44,0.00382
45,0.00418
46,0.00459
47,0.00506
48,0.00561
49,0.00622
50,0.00693
51,0.00774
52,0.00863
53,0.00953
54,0.01046
55,0.0114
56,0.01236
57,0.01332
58,0.01431
59,0.01541
60,0.0166
61,0.01787
62,0.0192
63,0.02059
64,0.02196
65,0.02327
66,0.02457
67,0.0259
68,0.02728
69,0.02873
70,0.0303
71,0.032
72,0.03376
73,0.03546
74,0.0371
75,0.03871
76,0.04032
77,0.04193
78,0.04367
79,0.04568
80,0.04811
81,0.05106
82,0.05464
83,0.0589
84,0.06387
85,0.06953
86,0.07592
87,0.0831
88,0.09118
89,0.1003
90,0.11059
91,0.1222
92,0.13522
93,0.14971
94,0.1657
95,0.18317
96,0.20208
97,0.22241
98,0.24408
99,0.26701
100,0.29112
101,0.3163
102,0.34242
103,0.36936
104,0.39697
105,0.42507
106,0.45349
107,0.48203
108,0.51049
109,0.53865
110,0.56627
111,1.0"""

    # Data TMI 2023 Perempuan (x, qx)
    data_perempuan_str = """x,qx
0,0.00788
1,0.0021
2,0.0009
3,0.00058
4,0.00049
5,0.00047
6,0.00047
7,0.00047
8,0.00045
9,0.00044
10,0.00043
11,0.00044
12,0.00045
13,0.00047
14,0.0005
15,0.00053
16,0.00056
17,0.00059
18,0.00063
19,0.00067
20,0.00072
21,0.00077
22,0.00082
23,0.00087
24,0.00092
25,0.00097
26,0.00102
27,0.00107
28,0.00113
29,0.00118
30,0.00123
31,0.00129
32,0.00135
33,0.00142
34,0.00149
35,0.00158
36,0.00168
37,0.00179
38,0.00192
39,0.00206
40,0.00223
41,0.00242
42,0.00263
43,0.00288
44,0.00316
45,0.00346
46,0.00379
47,0.00418
48,0.00461
49,0.00508
50,0.0056
51,0.00618
52,0.0068
53,0.00741
54,0.00804
55,0.00871
56,0.0094
57,0.01008
58,0.01078
59,0.01152
60,0.01231
61,0.0131
62,0.0139
63,0.01471
64,0.0155
65,0.01623
66,0.01695
67,0.0177
68,0.01847
69,0.01926
70,0.02012
71,0.02107
72,0.02208
73,0.02311
74,0.02416
75,0.02527
76,0.02643
77,0.02766
78,0.02902
79,0.03062
80,0.03251
81,0.0347
82,0.0372
83,0.03999
84,0.04304
85,0.0464
86,0.05013
87,0.05437
88,0.05927
89,0.06502
90,0.07182
91,0.07987
92,0.08933
93,0.10035
94,0.11302
95,0.1274
96,0.1435
97,0.16135
98,0.18096
99,0.20235
100,0.22557
101,0.25065
102,0.27761
103,0.30649
104,0.33727
105,0.36994
106,0.40447
107,0.44081
108,0.47886
109,0.51853
110,0.55968
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

# --- 3. FUNGSI PERHITUNGAN ---
@st.cache_data
def build_commutation_table(df_raw_mortality, i, l0=100000):
    '''Membangun tabel komutasi (lx, Dx, Nx) dari data qx TMI. Menggunakan Decimal untuk presisi.'''
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

@st.cache_data
def calculate_actuarial_values_excel_logic(comm_table, x_entry, x_now, r, i, k, gaji_masuk, s):
    '''
    Menghitung nilai aktuaria dengan logika FINAL sesuai data Excel user:
    
    1. EAN (Entry Age Normal):
       - NC: Dihitung di Usia Masuk (Level Cost).
       - AL: Metode Rasio (Prospektif).
       
    2. AAN (Attained Age Normal) - Sesuai Pola CSV:
       - NC: PVFB_entry / Anuitas_sisa (Mendanai beban awal di sisa waktu).
       - AL: PVFB_x - PVFB_entry (Kewajiban adalah kenaikan PVFB di atas beban awal).
    '''
    if comm_table is None or comm_table.empty:
         return {}, pd.DataFrame() 

    # --- 1. Mapping Data Komutasi ---
    D = comm_table.set_index('x')['Dx'].to_dict()
    N = comm_table.set_index('x')['Nx'].to_dict()
    
    def get_D(x): return D.get(x, Decimal(0))
    def get_N(x): return N.get(x, Decimal(0))
    
    metrics = {}
    actuarial_data = []
    
    # --- 2. Parameter Kunci ---
    D_entry = get_D(x_entry)
    N_entry = get_N(x_entry)
    D_r = get_D(r)
    N_r = get_N(r)

    # --- 3. Hitung PVFB Awal (Kunci Perhitungan) ---
    # Gaji diproyeksikan: S_{r-1} = S_e * (1+s)^(r-e-1)
    Sr_minus_1 = ((Decimal(1) + s)**(r - x_entry - 1)) * gaji_masuk
    metrics['Sr_minus_1'] = Sr_minus_1
    
    # Manfaat Pensiun
    B_r = k * Decimal(r - x_entry) * Sr_minus_1
    metrics['B_r'] = B_r
    
    # PVFB pada Usia Masuk (PVFB_e)
    # Ini adalah konstanta penting untuk kedua metode (EAN & AAN versi Excel ini)
    if D_entry > 0:
        PVFB_at_entry = B_r * (D_r / D_entry)
    else:
        PVFB_at_entry = Decimal(0)
        
    metrics['PVFB_entry_AAN'] = PVFB_at_entry 

    # --- 4. HITUNG NC EAN (FIXED) ---
    # Rumus: PVFB_e / Anuitas_e
    if D_entry > 0:
        anuitas_entry = (N_entry - N_r) / D_entry
        # Implementasi rumus gambar user (PVFB_x * Dx/De ...) pada x=e hasilnya sama dengan ini:
        if anuitas_entry > 0:
            NC_EAN_FIXED = PVFB_at_entry / anuitas_entry
        else:
            NC_EAN_FIXED = Decimal(0)
    else:
        NC_EAN_FIXED = Decimal(0)

    # --- 5. LOOP PERHITUNGAN TAHUNAN ---
    for x_loop in range(x_entry, r):
        
        D_x = get_D(x_loop)
        N_x = get_N(x_loop)
        
        # Variabel Dinamis Tahun Berjalan
        if D_x > 0:
            PVFB_x = B_r * (D_r / D_x)
            anuitas_x_term = (N_x - N_r) / D_x
        else:
            PVFB_x = Decimal(0)
            anuitas_x_term = Decimal(0)
        
        # ==========================================
        # METODE EAN (Entry Age Normal)
        # ==========================================
        # NC: Tetap (Level Cost)
        nc_ean_x = NC_EAN_FIXED 
        
        # AL: Metode Rasio
        if (N_entry - N_r) != 0:
            ratio_progress = (N_entry - N_x) / (N_entry - N_r)
            al_ean_x = PVFB_x * ratio_progress
        else:
            al_ean_x = Decimal(0)

        # ==========================================
        # METODE AAN (Attained Age Normal) - UPDATED
        # ==========================================
        # NC AAN: PVFB_entry / Anuitas_sisa
        # (Analisis CSV: NC naik karena Anuitas_sisa mengecil, tapi pembilang tetap PVFB_entry)
        if anuitas_x_term > 0:
            nc_aan_x = PVFB_at_entry / anuitas_x_term
        else:
            nc_aan_x = Decimal(0)
            
        # AL AAN: PVFB_x - PVFB_entry
        # (Analisis CSV: AL tidak nol, tapi selisih antara kewajiban kini dan awal)
        al_aan_x = PVFB_x - PVFB_at_entry

        # Simpan Data
        actuarial_data.append({
            "Usia": x_loop,
            "Iuran Normal (EAN)": nc_ean_x, 
            "Iuran Normal (AAN)": nc_aan_x,
            "Kewajiban Aktuaria (EAN)": al_ean_x,
            "Kewajiban Aktuaria (AAN)": al_aan_x,
            "PVFB": PVFB_x
        })

    df_actuarial_full = pd.DataFrame(actuarial_data)
    
    # --- 6. Output Dashboard (Usia Valuasi) ---
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

    # --- 7. Nilai Akhir (Future Value) ---
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

    # --- 8. Data Formula Visual ---
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

# --- 4. UI STREAMLIT ---

# Muat data di awal
df_laki_raw, df_perempuan_raw = load_mortality_data()

st.title("📊 Dashboard Perhitungan Dana Pensiun")
st.caption("Dashboard interaktif untuk menghitung nilai-nilai aktuaria program dana pensiun.")

# --- Sidebar untuk Input ---
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

    # Ubah ke Decimal untuk perhitungan. Gunakan str() untuk presisi
    i = Decimal(str(i_percent)) / Decimal(100)
    s = Decimal(str(s_percent)) / Decimal(100)
    k = Decimal(str(k_percent)) / Decimal(100)

    st.divider()
    st.button("Reset ke Default", on_click=reset_defaults, use_container_width=True)

    current_x_now = st.session_state.get('widget_valuation_age', 40)
    current_r = st.session_state.get('widget_retirement_age', 65)
    
    # Validasi usia
    valid = True
    if current_x_now >= current_r:
        st.error("Usia Valuasi (x) harus lebih kecil dari Usia Pensiun (r).")
        valid = False
    if current_x_now < x_entry: # Menggunakan x_entry dari widget, bukan state
        st.error("Usia Valuasi (x) tidak boleh lebih kecil dari Usia Masuk (e).")
        valid = False
    if current_r <= x_entry: # Menggunakan x_entry dari widget, bukan state
        st.error("Usia Pensiun (r) harus lebih besar dari Usia Masuk (e).")
        valid = False
    
    if not valid:
        st.stop()

# --- 5. PROSES PERHITUNGAN UTAMA ---

if df_laki_raw is not None and df_perempuan_raw is not None:
    
    # Ambil nilai dari session_state
    jenis_kelamin_state = st.session_state.widget_gender
    x_entry_state = st.session_state.widget_entry_age
    x_now_state = st.session_state.widget_valuation_age
    r_state = st.session_state.widget_retirement_age
    gaji_masuk_state = st.session_state.widget_initial_salary
    i_percent_state = st.session_state.widget_interest_rate
    k_percent_state = st.session_state.widget_benefit_prop
    s_percent_state = st.session_state.widget_salary_increase
    
    # Konversi ke Decimal untuk akurasi
    i_state = Decimal(str(i_percent_state)) / Decimal(100)
    k_state = Decimal(str(k_percent_state)) / Decimal(100)
    s_state = Decimal(str(s_percent_state)) / Decimal(100)
    gaji_masuk_state = Decimal(gaji_masuk_state)
    
    df_raw = df_perempuan_raw if jenis_kelamin_state == "Perempuan" else df_laki_raw
    
    comm_table = build_commutation_table(df_raw, i_state, l0=100000)

    metrics, df_actuarial_full = calculate_actuarial_values_excel_logic(
        comm_table, x_entry_state, x_now_state, r_state, i_state, k_state, gaji_masuk_state, s_state
    )

    # Metrics
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
    
    NA_ean_term_first = metrics.get('NA_ean_term_first', Decimal(0))
    NA_ean_term_second = metrics.get('NA_ean_term_second', Decimal(0))
    NA_ean_term_last = metrics.get('NA_ean_term_last', Decimal(0))
    NA_aan_term_first = metrics.get('NA_aan_term_first', Decimal(0))
    NA_aan_term_second = metrics.get('NA_aan_term_second', Decimal(0))
    NA_aan_term_last = metrics.get('NA_aan_term_last', Decimal(0))

    # Nilai Komutasi
    if comm_table is not None and not comm_table.empty:
        comm_table_dict_D = comm_table.set_index('x')['Dx'].to_dict()
        comm_table_dict_N = comm_table.set_index('x')['Nx'].to_dict()
        
        Dx_now = comm_table_dict_D.get(x_now_state, Decimal(0))
        Nx_now = comm_table_dict_N.get(x_now_state, Decimal(0))
        Dx_entry = comm_table_dict_D.get(x_entry_state, Decimal(0))
        Nx_entry = comm_table_dict_N.get(x_entry_state, Decimal(0))
        Dx_r = comm_table_dict_D.get(r_state, Decimal(0))
        Nx_r = comm_table_dict_N.get(r_state, Decimal(0))
        
        anuitas_now_formula = (Nx_now - Nx_r) / Dx_now if Dx_now > 0 else Decimal(0)
        anuitas_entry_formula = (Nx_entry - Nx_r) / Dx_entry if Dx_entry > 0 else Decimal(0)
        anuitas_entry_to_now_formula = (Nx_entry - Nx_now) / Dx_entry if Dx_entry > 0 else Decimal(0)
    else:
        Dx_now, Nx_now, Dx_entry, Nx_entry, Dx_r, Nx_r = (Decimal(0),) * 6
        anuitas_now_formula, anuitas_entry_formula, anuitas_entry_to_now_formula = (Decimal(0),) * 3

    # --- 6. TAMPILKAN OUTPUT ---
    
    # Helper function untuk format Rupiah (presisi 2) - UNTUK UI
    def format_rp(val):
        if not isinstance(val, Decimal):
            val = Decimal(str(val))
        return f"Rp {val:,.2f}" 
    
    # Helper function untuk format angka (presisi 7) - UNTUK TAB FORMULA
    def format_calc(val):
        if not isinstance(val, Decimal):
            val = Decimal(str(val))
        return f"{val:,.7f}"
    
    # Helper function untuk format angka tanpa koma (untuk LaTeX)
    def format_latex_num(val):
         if not isinstance(val, Decimal):
            val = Decimal(str(val))
         # Hasilkan string angka dengan 7 desimal tanpa koma
         return f"{val:.7f}"

    tab_summary, tab_formula, tab_commutation = st.tabs([
        "📊 Ringkasan & Detail", 
        "🔬 Formula Perhitungan",
        "🧮 Tabel Komutasi" 
        ])

    # --- ISI TAB SUMMARY ---
    with tab_summary:
        st.header(f"📈 Ringkasan Hasil Perhitungan (Usia Valuasi: {x_now_state})")
        st.caption(f"Perhitungan menggunakan metode **Entry Age Normal (EAN)** dan **Attained Age Normal (AAN)**.")
        st.divider()

        st.subheader("Nilai Aktuaria Utama")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Manfaat Pensiun Tahunan (Br)", format_rp(B_r), help=f"Dihitung: {k_state*100:.1f}% x {r_state-x_entry_state} thn x Gaji Akhir Proyeksi ({format_rp(Sr_minus_1)})")
            st.metric(f"Nilai Sekarang Manfaat (PVFB)", format_rp(PVFB_x_now), help=f"Present value manfaat pensiun di usia {x_now_state}.")
        with col_s2:
            st.metric("Nilai Akhir Total Iuran EAN", format_rp(NA_ean_total), help=f"Akumulasi iuran EAN hingga usia {r_state}.")
            st.metric("Nilai Akhir Total Iuran AAN", format_rp(NA_aan_total), help=f"Akumulasi iuran AAN hingga usia {r_state}.")
        
        st.divider()
        st.subheader(f"Detail Metode di Usia {x_now_state}")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.markdown("##### Entry Age Normal (EAN)")
            st.metric(f"Iuran Normal (NC)", format_rp(NC_ilp_now), help="Iuran tahunan pada usia valuasi.") 
            st.metric(f"Kewajiban Aktuaria (AL)", format_rp(AL_ilp_x_now), help="Target dana terkumpul saat ini.")
        with col_m2:
            st.markdown("##### Attained Age Normal (AAN)")
            st.metric(f"Iuran Normal (NC)", format_rp(NC_aan_x_now), help="Iuran tahunan saat ini.")
            st.metric(f"Kewajiban Aktuaria (AL)", format_rp(AL_aan_x_now), help="Target dana terkumpul saat ini.")

        st.divider()

        st.subheader("📊 Visualisasi & Detail Perhitungan")
        
        if not df_actuarial_full.empty:
            df_chart_data = df_actuarial_full.astype(float)
            
            st.markdown("##### Perbandingan Pola Iuran Normal Tahunan")
            df_chart_nc = df_chart_data[['Usia', 'Iuran Normal (AAN)', 'Iuran Normal (EAN)']].melt('Usia', var_name='Metode', value_name='Iuran Tahunan')
            
            try:
                y_max = df_chart_nc['Iuran Tahunan'].max()
                y_min = df_chart_nc['Iuran Tahunan'].min() 
                y_padding = (y_max - y_min) * 0.1 
                y_domain = [max(0, y_min - y_padding), y_max + y_padding] 
            except Exception: 
                 y_domain = [0, 1000000] 
            
            chart_nc = alt.Chart(df_chart_nc).mark_line(point=True).encode(
                x=alt.X('Usia', axis=alt.Axis(title='Usia Peserta')), 
                y=alt.Y('Iuran Tahunan', axis=alt.Axis(title='Iuran Tahunan (Rp)'), scale=alt.Scale(domain=y_domain, clamp=True)), 
                color='Metode',
                tooltip=[
                    alt.Tooltip('Usia'), 
                    alt.Tooltip('Metode'), 
                    alt.Tooltip('Iuran Tahunan', format=',.2f', title='Iuran (Rp)')
                ]
            ).properties(
                title='Perkembangan Iuran Normal Tahunan (EAN vs AAN)'
            ).interactive()
            st.altair_chart(chart_nc, use_container_width=True)

            st.markdown("##### Perbandingan Grafik Kewajiban Aktuaria")
            df_chart_al = df_chart_data[['Usia', 'Kewajiban Aktuaria (AAN)', 'Kewajiban Aktuaria (EAN)']].melt('Usia', var_name='Metode', value_name='Kewajiban Aktuaria')

            try:
                y_max_al = df_chart_al['Kewajiban Aktuaria'].max()
                y_min_al = df_chart_al['Kewajiban Aktuaria'].min() 
                y_padding_al = (y_max_al - y_min_al) * 0.1 
                y_domain_al = [max(0, y_min_al - y_padding_al), y_max_al + y_padding_al] 
            except Exception: 
                 y_domain_al = [0, 1000000]
            
            chart_al = alt.Chart(df_chart_al).mark_line(point=True).encode(
                x=alt.X('Usia', axis=alt.Axis(title='Usia Peserta')), 
                y=alt.Y('Kewajiban Aktuaria', axis=alt.Axis(title='Kewajiban Aktuaria (Rp)'), scale=alt.Scale(domain=y_domain_al, clamp=True)), 
                color='Metode',
                tooltip=[
                    alt.Tooltip('Usia'), 
                    alt.Tooltip('Metode'), 
                    alt.Tooltip('Kewajiban Aktuaria', format=',.2f', title='Kewajiban (Rp)')
                ]
            ).properties(
                title='Perkembangan Kewajiban Aktuaria (EAN vs AAN)'
            ).interactive()
            st.altair_chart(chart_al, use_container_width=True)

            # --- Ringkasan Interpretasi ---
            st.subheader("💡 Ringkasan Interpretasi")
            
            # Interpretasi Pola Grafik
            interpretation_graph = "Seperti terlihat di grafik, iuran **AAN** (putih) dimulai lebih rendah namun akan **meningkat tajam** menjelang usia pensiun. Iuran **EAN** (biru) memiliki pola kenaikan yang **lebih landai dan stabil**."
            
            # Interpretasi Nilai Akhir
            if NA_ean_total < NA_aan_total:
                interpretation_na = f"Metode **EAN** lebih menguntungkan bagi **peserta**, karena total iuran yang dibayarkan hingga pensiun **lebih rendah** ({format_rp(NA_ean_total)}) dibandingkan AAN ({format_rp(NA_aan_total)})."
            else:
                interpretation_na = f"Metode **AAN** lebih menguntungkan bagi **peserta**, karena total iuran yang dibayarkan hingga pensiun **lebih rendah** ({format_rp(NA_aan_total)}) dibandingkan EAN ({format_rp(NA_ean_total)})."

            # Interpretasi Kewajiban Aktuaria
            if AL_ilp_x_now > AL_aan_x_now:
                interpretation_al = f"Metode **EAN** menargetkan dana terkumpul (Kewajiban Aktuaria) **lebih besar** saat ini ({format_rp(AL_ilp_x_now)}) dibandingkan AAN ({format_rp(AL_aan_x_now)}). Ini menunjukkan pendanaan yang lebih cepat dan lebih aman dari sisi **penyelenggara**."
            else:
                interpretation_al = f"Metode **AAN** menargetkan dana terkumpul (Kewajiban Aktuaria) **lebih besar** saat ini ({format_rp(AL_aan_x_now)}) dibandingkan EAN ({format_rp(AL_ilp_x_now)})."

            # Interpretasi Iuran Normal Saat Ini
            if NC_ilp_now < NC_aan_x_now:
                interpretation_nc = f"Pada usia {x_now_state} saat ini, iuran tahunan **EAN** ({format_rp(NC_ilp_now)}) **lebih rendah** daripada iuran AAN ({format_rp(NC_aan_x_now)})."
            else:
                interpretation_nc = f"Pada usia {x_now_state} saat ini, iuran tahunan **AAN** ({format_rp(NC_aan_x_now)}) **lebih rendah** daripada iuran EAN ({format_rp(NC_ilp_now)})."

            st.markdown("Berikut adalah kesimpulan utama dari perbandingan kedua metode:")
            st.markdown(f"* **Pola Iuran:** {interpretation_graph}")
            st.markdown(f"* **Total Biaya (Nilai Akhir):** {interpretation_na}")
            st.markdown(f"* **Kewajiban Saat Ini (Usia {x_now_state}):** {interpretation_al}")
            st.markdown(f"* **Iuran Saat Ini (Usia {x_now_state}):** {interpretation_nc}")
            
            st.divider() # Pemisah sebelum tabel rinci

            st.markdown("##### Tabel Rinci Perhitungan per Usia")
            cols_to_show = ['PVFB', 'Iuran Normal (EAN)', 'Kewajiban Aktuaria (EAN)', 'Iuran Normal (AAN)', 'Kewajiban Aktuaria (AAN)']
            df_display = df_actuarial_full.set_index('Usia')[cols_to_show]
            
            def highlight_row(row):
                if row.name == x_now_state:
                    return ['background-color: #2b6aca; color: white;'] * len(row) 
                return [''] * len(row) 

            st.dataframe(df_display.style.apply(highlight_row, axis=1).format("Rp {:,.2f}"), use_container_width=True, height=600)
            st.caption(f"Tabel ini menunjukkan nilai aktuaria per tahun dari usia masuk ({x_entry_state}) hingga pensiun ({r_state-1}). Baris usia valuasi ({x_now_state}) ditandai.")

    # --- ISI TAB FORMULA ---
    with tab_formula:
        st.header("🔬 Detail Formula Perhitungan")
        st.info(f"Asumsi: Suku Bunga (i) = **{i_percent_state:.1f}%**, Kenaikan Gaji (s) = **{s_percent_state:.1f}%**, TMI 2023 **{jenis_kelamin_state}**.")
        
        # --- 1. Manfaat Pensiun ---
        st.subheader("1. Manfaat Pensiun Tahunan ($B_r$)")
        st.metric("Hasil Perhitungan", format_rp(B_r), help="Manfaat tahunan yang akan diterima saat pensiun.")
        with st.expander("Lihat Detail Formula"):
            
            st.markdown(f"**Perhitungan $S_{{{r_state-1}}}$ (Gaji Proyeksi):**")
            st.latex(r"S_{r-1} = (1+s)^{r-e-1} \times s_e")
            latex_s_e = rf"S_{{{r_state-1}}} = (1 + {format_latex_num(s_state)})^{{{r_state}-{x_entry_state}-1}} \times {gaji_masuk_state:,.0f}"
            st.latex(latex_s_e)
            st.latex(rf"S_{{{r_state-1}}} = {format_calc(Sr_minus_1)}")

            st.markdown(f"**Perhitungan $B_{{{r_state}}}$ (Manfaat Pensiun):**")
            st.latex(r"B_r = k \times (r - e) \times S_{r-1}")
            latex_b_r_vars = rf"B_{{{r_state}}} = {format_latex_num(k_state)} \times ({r_state} - {x_entry_state}) \times S_{{{r_state-1}}}"
            st.latex(latex_b_r_vars)
            latex_b_r_nums = rf"B_{{{r_state}}} = {format_latex_num(k_state)} \times ({r_state-x_entry_state}) \times {format_calc(Sr_minus_1)}"
            st.latex(latex_b_r_nums)
            st.latex(rf"B_{{{r_state}}} = {format_calc(B_r)}")

        st.divider()

        # --- 2. PVFB ---
        st.subheader("2. Nilai Sekarang Manfaat Pensiun (${}^{r}(PVFB)_{x}$)")
        st.metric(f"Hasil di Usia {x_now_state}", format_rp(PVFB_x_now), help="Nilai kini dari seluruh manfaat pensiun yang diharapkan.")
        with st.expander("Lihat Detail Formula"):
            st.latex(r"^{r}(PVFB)_{x} = B_r \times \frac{D_r}{D_x}")
            st.markdown(f"**Perhitungan di Usia {x_now_state}:**")
            latex_pvfb_vars = rf"^{{{r_state}}}(PVFB)_{{{x_now_state}}} = B_{{{r_state}}} \times \frac{{D_{{{r_state}}}}}{{D_{{{x_now_state}}}}}"
            st.latex(latex_pvfb_vars)
            latex_pvfb_nums = rf"^{{{r_state}}}(PVFB)_{{{x_now_state}}} = {format_calc(B_r)} \times \frac{{{format_calc(Dx_r)}}}{{{format_calc(Dx_now)}}}"
            st.latex(latex_pvfb_nums)
            st.latex(rf"^{{{r_state}}}(PVFB)_{{{x_now_state}}} = {format_calc(PVFB_x_now)}")

        st.divider()

        # --- 3. IURAN NORMAL ---
        st.subheader(f"3. Iuran Normal (NC) di Usia {x_now_state}")
        col1_f, col2_f = st.columns(2)
        with col1_f:
            st.markdown("**Metode EAN**")
            st.metric(f"Iuran Normal (NC)", format_rp(NC_ilp_now), help="Iuran tahunan EAN.")
            with st.expander("Lihat Detail Formula NC EAN"):
                 st.latex(r"^{EAN~r}(NC)_{x} = \frac{D_x}{N_x - N_r} \times {}^{r}(PVFB)_{x}")
                 st.markdown(f"**Perhitungan di Usia {x_now_state}:**")
                 latex_nc_ean_vars = rf"^{{EAN~{r_state}}}(NC)_{{{x_now_state}}} = \frac{{D_{{{x_now_state}}}}}{{N_{{{x_now_state}}} - N_{{{r_state}}}}} \times {{}}^{{{r_state}}}(PVFB)_{{{x_now_state}}}"
                 st.latex(latex_nc_ean_vars)
                 latex_nc_ean_nums = rf"^{{EAN~{r_state}}}(NC)_{{{x_now_state}}} = \frac{{{format_calc(Dx_now)}}}{{{format_calc(Nx_now)} - {format_calc(Nx_r)}}} \times {format_calc(PVFB_x_now)}"
                 st.latex(latex_nc_ean_nums)
                 latex_nc_ean_mid = rf"^{{EAN~{r_state}}}(NC)_{{{x_now_state}}} = \frac{{{format_calc(Dx_now)}}}{{{format_calc(Nx_now - Nx_r)}}} \times {format_calc(PVFB_x_now)}"
                 st.latex(latex_nc_ean_mid)
                 st.latex(rf"^{{EAN~{r_state}}}(NC)_{{{x_now_state}}} = {format_calc(NC_ilp_now)}")
                 
        with col2_f:
            st.markdown("**Metode AAN**")
            st.metric(f"Iuran Normal (NC)", format_rp(NC_aan_x_now), help="Iuran tahunan AAN.")
            with st.expander("Lihat Detail Formula NC AAN"):
                 st.latex(r"^{AAN~r}(NC)_{x} = \frac{{}^{r}(PVFB)_{e}}{\frac{N_x - N_r}{D_x}}")
                 st.markdown(f"**Perhitungan di Usia {x_now_state}:**")
                 latex_nc_aan_vars = rf"^{{AAN~{r_state}}}(NC)_{{{x_now_state}}} = \frac{{{{}}^{{{r_state}}}(PVFB)_{{{x_entry_state}}}}}{{ \frac{{N_{{{x_now_state}}} - N_{{{r_state}}}}}{{D_{{{x_now_state}}}}} }}"
                 st.latex(latex_nc_aan_vars)
                 st.latex(rf"\text{{Nilai pembilang: }} ^{{{r_state}}}(PVFB)_{{{x_entry_state}}} = {format_calc(PVFB_entry_AAN)}")
                 st.latex(rf"\text{{Nilai penyebut: }} \frac{{{format_calc(Nx_now)} - {format_calc(Nx_r)}}}{{{format_calc(Dx_now)}}} = {format_calc(anuitas_now_formula)}")
                 latex_nc_aan_mid = rf"^{{AAN~{r_state}}}(NC)_{{{x_now_state}}} = \frac{{{format_calc(PVFB_entry_AAN)}}}{{{format_calc(anuitas_now_formula)}}}"
                 st.latex(latex_nc_aan_mid)
                 st.latex(rf"^{{AAN~{r_state}}}(NC)_{{{x_now_state}}} = {format_calc(NC_aan_x_now)}")

        st.divider()

        # --- 4. KEWAJIBAN AKTUARIA ---
        st.subheader(f"4. Kewajiban Aktuaria (AL) di Usia {x_now_state}")
        col3_f, col4_f = st.columns(2)
        with col3_f:
            st.markdown("**Metode EAN**")
            st.metric(f"Kewajiban Aktuaria (AL)", format_rp(AL_ilp_x_now), help="Target dana EAN.")
            with st.expander("Lihat Detail Formula AL EAN"):
                 st.latex(r"^{EAN~r}(AL)_{x} = \frac{\frac{N_e - N_x}{D_e}}{\frac{N_e - N_r}{D_e}} \times {}^{r}(PVFB)_{x}") 
                 st.markdown(f"**Perhitungan di Usia {x_now_state}:**")
                 latex_al_ean_vars = rf"^{{EAN~{r_state}}}(AL)_{{{x_now_state}}} = \frac{{\frac{{N_{{{x_entry_state}}} - N_{{{x_now_state}}}}}{{D_{{{x_entry_state}}}}}}}{{\frac{{N_{{{x_entry_state}}} - N_{{{r_state}}}}}{{D_{{{x_entry_state}}}}}}} \times {{}}^{{{r_state}}}(PVFB)_{{{x_now_state}}}"
                 st.latex(latex_al_ean_vars)
                 st.latex(rf"\text{{Nilai pembilang: }} \frac{{{format_calc(Nx_entry)} - {format_calc(Nx_now)}}}{{{format_calc(Dx_entry)}}} = {format_calc(anuitas_entry_to_now_formula)}")
                 st.latex(rf"\text{{Nilai penyebut: }} \frac{{{format_calc(Nx_entry)} - {format_calc(Nx_r)}}}{{{format_calc(Dx_entry)}}} = {format_calc(anuitas_entry_formula)}")
                 latex_al_ean_mid = rf"^{{EAN~{r_state}}}(AL)_{{{x_now_state}}} = \frac{{{format_calc(anuitas_entry_to_now_formula)}}}{{{format_calc(anuitas_entry_formula)}}} \times {format_calc(PVFB_x_now)}"
                 st.latex(latex_al_ean_mid)
                 st.latex(rf"^{{EAN~{r_state}}}(AL)_{{{x_now_state}}} = {format_calc(AL_ilp_x_now)}")

        with col4_f:
            st.markdown("**Metode AAN**")
            st.metric(f"Kewajiban Aktuaria (AL)", format_rp(AL_aan_x_now), help="Target dana AAN.")
            with st.expander("Lihat Detail Formula AL AAN"):
                 st.latex(r"^{AAN~r}(AL)_{x} = {}^{r}(PVFB)_{x} - {}^{AAN~r}(NC)_{x} \times \frac{N_x - N_r}{D_x}")
                 st.markdown(f"**Perhitungan di Usia {x_now_state}:**")
                 latex_al_aan_vars = rf"^{{AAN~{r_state}}}(AL)_{{{x_now_state}}} = {{}}^{{{r_state}}}(PVFB)_{{{x_now_state}}} - ({{}}^{{AAN~{r_state}}}(NC)_{{{x_now_state}}} \times \frac{{N_{{{x_now_state}}} - N_{{{r_state}}}}}{{D_{{{x_now_state}}}}})"
                 st.latex(latex_al_aan_vars)
                 latex_al_aan_mid = rf"^{{AAN~{r_state}}}(AL)_{{{x_now_state}}} = {format_calc(PVFB_x_now)} - ({format_calc(NC_aan_x_now)} \times {format_calc(anuitas_now_formula)})"
                 st.latex(latex_al_aan_mid)
                 st.latex(rf"^{{AAN~{r_state}}}(AL)_{{{x_now_state}}} = {format_calc(AL_aan_x_now)}")

        st.divider()
        
# --- 5. NILAI AKHIR ---
        st.subheader("5. Nilai Akhir Total Iuran (NA) di Usia Pensiun")
        col1_na, col2_na = st.columns(2)
        with col1_na:
            st.metric("Hasil NA EAN", format_rp(NA_ean_total), help="Akumulasi iuran EAN.")
            with st.expander("Lihat Detail Formula NA EAN"):
                st.markdown("**Metode Entry Age Normal**")
                st.latex(r"{}^{EAN}NA = \sum_{x=e}^{r-1} \, {}^{EAN}(NC)_x (1+i)^{r-x}")
                st.latex(rf"{{}}^{{EAN}}NA = \sum_{{x={x_entry_state}}}^{{{r_state-1}}} \, {{}}^{{EAN}}(NC)_x (1 + {format_latex_num(i_state)})^{{{r_state}-x}}")
                term1_power = r_state - x_entry_state
                term2_power = r_state - (x_entry_state + 1)
                x_last = r_state - 1 # Usia terakhir sebelum pensiun
                st.latex(rf"{{}}^{{EAN}}NA = {{}}^{{EAN}}(NC)_{{{x_entry_state}}} (1+{format_latex_num(i_state)})^{{{term1_power}}} + {{}}^{{EAN}}(NC)_{{{x_entry_state+1}}} (1+{format_latex_num(i_state)})^{{{term2_power}}} + \dots + {{}}^{{EAN}}(NC)_{{{x_last}}} (1+{format_latex_num(i_state)})^{{1}}")
                st.latex(rf"{{}}^{{EAN}}NA = {format_calc(NA_ean_term_first)} + {format_calc(NA_ean_term_second)} + \dots + {format_calc(NA_ean_term_last)}")
                st.latex(rf"{{}}^{{EAN}}NA = {format_calc(NA_ean_total)}")
        
        with col2_na:
            st.metric("Hasil NA AAN", format_rp(NA_aan_total), help="Akumulasi iuran AAN.")
            with st.expander("Lihat Detail Formula NA AAN"):
                st.markdown("**Metode Attained Age Normal**")
                st.latex(r"{}^{AAN}NA = \sum_{x=e}^{r-1} \, {}^{AAN}(NC)_x (1+i)^{r-x}")
                st.latex(rf"{{}}^{{AAN}}NA = \sum_{{x={x_entry_state}}}^{{{r_state-1}}} \, {{}}^{{AAN}}(NC)_x (1 + {format_latex_num(i_state)})^{{{r_state}-x}}")
                term1_power = r_state - x_entry_state
                term2_power = r_state - (x_entry_state + 1)
                x_last = r_state - 1
                st.latex(rf"{{}}^{{AAN}}NA = {{}}^{{AAN}}(NC)_{{{x_entry_state}}} (1+{format_latex_num(i_state)})^{{{term1_power}}} + {{}}^{{AAN}}(NC)_{{{x_entry_state+1}}} (1+{format_latex_num(i_state)})^{{{term2_power}}} + \dots + {{}}^{{AAN}}(NC)_{{{x_last}}} (1+{format_latex_num(i_state)})^{{1}}")
                st.latex(rf"{{}}^{{AAN}}NA = {format_calc(NA_aan_term_first)} + {format_calc(NA_aan_term_second)} + \dots + {format_calc(NA_aan_term_last)}")
                st.latex(rf"{{}}^{{AAN}}NA = {format_calc(NA_aan_total)}")

    # --- ISI TAB TABEL KOMUTASI ---
    with tab_commutation:
        st.header("🧮 Tabel Komutasi Lengkap")
        st.caption(f"Tabel ini menunjukkan fungsi komutasi dasar (lx, Dx, Nx) yang dihitung berdasarkan TMI 2023 untuk **{jenis_kelamin_state}** dan suku bunga **{i_percent_state:.1f}%**.")
        if comm_table is not None and not comm_table.empty:
            cols_commutation = ['x', 'qx', 'px', 'lx', 'Dx', 'Nx']
            df_comm_display = comm_table[cols_commutation].set_index('x')
            
            st.dataframe(df_comm_display.style.format({
                'qx': '{:,.6f}',
                'px': '{:,.6f}',
                'lx': '{:,.2f}',
                'Dx': '{:,.2f}',
                'Nx': '{:,.2f}'
            }), use_container_width=True, height=600)
        else:
            st.warning("Tabel komutasi belum tersedia.")

else:
    st.error("❌ Gagal memuat data mortalitas internal. Perhitungan tidak dapat dilanjutkan.")

    st.warning("Pastikan data TMI sudah dimuat dengan benar di dalam skrip Python.")
