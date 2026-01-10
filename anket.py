import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="SBKY Anketi", layout="wide")

# 1. Ders Listesi
ders_programi = {
    "Sınıf 1": ["Medeniyet Tarihi 1", "Siyaset Bilimi 1", "Hukukun Temel Kavramları", "Sosyoloji", "Sosyal Bilimlerde İstatistik", "Türk İdare Tarihi", "Araştırma Yöntem ve Teknikleri"],
    "Sınıf 2": ["Anayasa Hukuku", "Kamu Yönetimi", "Yönetim Bilimi", "Siyasal Tarih", "İktisada Giriş"],
    "Sınıf 3": ["Yerel Yönetimler 1", "İdare Hukuku", "Karşılaştırmalı Kamu Yönetimi", "Temel Hak ve Hürriyetler", "AB Kurumları ve Politikaları", "Doğu Siyasal Düşünceler Tarihi", "Kültürel Haklar ve Siyaset", "Siyaset Sosyolojisi"],
    "Sınıf 4": ["Kamu Maliyesi", "Karş. Siyasal Sistemler", "Kentsel Politikalar", "Siyasal Antropoloji", "Ticaret Hukuku", "Uluslararası İktisat", "İnsan Kaynakları Yönetimi"]
}

# 2. 20 Akreditasyon Sorusu
sorular = [
    "Öğretim elemanı, konulara ilişkin ileri düzey ve güncel akademik bilgiye sahiptir.",
    "Öğretim elemanı, dersi açık ve anlaşılır biçimde sunmaktadır.",
    "Öğretim elemanı, içerikleri güncel gelişmeler doğrultusunda yenilemektedir.",
    "Öğretim elemanı, uygun öğretim teknolojilerini etkili kullanmaktadır.",
    "Öğretim elemanı, adil bir tutum sergilemektedir.",
    "Öğretim elemanı, öğrencileri derse katılım konusunda teşvik etmektedir.",
    "Öğretim elemanı, sorulara ve eleştirilere açıktır.",
    "Öğretim elemanı, etkili geri bildirim süreçleri yürütmektedir.",
    "Öğretim elemanına ders dışı zamanlarda ulaşılabilmektedir.",
    "Öğretim elemanı, ders saatlerine özen göstermektedir.",
    "Kaynaklar, dönemin başında açık biçimde sunulmuştur.",
    "Kullanılan materyaller içeriklerin anlaşılmasına katkı sağlamıştır.",
    "Anlatılan konular ile sınavlar örtüşmektedir.",
    "Sınavların zorluk düzeyi içerikle uyumludur.",
    "Sınav soruları öğrenme süreçlerini tamamlar niteliktedir.",
    "Bu öğretim elemanından başka dersler de almak isterim.",
    "Edindiğim bilgiler mesleki yaşamda hazırlıklı olmamı sağlayacaktır.",
    "Bilgilerin kariyer sınavlarında katkısı olacağını düşünüyorum.",
    "Ders, eleştirel düşünme becerilerimi geliştirdi.",
    "Ders, kuramsal bilgiler ile uygulama arasındaki ilişkiyi anlamama yardımcı oldu."
]

options = ["K. Katılmıyorum", "Katılmıyorum", "Fikrim Yok", "Katılıyorum", "K. Katılıyorum"]

# --- DURUM YÖNETİMİ (Session State) ---
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'all_data' not in st.session_state:
    st.session_state.all_data = []

# Başlık
st.title("🏛️ SBKY Bölüm Anketi")

# Sınıf Seçimi (Sadece ilk adımda gösterilir veya yan menüye alınır)
with st.sidebar:
    sinif = st.selectbox("Sınıfınızı Seçiniz:", list(ders_programi.keys()))
    st.write(f"İlerleme: {st.session_state.current_step + 1} / 20")
    st.progress((st.session_state.current_step + 1) / 20)

aktif_dersler = ders_programi[sinif]

# --- ANKET EKRANI ---
if st.session_state.current_step < 20:
    s_no = st.session_state.current_step
    soru_metni = sorular[s_no]
    
    # SORU METNİ - HER ZAMAN TEPEDE DURUR
    st.info(f"**SORU {s_no + 1}:** {soru_metni}")
    
    # CEVAP ALANI
    current_responses = []
    for ders in aktif_dersler:
        cevap = st.select_slider(
            f"**{ders}**",
            options=options,
            value="Fikrim Yok",
            key=f"step_{s_no}_{ders}"
        )
        current_responses.append({"Sinif": sinif, "Ders": ders, "Soru_No": s_no + 1, "Puan": cevap})
    
    # BUTONLAR
    if st.button("Sonraki Soruya Geç ➡️"):
        st.session_state.all_data.extend(current_responses)
        st.session_state.current_step += 1
        st.rerun()

else:
    # --- GÖNDERME EKRANI ---
    st.success("Tüm soruları yanıtladınız! Şimdi sisteme gönderebilirsiniz.")
    if st.button("🚀 ANKETİ TAMAMLA VE GÖNDER"):
        script_url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec" 
        with st.spinner('Kaydediliyor...'):
            try:
                response = requests.post(script_url, json=st.session_state.all_data)
                if response.text == "Başarılı":
                    st.balloons()
                    st.success("Cevaplarınız başarıyla iletildi!")
                    st.session_state.current_step = 0 # Sıfırla
                    st.session_state.all_data = []
                else:
                    st.error(f"Hata: {response.text}")
            except Exception as e:
                st.error(f"Bağlantı hatası: {e}")