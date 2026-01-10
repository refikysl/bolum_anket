import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="SBKY Akreditasyon Anketi", layout="wide", initial_sidebar_state="collapsed")

# --- ARTİSTLİK VE FONKSİYONEL DOKUNUŞ: STICKY QUESTION CSS ---
st.markdown("""
    <style>
    /* Sorunun ekrana yapışmasını sağlayan sihirli kod */
    .sticky-question {
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: #1f77b4;
        color: white;
        padding: 15px;
        border-radius: 10px;
        z-index: 999;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        font-weight: bold;
    }
    /* Mobil cihazlar için radyo buton aralıklarını optimize etme */
    div.row-widget.stRadio > div {
        flex-direction: column;
    }
    /* Kart yapısı */
    .question-card {
        background-color: #ffffff;
        border: 1px solid #e6e9ef;
        padding: 20px;
        border-radius: 15px;
        margin-bottom: 40px;
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

st.title("🏛️ SBKY Ders Değerlendirme Anketi")
sinif = st.selectbox("Lütfen Sınıfınızı Seçiniz:", list(ders_programi.keys()))

aktif_dersler = ders_programi[sinif]
form_cevaplari = []

# --- ANKET OLUŞTURMA (Yapışkan Başlıklı Model) ---
for s_no, soru_metni in enumerate(sorular, 1):
    # HTML kullanarak yapışkan başlık oluşturma
    st.markdown(f'<div class="sticky-question">SORU {s_no}: {soru_metni}</div>', unsafe_allow_html=True)
    
    # Dersleri ve seçenekleri bir kapsayıcı içinde göster
    with st.container():
        cols = st.columns(len(aktif_dersler))
        for idx, ders in enumerate(aktif_dersler):
            with cols[idx]:
                cevap = st.radio(f"**{ders}**", options, index=2, key=f"q{s_no}_{ders}")
                form_cevaplari.append({"Sinif": sinif, "Ders": ders, "Soru_No": s_no, "Puan": cevap})
    
    st.markdown('<hr style="border: 2px solid #f0f2f6;">', unsafe_allow_html=True)

# --- GÖNDERME BUTONU ---
if st.button("🚀 ANKETİ TAMAMLA VE GÖNDER", use_container_width=True):
    # KENDİ GOOGLE SCRIPT URL'NİZİ BURAYA YAPIŞTIRIN
    script_url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec"
    
    with st.spinner('Veriler kaydediliyor...'):
        try:
            response = requests.post(script_url, json=form_cevaplari)
            if response.text == "Başarılı":
                st.balloons()
                st.success("Cevaplarınız başarıyla iletildi!")
            else:
                st.error(f"Hata: {response.text}")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")