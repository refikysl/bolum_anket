import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="SBKY Anketi", layout="wide")

# --- GÜVENLİ STICKY CSS (Sadece Soruya Odaklı) ---
st.markdown("""
    <style>
    .stHeader {
        z-index: 100;
    }
    .sticky-box {
        position: -webkit-sticky;
        position: sticky;
        top: 0px;
        background-color: #1f77b4;
        color: white;
        padding: 15px;
        border-radius: 8px;
        z-index: 99;
        margin-top: 10px;
        margin-bottom: 10px;
        font-weight: bold;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .answer-card {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

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

st.title("🏛️ SBKY Bölüm Anketi")
sinif = st.selectbox("Sınıfınızı Seçiniz:", list(ders_programi.keys()))

aktif_dersler = ders_programi[sinif]
form_cevaplari = []

# --- ANKET DÖNGÜSÜ ---
for s_no, soru_metni in enumerate(sorular, 1):
    # Yapışkan Soru Başlığı
    st.markdown(f'<div class="sticky-box">SORU {s_no}: {soru_metni}</div>', unsafe_allow_html=True)
    
    # Cevap Alanı
    with st.container():
        cols = st.columns(len(aktif_dersler))
        for idx, ders in enumerate(aktif_dersler):
            with cols[idx]:
                cevap = st.radio(f"**{ders}**", options, index=2, key=f"q{s_no}_{ders}")
                form_cevaplari.append({"Sinif": sinif, "Ders": ders, "Soru_No": s_no, "Puan": cevap})
    
    st.divider()

# --- GÖNDERME BUTONU ---
if st.button("🚀 ANKETİ TAMAMLA VE GÖNDER", use_container_width=True):
    # BURAYA KENDİ SCRIPT URL'NİZİ YAPIŞTIRIN
    script_url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec" 
    
    with st.spinner('Kaydediliyor...'):
        try:
            response = requests.post(script_url, json=form_cevaplari)
            if response.text == "Başarılı":
                st.balloons()
                st.success("Cevaplarınız başarıyla iletildi!")
            else:
                st.error(f"Hata: {response.text}")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")