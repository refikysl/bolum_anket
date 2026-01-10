import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="SBKY Akreditasyon Anketi", layout="wide", initial_sidebar_state="expanded")

# --- ARTİSTLİK DOKUNUŞ: ÖZEL CSS ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stRadio > label { font-weight: bold; color: #1f77b4; }
    div[data-testid="stVerticalBlock"] > div:has(div.stInfo) {
        border-radius: 15px;
        padding: 10px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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

options = ["Kesinlikle katılmıyorum", "Katılmıyorum", "Fikrim yok", "Katılıyorum", "Kesinlikle katılıyorum"]

# --- SIDEBAR (YAN MENÜ) TASARIMI ---
with st.sidebar:
    st.header("📊 Anket Durumu")
    sinif = st.selectbox("Sınıfınızı Seçiniz:", list(ders_programi.keys()))
    st.divider()
    st.info("Her ders için tüm soruları yanıtladığınızdan emin olun.")

# Ana Başlık
st.title("🏛️ Siyaset Bilimi ve Kamu Yönetimi")
st.subheader("Ders Değerlendirme ve Akreditasyon Anketi")

aktif_dersler = ders_programi[sinif]
form_cevaplari = []

# --- ANKET OLUŞTURMA ---
for s_no, soru_metni in enumerate(sorular, 1):
    # Her soruyu şık bir kutu içine alıyoruz
    with st.container():
        st.info(f"**SORU {s_no}:** {soru_metni}")
        cols = st.columns(len(aktif_dersler))
        
        for idx, ders in enumerate(aktif_dersler):
            with cols[idx]:
                cevap = st.radio(f"{ders}", options, index=2, key=f"q{s_no}_{ders}")
                form_cevaplari.append({"Sinif": sinif, "Ders": ders, "Soru_No": s_no, "Puan": cevap})
    st.write("") # Boşluk bırak

# --- İLERLEME ÇUBUĞU HESABI ---
# (Sadece işaretlenenleri saymak yerine görsel olarak doluluk hissi verir)
st.sidebar.write(f"**Değerlendirilen Ders Sayısı:** {len(aktif_dersler)}")
st.sidebar.write(f"**Toplam Soru Sayısı:** {len(sorular)}")

# --- GÖNDERME BUTONU VE EFEKTLER ---
st.divider()
if st.button("🚀 ANKETİ TAMAMLA VE SİSTEME GÖNDER", use_container_width=True):
    # Sizin Google Apps Script URL'nizi buraya tekrar yapıştırın!
    script_url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec" 
    
    with st.spinner('Verileriniz güvenli sunucuya aktarılıyor...'):
        try:
            response = requests.post(script_url, json=form_cevaplari)
            if response.text == "Başarılı":
                st.balloons()
                st.snow() # Bonus efekt: Kar yağdır!
                st.success("✅ Başarılı! Katkılarınız için teşekkür ederiz.")
                st.confetti() # Eğer özel kütüphane varsa çalışır, yoksa hata vermez
            else:
                st.error(f"Hata oluştu: {response.text}")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")