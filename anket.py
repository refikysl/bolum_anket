import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="SBKY Bölümü Ders Değerlendirme Anketi", layout="wide")

# 1. Ders Listesi
ders_programi = {
    "Sınıf 1": ["Medeniyet Tarihi 1", "Siyaset Bilimi 1", "Hukukun Temel Kavramları", "Sosyoloji", "Sosyal Bilimlerde İstatistik", "Türk İdare Tarihi", "Araştırma Yöntem ve Teknikleri"],
    "Sınıf 2": ["Anayasa Hukuku", "Kamu Yönetimi", "Yönetim Bilimi", "Siyasal Tarih", "İktisada Giriş"],
    "Sınıf 3": ["Yerel Yönetimler 1", "İdare Hukuku", "Karşılaştırmalı Kamu Yönetimi", "Temel Hak ve Hürriyetler", "AB Kurumları ve Politikaları", "Doğu Siyasal Düşünceler Tarihi", "Kültürel Haklar ve Siyaset", "Siyaset Sosyolojisi"],
    "Sınıf 4": ["Kamu Maliyesi", "Karş. Siyasal Sistemler", "Kentsel Politikalar", "Siyasal Antropoloji", "Ticaret Hukuku", "Uluslararası İktisat", "İnsan Kaynakları Yönetimi"]
}

# 2. 13 Akreditasyon Sorusu
sorular = [
    "Öğretim elemanı, ders konularına ilişkin ileri düzey akademik bilgiye sahiptir ve içeriği güncel gelişmelerle desteklemektedir",
    "Öğretim elemanı, dersi açık ve anlaşılır biçimde sunmaktadır",
    "Öğretim elemanına ofis saatlerinde ve ders dışı zamanlarda mail, sosyal medya ya da telefon yoluyla ulaşılabilmektedir",
    "Öğretim elemanı, öğrencileri derse katılım konusunda teşvik etmektedir. Sorulara ve eleştirilere açıktır",
    "Öğretim elemanı görsel ya da işitsel dijital materyalleri öğrenmeyi destekleyecek şekilde etkili kullanmaktadır",
    "Öğretim elemanı, ders saatlerine özen göstermektedir",
    "Bu öğretim elemanından başka dersler de almak isterim",
    "Derste kullanılan materyaller (kitap, not, slayt gibi) içeriklerin anlaşılmasına katkı sağlamıştır",
    "Sınavların kapsamı, zorluk düzeyi ve soru niteliği dersin öğrenme hedefleriyle örtüşmektedir",
    "Bu derste edindiğim bilgiler mesleki yaşamda hazırlıklı olmamı sağlayacaktır",
    "Bu derste edindiğim bilgilerin kariyer sınavlarında katkısı olacağını düşünüyorum",
    "Ders, eleştirel düşünme becerilerimi geliştirdi",
    "Ders, kuramsal bilgiler ile uygulama arasındaki ilişkiyi anlamama yardımcı oldu."
]

# Session State başlangıç değerleri
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'all_data' not in st.session_state:
    st.session_state.all_data = []
if 'selected_dersler' not in st.session_state:
    st.session_state.selected_dersler = []
if 'selected_sinif' not in st.session_state:
    st.session_state.selected_sinif = None

# Stil tanımları (değişmedi)
st.markdown("""
<style>
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #ff4b4b 0%, #ffa726 25%, #ffeb3b 50%, #4caf50 75%, #2e7d32 100%);
        height: 10px;
    }
    .stSlider > div > div > div > div > div {
        height: 24px;
        width: 24px;
    }
    .ders-baslik {
        font-size: 20px;
        font-weight: bold;
        color: #1e3a8a;
        margin-top: 5px;
        margin-bottom: 3px;
        padding: 8px;
        background-color: #f0f8ff;
        border-radius: 6px;
        border-left: 4px solid #1e3a8a;
    }
    .soru-ust-kisim {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .soru-numara {
        font-size: 24px;
        font-weight: bold;
        color: #ffd700;
        margin-bottom: 5px;
    }
    .soru-metni {
        font-size: 17px;
        line-height: 1.4;
    }
    .slider-etiket-konteynir {
        display: flex;
        justify-content: space-between;
        margin-top: 5px;
        margin-bottom: 8px;
    }
    .slider-etiket-sol, .slider-etiket-sag {
        font-size: 11px;
        line-height: 1.2;
        text-align: center;
        padding: 0 5px;
    }
    .etiket-buyuk {
        font-size: 16px;
        font-weight: bold;
        display: block;
    }
    .etiket-kucuk {
        font-size: 9px;
        display: block;
        line-height: 1.1;
    }
    .ders-konteynir {
        margin-bottom: 8px;
        padding-bottom: 8px;
        border-bottom: 1px solid #e0e0e0;
    }
    .puan-gostergesi {
        text-align: center;
        margin: 8px 0;
    }
    @media (max-width: 768px) {
        .ders-baslik { font-size: 18px; padding: 6px; }
        .soru-ust-kisim { padding: 12px 15px; }
        .soru-numara { font-size: 20px; }
        .soru-metni { font-size: 15px; }
    }
</style>
""", unsafe_allow_html=True)

# Başlık
st.title("🏛️ SBKY Bölümü Ders Değerlendirme Anketi")

