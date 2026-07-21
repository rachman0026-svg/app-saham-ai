import streamlit as st
import yfinance as yf
from google import genai
from google.genai import types

# 1. Konfigurasi Halaman Streamlit
st.set_page_config(page_title="Analisis Saham AI", layout="wide")
st.title("📈 Web Analisa Saham AI")

# 2. Ambil API Key dari Streamlit Secrets
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("API Key Gemini belum diisi di Secrets Streamlit.")
    st.stop()

# 3. Inisialisasi Gemini Client
client = genai.Client(api_key=api_key)

# 4. Input Ticker Saham dari User
ticker_input = st.text_input("Masukkan Kode Saham (Contoh: BBCA.JK, TLKM.JK, AAPL):", "BBCA.JK")

if st.button("Analisa Saham"):
    with st.spinner("Mengambil data saham dan menganalisis..."):
        # Ambil data dari yfinance
        stock = yf.Ticker(ticker_input)
        hist = stock.history(period="1mo")
        info = stock.info

        if hist.empty:
            st.error("Data saham tidak ditemukan. Pastikan kodenya benar.")
        else:
            # Tampilkan Informasi & Grafik
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("Ringkasan Data")
                st.write(f"**Nama Perusahaan:** {info.get('longName', ticker_input)}")
                st.write(f"**Harga Terakhir:** {hist['Close'].iloc[-1]:,.2f}")
                st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
            
            with col2:
                st.subheader("Grafik Penutupan 1 Bulan")
                st.line_chart(hist['Close'])

            # Prompt dan Konfigurasi untuk Gemini AI
            prompt = f"""
            Bertindaklah sebagai analis keuangan profesional. Berikut adalah data saham {ticker_input}:
            - Nama Perusahaan: {info.get('longName', ticker_input)}
            - Harga Penutupan Terakhir: {hist['Close'].iloc[-1]}
            - Ringkasan Perusahaan: {info.get('longBusinessSummary', 'Tidak ada deskripsi')}
            
            Berikan analisis singkat mengenai posisi perusahaan ini, serta sentimen investasi secara objektif.
            """

            # Panggil Gemini API dengan fitur Search Grounding jika diperlukan
            config = types.GenerateContentConfig(
                temperature=0.7,
                tools=[{"google_search": {}}]
            )
            
            response = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=config
            )
            
            st.markdown("---")
            st.subheader("💡 Analisis AI (Gemini)")
            st.write(response.text)