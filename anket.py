import streamlit as st
import pandas as pd
import requests

# 1. Ders Listesi - SADECE SAF PYTHON KODU
ders_programi = {
    "Sınıf 1": ["Medeniyet Tarihi 1", "Siyaset Bilimi 1", "Hukukun Temel Kavramları", "Sosyoloji", "Sosyal Bilimlerde İstatistik", "Türk İdare Tarihi", "Araştırma Yöntem ve Teknikleri"],
    "Sınıf 2": ["Anayasa Hukuku", "Kamu Yönetimi", "Yönetim Bilimi", "Siyasal Tarih", "İktisada Giriş"],
    "Sınıf 3": ["Yerel Yönetimler 1", "İdare Hukuku", "Karşılaştırmalı Kamu Yönetimi", "Temel Hak ve Hürriyetler", "AB Kurumları ve Politikaları", "Doğu Siyasal Düşünceler Tarihi", "Kültürel Haklar ve Siyaset", "Siyaset Sosyolojisi"],
    "Sınıf 4": ["Kamu Maliyesi", "Karş. Siyasal Sistemler", "Kentsel Politikalar", "Siyasal Antropoloji", "Ticaret Hukuku", "Uluslararası İktisat", "İnsan Kaynakları Yönetimi"]
}

# 2. 20 Akreditasyon Sorusu
sorular = [
    "Öğretim elemanı, ders kapsamında ele alınan konulara ilişkin ileri düzey ve güncel akademik bilgiye sahiptir.",
    "Öğretim elemanı, dersi açık ve anlaşılır biçimde sunarak öğretim sürecini etkili şekilde yürütmektedir.",
    "Öğretim elemanı, dersin içeriklerini alanındaki güncel gelişmeler doğrultusunda yenilemektedir.",
    "Öğretim elemanı, ders kapsamında uygun öğretim teknolojilerini etkili bir şekilde kullanmaktadır.",
    "Öğretim elemanı, öğrenciler arasında ayrım gözetmeden adil bir tutum sergilemektedir.",
    "Öğretim elemanı, öğrencileri derse aktif katılım ve tartışmalara katılma konusunda teşvik etmektedir.",
    "Öğretim elemanı, öğrencilerden gelen sorulara ve eleştirilere açık bir tutum sergilemektedir.",
    "Öğretim elemanı, öğrencilerle etkili geri bildirim süreçleri yürütmektedir.",
    "Öğretim elemanına, ders dışı zamanlarda ulaşılabilmektedir.",
    "Öğretim elemanı, dersin başlangıç ve bitiş saatlerine özen göstermektedir.",
    "Ders kapsamında kullanılacak kaynaklar dönemin başında öğrencilere sunulmuştur.",
    "Ders materyalleri (slayt, kitap vb.) içeriklerin anlaşılmasına katkı sağlamıştır.",
    "Derslerde anlatılan konular ile yapılan sınavlar örtüşmektedir.",
    "Sınavların kapsamı ve zorluk düzeyi, dersin içeriğiyle uyumludur.",
    "Sınavlarda sorulan sorular öğrenme süreçlerini tamamlar niteliktedir.",
    "Bu öğretim elemanından başka dersler de almayı isterim.",
    "Bu derste edindiğim beceriler, mesleki yaşamdaki uygulamalara hazırlıklı olmamı sağlayacaktır.",
    "Bu dersin kariyer sınavlarında (mezuniyet sonrası) katkısı olacağını düşünüyorum.",
    "Bu ders, eleştirel düşünme ve analiz becerilerimi geliştirmeme katkı sağladı.",
    "Ders, kuramsal bilgiler ile uygulama arasındaki ilişkiyi kavramama yardımcı oldu."
]

options = ["Kesinlikle katılmıyorum", "Katılmıyorum", "Fikrim yok", "Katılıyorum", "Kesinlikle katılıyorum"]

st.set_page_config(page_title="Bölüm Anketi", layout="wide")
st.title("Ders Değerlendirme Anketi")

sinif = st.selectbox("Sınıfınızı Seçiniz:", list(ders_programi.keys()))
aktif_dersler = ders_programi[sinif]

form_cevaplari = []

for s_no, soru_metni in enumerate(sorular, 1):
    st.markdown(f"**Soru {s_no}:** {soru_metni}")
    cols = st.columns(len(aktif_dersler))
    for idx, ders in enumerate(aktif_dersler):
        with cols[idx]:
            cevap = st.radio(f"**{ders}**", options, index=2, key=f"q{s_no}_{ders}")
            form_cevaplari.append({"Sinif": sinif, "Ders": ders, "Soru_No": s_no, "Puan": cevap})
    st.divider()

if st.button("Anketi Tamamla ve Gönder"):
    # Google Apps Script'ten aldığınız URL'yi buraya yapıştırın
    script_url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec"
    
    with st.spinner('Kaydediliyor...'):
        try:
            response = requests.post(script_url, json=form_cevaplari)
            if response.text == "Başarılı":
                st.success("Cevaplarınız başarıyla kaydedildi!")
                st.balloons()
            else:
                st.error(f"Sunucu hatası: {response.text}")
        except Exception as e:
            st.error(f"Bağlantı hatası: {e}")