# Adım 0: Sınıf ve ders seçimi
if st.session_state.current_step == 0:
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1e3a8a; margin-bottom: 25px; color: #000000;">
    <h4 style="color: #1e3a8a; margin-top: 0;">📝 Değerli Öğrencimiz,</h4>
    <p>Bölümümüzün eğitim kalitesini artırmak ve uluslararası akreditasyon standartlarına uyumunu değerlendirmek amacıyla düzenlenen bu anket, ders içerikleri ve öğretim süreçlerinin geliştirilmesine ışık tutacaktır.</p>
    <p>Öncelikle döneminizden aldığınız dersleri seçmeniz gerekmektedir. Seçiminize bağlı olarak yalnızca ilgili dersler değerlendirmenize sunulacaktır.</p>
    <p>Anket 13 sorudan oluşmaktadır. Her bir soru için aldığınız derslerin her biri için 1-5 arasında değerlendirme yapacaksınız.</p>
    <ul>
        <li>Kimlik bilgisi istenmemektedir.</li>
        <li>Yanıtlarınız sadece iyileştirme amacıyla kullanılacaktır.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.markdown("<h4>📋 Lütfen sınıfınızı seçiniz:</h4>", unsafe_allow_html=True)
    sinif = st.selectbox("", list(ders_programi.keys()), key="sinif_sec", label_visibility="collapsed")
    
    if st.session_state.selected_sinif != sinif:
        st.session_state.selected_dersler = []
        st.session_state.selected_sinif = sinif
    
    st.markdown(f"<h4>📚 {sinif} için derslerinizi seçiniz:</h4>", unsafe_allow_html=True)
    
    aktif_dersler = ders_programi[sinif]
    secilenler = []
    
    for ders in aktif_dersler:
        default = True
        if st.session_state.selected_dersler and ders not in st.session_state.selected_dersler:
            default = False
        if st.checkbox(ders, value=default, key=f"ch_{ders}"):
            secilenler.append(ders)
    
    st.session_state.selected_dersler = secilenler
    
    st.markdown("---")
    
    if len(secilenler) == 0:
        st.error("⚠️ En az bir ders seçmelisiniz!")
    else:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("✅ Ders seçimini tamamla ve başla", use_container_width=True, type="primary"):
                st.session_state.current_step = 1
                st.rerun()

# Soru sayfaları (1-13)
elif 1 <= st.session_state.current_step <= 13:
    s_idx = st.session_state.current_step - 1
    soru = sorular[s_idx]
    
    # SAYFA BAŞI ANCHOR
    st.markdown('<div id="question-top"></div>', unsafe_allow_html=True)
    
    # Sabit soru başlığı
    st.markdown(f"""
    <div class="soru-ust-kisim">
        <div class="soru-numara">❓ Soru {s_idx + 1} / 13</div>
        <div class="soru-metni">{soru}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="text-align: center; margin: 0 0 20px 0; padding: 10px; background: #f8f9fa; border-radius: 6px;">
    <strong>1 = Kesinlikle Katılmıyorum</strong>      
    <strong>5 = Kesinlikle Katılıyorum</strong>
    </div>
    """, unsafe_allow_html=True)
    
    aktif_dersler = st.session_state.selected_dersler
    responses = []
    
    for i, ders in enumerate(aktif_dersler, 1):
        st.markdown('<div class="ders-konteynir">', unsafe_allow_html=True)
        st.markdown(f'<div class="ders-baslik">{i}. {ders}</div>', unsafe_allow_html=True)
        
        st.markdown("""
        <div class="slider-etiket-konteynir">
            <div class="slider-etiket-sol"><span class="etiket-buyuk">1</span><span class="etiket-kucuk">Kesinlikle<br>Katılmıyorum</span></div>
            <div class="slider-etiket-sag"><span class="etiket-buyuk">5</span><span class="etiket-kucuk">Kesinlikle<br>Katılıyorum</span></div>
        </div>
        """, unsafe_allow_html=True)
        
        puan = st.slider("", 1, 5, 3, key=f"q{s_idx}_{ders}", label_visibility="collapsed")
        
        st.markdown(f"""
        <div class="puan-gostergesi">
            <div style="font-weight:bold; color:#1e3a8a;">Seçilen: <span style="font-size:20px;color:#3b82f6">{puan}</span></div>
            <div style="font-size:22px;letter-spacing:4px;">{'●' * puan}{'○' * (5-puan)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        responses.append({
            "Sinif": st.session_state.selected_sinif,
            "Ders": ders,
            "Soru_No": s_idx + 1,
            "Puan": puan
        })
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if s_idx < 12:
            btn_text = f"➡️ Sonraki Soru ({s_idx + 2}/13)"
        else:
            btn_text = "✅ Anketi Bitir"
        
        if st.button(btn_text, use_container_width=True, type="primary"):
            st.session_state.all_data.extend(responses)
            st.session_state.current_step += 1
            
            # En üste kaydırma komutu (gecikmeli)
            st.markdown("""
            <script>
            setTimeout(function() {
                window.scrollTo({ top: 0, behavior: 'instant' });
            }, 100);
            </script>
            """, unsafe_allow_html=True)
            
            st.rerun()

# Son ekran - Gönderme
else:
    st.success("🎉 Tebrikler! Tüm soruları tamamladınız.")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🚀 VERİLERİ GÖNDER", use_container_width=True, type="primary"):
            url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec"
            
            with st.spinner("Kaydediliyor..."):
                try:
                    resp = requests.post(url, json=st.session_state.all_data)
                    if "Başarılı" in resp.text:
                        st.balloons()
                        st.success("✅ Veriler başarıyla kaydedildi!")
                        # Sıfırlama
                        for key in list(st.session_state.keys()):
                            del st.session_state[key]
                        st.rerun()
                    else:
                        st.error("Gönderme sırasında hata: " + resp.text)
                except Exception as e:
                    st.error(f"Bağlantı hatası: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<p style='text-align:center; color:#666; font-size:14px;'>SBKY Bölümü Ders Değerlendirme Anketi</p>", unsafe_allow_html=True)