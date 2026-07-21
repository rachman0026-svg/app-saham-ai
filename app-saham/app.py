import streamlit as st
import yfinance as yf
from google import genai

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Analisis Saham AI", layout="wide")
st.title("📈 Web Analisa Saham AI")

# 2. Ambil API Key dari Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key Gemini belum dikonfigurasi di Streamlit Secrets.")
    st.stop()

# 3. Inisialisasi Gemini Client
try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gagal menginisialisasi Gemini Client: {e}")
    st.stop()

# 4. Input Ticker Saham dari User
ticker_input = st.text_input("Masukkan Kode Saham (contoh: BBCA.JK, TLKM.JK, AAPL):", "BBCA.JK")

if st.button("Analisa Saham"):
    with st.spinner("Mengambil data saham dan menganalisis..."):
        try:
            # Ambil Data Saham dari Yahoo Finance
            stock = yf.Ticker(ticker_input)
            hist = stock.history(period="1mo")
            info = stock.info

            if hist.empty:
                st.error("❌ Data saham tidak ditemukan. Pastikan kodenya benar (misal pakai '.JK' untuk saham Indonesia).")
            else:
                # Tampilkan Ringkasan & Grafik
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Ringkasan Data")
                    st.write(f"**Nama Perusahaan:** {info.get('longName', ticker_input)}")
                    st.write(f"**Harga Terakhir:** Rp {hist['Close'].iloc[-1]:,.2f}")
                    st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
                
                with col2:
                    st.subheader("Grafik Penutupan 1 Bulan")
                    st.line_chart(hist['Close'])

                # Susun Prompt untuk Gemini AI
                prompt = f"""
                Bertindaklah sebagai analis keuangan profesional. Berikut adalah data saham {ticker_input}:
                - Nama Perusahaan: {info.get('longName', ticker_input)}
                - Harga Penutupan Terakhir: {hist['Close'].iloc[-1]}
                - Ringkasan Bisnis: {info.get('longBusinessSummary', 'Tidak ada deskripsi')}
                
                Berikan analisis singkat mengenai posisi perusahaan ini dan sentimen investasi secara objektif dan mudah dipahami.
                """

                # Panggil API Gemini tanpa config tambahan yang bikin error
                response = client.models.generate_content(
                  # GANTI BARIS 60 MENJADI INI:
                  model='gemini-2.0-flash',
                    contents=prompt
                )
                
                st.markdown("---")
                st.subheader("💡 Analisis AI (Gemini)")
                st.write(response.text)

        except Exception as e:
            st.error(f"⚠️ Terjadi kesalahan saat memproses analisis: {e}")
