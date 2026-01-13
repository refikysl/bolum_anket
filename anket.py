import streamlit as st
import pandas as pd
import requests

# Sayfa Ayarları
st.set_page_config(page_title="SBKY Bölümü Ders Değerlendirme Anketi", layout="wide")

# 1. Ders Listesi (Değişmedi)
ders_programi = {
    "Sınıf 1": ["Medeniyet Tarihi 1", "Siyaset Bilimi 1", "Hukukun Temel Kavramları", "Sosyoloji", "Sosyal Bilimlerde İstatistik", "Türk İdare Tarihi", "Araştırma Yöntem ve Teknikleri"],
    "Sınıf 2": ["Anayasa Hukuku", "Kamu Yönetimi", "Yönetim Bilimi", "Siyasal Tarih", "İktisada Giriş"],
    "Sınıf 3": ["Yerel Yönetimler 1", "İdare Hukuku", "Karşılaştırmalı Kamu Yönetimi", "Temel Hak ve Hürriyetler", "AB Kurumları ve Politikaları", "Doğu Siyasal Düşünceler Tarihi", "Kültürel Haklar ve Siyaset", "Siyaset Sosyolojisi"],
    "Sınıf 4": ["Kamu Maliyesi", "Karş. Siyasal Sistemler", "Kentsel Politikalar", "Siyasal Antropoloji", "Ticaret Hukuku", "Uluslararası İktisat", "İnsan Kaynakları Yönetimi"]
}

# 2. Güncellenmiş 13 Akreditasyon Sorusu
sorular = [
    "Öğretim elemanı, ders konularına ilişkin ileri düzey akademik bilgiye sahiptir ve içeriği güncel gelişmelerle desteklemektedir",
    "Öğretim elemanı, dersi açık ve anlaşılır biçimde sunmaktadır",
    "Öğretim elemanına ofis saatlerinde ve ders dışı zamanlarda mail, sosyal medya ya da telefon yoluyla ulaşılabilmektedir",
    "Öğretim elemanı, öğrencileri derse katılım konusunda teşvik etmektedir. Sorulara ve eleştirilere açıktır",
    "Öğretim elemanı  görsel ya da işitsel dijital materyalleri öğrenmeyi destekleyecek şekilde etkili kullanmaktadır",
    "Öğretim elemanı, ders saatlerine özen göstermektedir",
    "Bu öğretim elemanından başka dersler de almak isterim",
    "Derste kullanılan materyaller (kitap, not, slayt gibi) içeriklerin anlaşılmasına katkı sağlamıştır",
    "Sınavların kapsamı, zorluk düzeyi ve soru niteliği dersin öğrenme hedefleriyle örtüşmektedir",
    "Bu derste edindiğim bilgiler mesleki yaşamda hazırlıklı olmamı sağlayacaktır",
    "Bu derste edindiğim bilgilerin kariyer sınavlarında katkısı olacağını düşünüyorum",
    "Ders, eleştirel düşünme becerilerimi geliştirdi",
    "Ders, kuramsal bilgiler ile uygulama arasındaki ilişkiyi anlamama yardımcı oldu."
]

# --- DURUM YÖNETİMİ ---
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'all_data' not in st.session_state:
    st.session_state.all_data = []
if 'selected_dersler' not in st.session_state:
    st.session_state.selected_dersler = []
if 'selected_sinif' not in st.session_state:
    st.session_state.selected_sinif = None

