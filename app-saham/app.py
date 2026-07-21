import streamlit as st
import yfinance as yf
from google import genai
import time

st.set_page_config(page_title="Analisis Saham AI", layout="wide")
st.title("📈 Web Analisa Saham AI")

# Inisialisasi session state untuk cache
if 'cache' not in st.session_state:
    st.session_state.cache = {}

api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("⚠️ API Key Gemini belum dikonfigurasi.")
    st.stop()

try:
    client = genai.Client(api_key=api_key)
except Exception as e:
    st.error(f"Gagal inisialisasi Gemini: {e}")
    st.stop()

ticker_input = st.text_input("Masukkan Kode Saham (contoh: BBCA.JK):", "BBCA.JK")

if st.button("Analisa Saham"):
    # Cek cache dulu
    if ticker_input in st.session_state.cache:
        cached_data = st.session_state.cache[ticker_input]
        # Jika cache kurang dari 1 jam, gunakan cache
        if time.time() - cached_data['timestamp'] < 3600:
            st.info("️ Menggunakan data cache (hemat kuota!)")
            st.write(cached_data['analysis'])
            st.stop()
    
    with st.spinner("Mengambil data dan menganalisis..."):
        try:
            stock = yf.Ticker(ticker_input)
            hist = stock.history(period="1mo")
            info = stock.info

            if hist.empty:
                st.error("❌ Data tidak ditemukan.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Ringkasan Data")
                    st.write(f"**Nama:** {info.get('longName', ticker_input)}")
                    st.write(f"**Harga:** Rp {hist['Close'].iloc[-1]:,.2f}")
                    st.write(f"**Sektor:** {info.get('sector', 'N/A')}")
                
                with col2:
                    st.subheader("Grafik 1 Bulan")
                    st.line_chart(hist['Close'])

                prompt = f"Analisis saham {ticker_input} harga {hist['Close'].iloc[-1]} sektor {info.get('sector', 'N/A')}"

                # Panggil API dengan error handling untuk quota
                try:
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt
                    )
                    analysis = response.text
                    
                    # Simpan ke cache
                    st.session_state.cache[ticker_input] = {
                        'analysis': analysis,
                        'timestamp': time.time()
                    }
                    
                    st.markdown("---")
                    st.subheader("💡 Analisis AI")
                    st.write(analysis)
                    
                except Exception as api_error:
                    if "429" in str(api_error) or "RESOURCE_EXHAUSTED" in str(api_error):
                        st.error("️ Kuota API habis! Tunggu 1-2 menit atau gunakan API key baru.")
                        st.info("💡 Tips: Hasil analisis akan di-cache selama 1 jam untuk hemat kuota.")
                    else:
                        st.error(f"Error: {api_error}")

        except Exception as e:
            st.error(f"⚠️ Error: {e}")
