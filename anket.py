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

# --- STİL - MİNİMAL, SIFIR BOŞLUK ---
st.markdown("""
<style>
    /* Ana container - sıfır padding */
    .main .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
    }
    
    /* SORU BAŞLIĞI - KOMPAKT */
    .soru-ust-kisim {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 6px 10px;
        border-radius: 5px;
        margin-bottom: 5px;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .soru-numara {
        font-size: 18px;
        font-weight: bold;
        color: #ffd700;
        margin: 0;
        padding: 0;
    }
    
    .soru-metni {
        font-size: 14px;
        line-height: 1.2;
        margin: 2px 0 0 0;
        padding: 0;
    }
    
    /* ÖLÇEK AÇIKLAMASI - KÜÇÜK */
    .olcek-aciklama {
        text-align: center;
        margin: 2px 0 5px 0;
        padding: 3px;
        background: #f8f9fa;
        border-radius: 3px;
        border: 1px solid #e0e0e0;
        font-size: 11px;
        color: #666;
    }
    
    /* DERS BLOĞU - SIFIR BOŞLUK */
    .ders-blok {
        margin: 0 !important;
        padding: 0 !important;
        border-bottom: 1px solid #f0f0f0;
    }
    
    /* DERS ADI - BÜYÜK, BEYAZ, OKUNAKLI */
    .ders-adi {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: white !important;
        margin: 3px 0 1px 0 !important;
        padding: 4px 5px !important;
        display: block;
        background-color: rgba(30, 58, 138, 0.9);
        border-radius: 4px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* SLİDER - TEK PARÇA, İNCE */
    .stSlider {
        margin: 0 !important;
        padding: 0 5px 5px 5px !important;
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
        height: 16px !important;
        width: 16px !important;
        margin: 0 !important;
    }
    
    /* Buton */
    .stButton > button {
        margin: 8px 0 5px 0 !important;
        padding: 8px !important;
        font-size: 14px !important;
    }
    
    /* MOBİL İÇİN */
    @media (max-width: 768px) {
        .soru-ust-kisim {
            padding: 5px 8px;
            margin-bottom: 4px;
        }
        
        .soru-numara {
            font-size: 16px;
        }
        
        .soru-metni {
            font-size: 13px;
        }
        
        .ders-adi {
            font-size: 16px !important;
            padding: 3px 4px !important;
        }
        
        .olcek-aciklama {
            font-size: 10px;
            padding: 2px;
            margin: 2px 0 4px 0;
        }
        
        .stSlider {
            padding: 0 5px 4px 5px !important;
        }
    }
    
    /* Çok küçük ekranlar için */
    @media (max-width: 480px) {
        .ders-adi {
            font-size: 15px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- ANA SAYFA - SADECE SORU 0'DA GÖSTER ---
if st.session_state.current_step == 0:
    st.title("🏛️ SBKY Bölümü Ders Değerlendirme Anketi")

# --- SORU 0: SINIF VE DERS SEÇİMİ ---
if st.session_state.current_step == 0:
    st.markdown("""
    <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1e3a8a; margin-bottom: 25px; color: #000000;">
    <h4 style="color: #1e3a8a; margin-top: 0;">📝 Değerli Öğrencimiz,</h4>
    <p>Bölümümüzün eğitim kalitesini artırmak ve uluslararası akreditasyon standartlarına uyumunu değerlendirmek amacıyla düzenlenen bu anket, ders içerikleri ve öğretim süreçlerinin geliştirilmesine ışık tutacaktır.</p>
    <p>Öncelikle döneminizden aldığınız dersleri seçmeniz gerekmektedir. Seçiminize bağlı olarak yalnızca ilgili dersler değerlendirmenize sunulacaktır. Herhangi bir sebeple alamadığınız ders varsa başındaki onay işaretini kaldırarak dersi değerlendirme dışı bırakınız.</p>
    <p>Anket 13 sorudan oluşmaktadır. Her bir soru aslında derse ya da dersi veren öğretim üyesine yönelik bir ifadedir. Altında aldığınız derslerin her biri için yukarıda yer alan ifadeye katılıp katılmadığınızı belirtebileceğiniz bir değerlendirme barı açılacaktır.</p>
    <p>Ankette yer alan ifadelere dair değerlendirmenizi, her bir ifadenin altında bulunan 1 (Kesinlikle Katılmıyorum) ile 5 (Kesinlikle Katılıyorum) arasında değerlendirme barını sağa ve sola hareket ettirerek belirtebilirsiniz. Barı, görüşünüzü en iyi yansıtan düzeye kaydırarak puanlamanızı tamamlayınız.</p>
    <ul>
        <li>Katılımcılardan herhangi bir kimlik bilgisi ya da tanımlayıcı bilgi istenmemektedir.</li>
        <li>Vereceğiniz yanıtlar yalnızca akademik iyileştirme çalışmalarında kullanılacaktır.</li>
        <li>Eğitim kalitemize sağladığınız değerli katkılar için teşekkür ederiz.</li>
    </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sınıf seçimi
    st.markdown("<h4>📋 Lütfen sınıfınızı seçiniz:</h4>", unsafe_allow_html=True)
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
    st.markdown(f"<h4>📚 {sinif} için derslerinizi seçiniz:</h4>", unsafe_allow_html=True)
    st.markdown("**Lütfen bu yarıyılda almakta olduğunuz dersleri işaretleyiniz.** Almadığınız derslerin işaretini kaldırınız.")
    
    aktif_dersler = ders_programi[sinif]
    selected_dersler = []
    
    # Tüm dersleri checkbox'larla göster
    for ders in aktif_dersler:
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
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("✅ Ders Seçimini Tamamla ve Sorulara Başla", use_container_width=True, type="primary"):
                st.session_state.current_step = 1
                st.rerun()

# --- ANKET SORULARI (1-13) ---
elif 1 <= st.session_state.current_step <= 13:
    s_no = st.session_state.current_step - 1  # Soru indeksi (0-12)
    soru_metni = sorular[s_no]
    
    # Sadece seçili dersleri kullan
    aktif_dersler = st.session_state.selected_dersler
    
    # SABİT SORU BAŞLIĞI - KOMPAKT
    st.markdown(f"""
    <div class="soru-ust-kisim">
        <div class="soru-numara">❓ Soru {s_no + 1} / 13</div>
        <div class="soru-metni">{soru_metni}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Ölçek açıklaması - KÜÇÜK
    st.markdown("""
    <div class="olcek-aciklama">
        <strong>1 = Kesinlikle Katılmıyorum</strong> | <strong>5 = Kesinlikle Katılıyorum</strong>
    </div>
    """, unsafe_allow_html=True)
    
    current_responses = []
    
    # Dersleri ÜST ÜSTE - SIFIR BOŞLUK
    for idx, ders in enumerate(aktif_dersler):
        # Ders bloğu
        st.markdown(f'<div class="ders-blok" id="ders_{idx}">', unsafe_allow_html=True)
        
        # Ders adı - BÜYÜK, BEYAZ, OKUNAKLI
        st.markdown(f'<div class="ders-adi">{idx+1}. {ders}</div>', unsafe_allow_html=True)
        
        # Puanlama slider'ı (1-5) - ALTTA, TEK PARÇA
        puan = st.slider(
            "",  # Boş label
            min_value=1,
            max_value=5,
            value=3,  # Varsayılan orta değer
            key=f"step_{s_no}_{ders}",
            label_visibility="collapsed"
        )
        
        current_responses.append({
            "Sinif": st.session_state.selected_sinif, 
            "Ders": ders, 
            "Soru_No": s_no + 1, 
            "Puan": puan
        })
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dersler bittikten sonra küçük boşluk
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
    <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; border-left: 5px solid #1e3a8a; margin-bottom: 25px;">
    <h4 style="color: #1e3a8a; margin-top: 0;">📋 Yanıtlarınız Hazır</h4>
    <p>Aşağıdaki butona tıklayarak yanıtlarınızı sisteme gönderebilirsiniz.</p>
    <p><strong>Not:</strong> Göndermeden önce, tüm soruları yanıtladığınızdan emin olunuz.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 VERİLERİ GÖNDER", use_container_width=True, type="primary"):
            script_url = "https://script.google.com/macros/s/AKfycbwjMMwluGWitBAfCL5gQlNnPH7wzp_9Ailz1yS9bHhfch5U5wRGQvjXv_khBU5aEMX_/exec" 
            
            with st.spinner('Verileriniz kaydediliyor... Lütfen bekleyiniz.'):
                try:
                    response = requests.post(script_url, json=st.session_state.all_data)
                    if response.text == "Başarılı":
                        st.balloons()
                        st.success("✅ **Tüm verileriniz başarıyla kaydedildi!**")
                        st.info("""
                        **Anketi tamamladığınız için teşekkür ederiz.**  
                        Eğitim kalitemizi artırmamıza yardımcı olduğunuz için minnettarız.
                        """)
                        
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
<div style="text-align: center; color: #666; font-size: 12px; margin-top: 20px;">
<p><strong>SBKY Bölümü Ders Değerlendirme Anketi</strong></p>
<p>Bu anket, bölümümüzün eğitim kalitesini artırmak ve akreditasyon sürecine katkı sağlamak amacıyla düzenlenmiştir.</p>
</div>
""", unsafe_allow_html=True)