# --- STİL - MİNİMAL VE KOMPAKT ---
st.markdown("""
<style>
    /* Ana container - minimum padding */
    .main .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }
    
    /* SORU BAŞLIĞI - KOMPAKT */
    .soru-ust-kisim {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 10px;
        position: sticky;
        top: 0;
        z-index: 100;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .soru-numara {
        font-size: 18px;
        font-weight: bold;
        color: #ffd700;
        margin-bottom: 2px;
    }
    
    .soru-metni {
        font-size: 14px;
        line-height: 1.2;
    }
    
    /* DERS SATIRI - ÇOK KOMPAKT, YAN YANA */
    .ders-satiri {
        display: flex;
        align-items: center;
        margin: 0 !important;
        padding: 4px 0 !important;
        border-bottom: 1px solid #f0f0f0;
        min-height: 40px;
    }
    
    .ders-adi {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #1e3a8a !important;
        width: 45% !important;
        padding-right: 10px !important;
        margin: 0 !important;
        display: flex;
        align-items: center;
    }
    
    /* SLİDER - TEK PARÇA, DAR */
    .slider-konteynir {
        width: 55% !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stSlider {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stSlider > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stSlider > div > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stSlider > div > div > div {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #ff4b4b 0%, #ffa726 25%, #ffeb3b 50%, #4caf50 75%, #2e7d32 100%);
        height: 6px !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .stSlider > div > div > div > div > div {
        height: 18px !important;
        width: 18px !important;
        margin: 0 !important;
    }
    
    /* Slider değer göstergesi - slider'ın üzerinde */
    .slider-deger {
        font-size: 12px;
        font-weight: bold;
        color: #1e3a8a;
        text-align: center;
        margin-top: 2px;
    }
    
    /* Ölçek açıklaması - küçük */
    .olcek-aciklama {
        text-align: center;
        margin: 5px 0 8px 0;
        padding: 4px;
        background: #f8f9fa;
        border-radius: 4px;
        border: 1px solid #e0e0e0;
        font-size: 11px;
        color: #666;
    }
    
    /* Buton */
    .stButton > button {
        margin: 5px 0 !important;
        padding: 8px !important;
        font-size: 14px !important;
    }
    
    /* MOBİL İÇİN */
    @media (max-width: 768px) {
        .soru-ust-kisim {
            padding: 6px 10px;
            margin-bottom: 8px;
        }
        
        .soru-numara {
            font-size: 16px;
        }
        
        .soru-metni {
            font-size: 13px;
        }
        
        .ders-adi {
            font-size: 14px !important;
            width: 50% !important;
        }
        
        .slider-konteynir {
            width: 50% !important;
        }
        
        .olcek-aciklama {
            font-size: 10px;
            padding: 3px;
            margin: 3px 0 6px 0;
        }
        
        .slider-deger {
            font-size: 11px;
        }
    }
    
    /* Çok küçük ekranlar için */
    @media (max-width: 480px) {
        .ders-adi {
            font-size: 13px !important;
            width: 55% !important;
        }
        
        .slider-konteynir {
            width: 45% !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- ANA SAYFA ---
st.title("🏛️ SBKY Bölümü Ders Değerlendirme Anketi")

# --- SORU 0: SINIF VE DERS SEÇİMİ ---
if st.session_state.current_step == 0:
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 12px; border-radius: 6px; border-left: 4px solid #1e3a8a; margin-bottom: 15px; color: #000000;">
    <h4 style="color: #1e3a8a; margin-top: 0; font-size: 16px;">📝 Değerli Öğrencimiz,</h4>
    <p style="font-size: 13px; margin-bottom: 8px;">Bölümümüzün eğitim kalitesini artırmak için düzenlenen bu ankette, lütfen derslerinizi değerlendiriniz.</p>
    <p style="font-size: 13px; margin-bottom: 8px;"><strong>Adımlar:</strong></p>
    <ol style="font-size: 13px; margin-bottom: 8px;">
        <li>Sınıfınızı seçin</li>
        <li>Aldığınız dersleri işaretleyin</li>
        <li>13 soruyu yanıtlayın (her soru için derslere 1-5 arası puan verin)</li>
    </ol>
    <p style="font-size: 12px; margin-bottom: 0;"><em>Anket tamamen anonimdir. Teşekkür ederiz.</em></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sınıf seçimi
    st.markdown("<h4 style='font-size: 16px; margin-bottom: 8px;'>📋 Sınıfınızı Seçiniz:</h4>", unsafe_allow_html=True)
    sinif = st.selectbox(
        "",
        list(ders_programi.keys()),
        key="sinif_secimi",
        label_visibility="collapsed"
    )
    
    # Sınıf değiştiyse seçili dersleri sıfırla
    if st.session_state.selected_sinif != sinif:
        st.session_state.selected_dersler = []
        st.session_state.selected_sinif = sinif
    
    st.markdown("---")
    
    # Ders seçimi
    st.markdown(f"<h4 style='font-size: 16px; margin-bottom: 8px;'>📚 {sinif} Dersleriniz:</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin-bottom: 8px;'><strong>Bu yarıyılda aldığınız dersleri işaretleyiniz.</strong></p>", unsafe_allow_html=True)
    
    aktif_dersler = ders_programi[sinif]
    selected_dersler = []
    
    # Tüm dersleri checkbox'larla göster - kompakt
    cols = st.columns(2)
    for idx, ders in enumerate(aktif_dersler):
        col_idx = idx % 2
        with cols[col_idx]:
            # Varsayılan olarak tüm dersler seçili
            default_value = True
            if st.session_state.selected_dersler and ders not in st.session_state.selected_dersler:
                default_value = False
                
            if st.checkbox(ders, value=default_value, key=f"ders_checkbox_{ders}"):
                selected_dersler.append(ders)
    
    st.session_state.selected_dersler = selected_dersler
    
    st.markdown("---")
    
    # İlerleme butonu
    if len(selected_dersler) == 0:
        st.error("⚠️ **Lütfen en az bir ders seçiniz!**")
    else:
        if st.button("✅ Ders Seçimini Tamamla ve Sorulara Başla", use_container_width=True, type="primary"):
            st.session_state.current_step = 1
            st.rerun()

# --- ANKET SORULARI (1-13) ---
elif 1 <= st.session_state.current_step <= 13:
    s_no = st.session_state.current_step - 1  # Soru indeksi (0-12)
    soru_metni = sorular[s_no]
    
    # Sadece seçili dersleri kullan
    aktif_dersler = st.session_state.selected_dersler
    
    # SABİT SORU BAŞLIĞI - ÇOK KOMPAKT
    st.markdown(f"""
    <div class="soru-ust-kisim">
        <div class="soru-numara">❓ Soru {s_no + 1} / 13</div>
        <div class="soru-metni">{soru_metni}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ölçek açıklaması - ÇOK KÜÇÜK
    st.markdown("""
    <div class="olcek-aciklama">
        <strong>1 = Kesinlikle Katılmıyorum</strong> | <strong>5 = Kesinlikle Katılıyorum</strong>
    </div>
    """, unsafe_allow_html=True)
    
    current_responses = []
    
    # Dersleri TEK SATIRDA gösteriyoruz - DERS ADI + SLİDER YAN YANA
    for idx, ders in enumerate(aktif_dersler):
        # Tek satır container
        st.markdown(f'<div class="ders-satiri" id="ders_{idx}">', unsafe_allow_html=True)
        
        # Ders adı - sol taraf
        col1, col2 = st.columns([4.5, 5.5])
        
        with col1:
            st.markdown(f'<div class="ders-adi">{idx+1}. {ders}</div>', unsafe_allow_html=True)
        
        with col2:
            # Puanlama slider'ı (1-5) - TEK PARÇA, DAR
            puan = st.slider(
                "",
                min_value=1,
                max_value=5,
                value=3,
                key=f"step_{s_no}_{ders}",
                label_visibility="collapsed"
            )
            
            # Puan değeri slider'ın altında küçük yazı
            st.markdown(f'<div class="slider-deger">{puan}</div>', unsafe_allow_html=True)
        
        current_responses.append({
            "Sinif": st.session_state.selected_sinif, 
            "Ders": ders, 
            "Soru_No": s_no + 1, 
            "Puan": puan
        })
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dersler bittikten sonra boşluk
    st.markdown("<br>", unsafe_allow_html=True)
    
    # İlerleme butonu
    if s_no < 12:  # Soru 1-12 için
        button_label = f"➡️ Sonraki Soru ({s_no + 2}/13)"
    else:  # Son soru için
        button_label = "✅ Tüm Soruları Tamamla"
    
    if st.button(button_label, use_container_width=True, type="primary"):
        # Verileri kaydet
        st.session_state.all_data.extend(current_responses)
        st.session_state.current_step += 1
        st.rerun()

# --- GÖNDERME EKRANI ---
else:
    st.success("🎉 **Tebrikler! Tüm soruları tamamladınız.**")
    
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 12px; border-radius: 6px; border-left: 4px solid #1e3a8a; margin-bottom: 15px;">
    <h4 style="color: #1e3a8a; margin-top: 0; font-size: 16px;">📋 Yanıtlarınız Hazır</h4>
    <p style="font-size: 13px;">Aşağıdaki butona tıklayarak yanıtlarınızı sisteme gönderebilirsiniz.</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 VERİLERİ GÖNDER", use_container_width=True, type="primary"):
        script_url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec" 
        
        with st.spinner('Verileriniz kaydediliyor...'):
            try:
                response = requests.post(script_url, json=st.session_state.all_data)
                if response.text == "Başarılı":
                    st.balloons()
                    st.success("✅ **Tüm verileriniz başarıyla kaydedildi!**")
                    st.info("**Anketi tamamladığınız için teşekkür ederiz.**")
                    
                    # Otomatik sıfırlama
                    st.session_state.current_step = 0
                    st.session_state.all_data = []
                    st.session_state.selected_dersler = []
                    st.session_state.selected_sinif = None
                    st.rerun()
                else:
                    st.error(f"❌ **Hata oluştu:** {response.text}")
                    st.info("Lütfen sayfayı yenileyip tekrar deneyiniz.")
            except Exception as e:
                st.error(f"❌ **Bağlantı hatası:** {e}")
                st.info("Lütfen internet bağlantınızı kontrol edip tekrar deneyiniz.")

# --- GENEL SAYFA AYAK BİLGİSİ ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; font-size: 11px; margin-top: 15px;">
<p><strong>SBKY Bölümü Ders Değerlendirme Anketi</strong></p>
</div>
""", unsafe_allow_html=True)