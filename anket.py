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
if 'radio_selections' not in st.session_state:
    st.session_state.radio_selections = {}

# --- STİL - MİNİMAL, SIFIR BOŞLUK ---
st.markdown("""
<style>
    /* Ana container - sıfır padding */
    .main .block-container {
        padding-top: 0.2rem !important;
        padding-bottom: 0.2rem !important;
    }
    
    /* SORU BAŞLIĞI - BÜYÜK PUNTOLU */
    .soru-ust-kisim {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 8px 12px;
        border-radius: 5px;
        margin-bottom: 5px;
        position: sticky;
        top: 0;
        z-index: 100;
    }
    
    .soru-numara {
        font-size: 20px !important;
        font-weight: bold !important;
        color: #ffd700 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .soru-metni {
        font-size: 18px !important;
        line-height: 1.3 !important;
        margin: 3px 0 0 0 !important;
        padding: 0 !important;
        color: white !important;
        font-weight: 600 !important;
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
        margin: 10px 0 !important;
        padding: 10px !important;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        background-color: #f9f9f9;
    }
    
    /* DERS ADI - BÜYÜK, BEYAZ, OKUNAKLI */
    .ders-adi {
        font-size: 18px !important;
        font-weight: 700 !important;
        color: white !important;
        margin: 0 0 10px 0 !important;
        padding: 8px 12px !important;
        display: block;
        background-color: rgba(30, 58, 138, 0.9);
        border-radius: 6px;
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
    }
    
    /* RADIO BUTON STİLİ */
    .stRadio > div {
        background-color: white;
        padding: 10px;
        border-radius: 6px;
        border: 1px solid #e0e0e0;
    }
    
    /* RADIO BUTON ETİKETLERİ */
    .stRadio > div > label {
        font-size: 14px !important;
    }
    
    /* RADIO BUTON KONTEYNIRI */
    .radio-container {
        display: flex;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 5px;
    }
    
    /* RADIO BUTON ÖĞELERİ */
    .radio-item {
        flex: 1;
        min-width: 60px;
        text-align: center;
        padding: 5px;
        border-radius: 4px;
        background-color: #f8f9fa;
        border: 1px solid #e0e0e0;
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
            padding: 6px 10px;
            margin-bottom: 4px;
        }
        
        .soru-numara {
            font-size: 18px !important;
        }
        
        .soru-metni {
            font-size: 16px !important;
        }
        
        .ders-adi {
            font-size: 16px !important;
            padding: 6px 10px !important;
        }
        
        .olcek-aciklama {
            font-size: 10px;
            padding: 2px;
            margin: 2px 0 4px 0;
        }
        
        .radio-item {
            min-width: 50px;
            padding: 4px;
            font-size: 12px;
        }
    }
    
    /* Çok küçük ekranlar için */
    @media (max-width: 480px) {
        .soru-metni {
            font-size: 15px !important;
        }
        
        .ders-adi {
            font-size: 15px !important;
        }
        
        .radio-container {
            flex-direction: column;
        }
        
        .radio-item {
            min-width: 100%;
            margin-bottom: 5px;
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
                st.session_state.radio_selections = {}
                st.rerun()

# --- ANKET SORULARI (1-13) ---
elif 1 <= st.session_state.current_step <= 13:
    s_no = st.session_state.current_step - 1  # Soru indeksi (0-12)
    soru_metni = sorular[s_no]
    
    # Sadece seçili dersleri kullan
    aktif_dersler = st.session_state.selected_dersler
    
    # SABİT SORU BAŞLIĞI - BÜYÜK PUNTOLU
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
    
    # BUTONU ÜSTE YERLEŞTİR
    if s_no < 12:  # Soru 1-12 için
        button_label = f"➡️ Sonraki Soru ({s_no + 2}/13)"
    else:  # Son soru için
        button_label = "✅ Tüm Soruları Tamamla"
    
    # Tüm radio button'ların seçilip seçilmediğini kontrol et
    all_radio_selected = True
    radio_key = f"radio_{s_no}"
    
    if radio_key not in st.session_state.radio_selections:
        st.session_state.radio_selections[radio_key] = {}
    
    for ders in aktif_dersler:
        ders_key = f"{radio_key}_{ders}"
        if ders_key not in st.session_state.radio_selections[radio_key]:
            all_radio_selected = False
    
    # Buton konteyneri - SAYFA BAŞINDA (HER ZAMAN DEVRE DIŞI BAŞLAT)
    col_top1, col_top2, col_top3 = st.columns([1, 2, 1])
    with col_top2:
        # Buton her zaman başlangıçta devre dışı
        next_button_disabled = not all_radio_selected
        
        next_button_clicked = st.button(
            button_label,
            key=f"top_button_{s_no}",
            use_container_width=True,
            disabled=next_button_disabled,  # Sadece tüm radio button'lar seçilmişse aktif
            type="primary"
        )
    
    current_responses = []
    
    # Dersleri ÜST ÜSTE - SIFIR BOŞLUK
    for idx, ders in enumerate(aktif_dersler):
        # Ders bloğu
        st.markdown(f'<div class="ders-blok" id="ders_{idx}">', unsafe_allow_html=True)
        
        # Ders adı - BÜYÜK, BEYAZ, OKUNAKLI
        st.markdown(f'<div class="ders-adi">{idx+1}. {ders}</div>', unsafe_allow_html=True)
        
        # Puanlama radio button'ları (1-5)
        ders_key = f"{radio_key}_{ders}"
        
        # Radio button seçenekleri
        options = {
            "1": "Kesinlikle Katılmıyorum",
            "2": "Katılmıyorum", 
            "3": "Kararsızım",
            "4": "Katılıyorum",
            "5": "Kesinlikle Katılıyorum"
        }
        
        # Radio button'u yatay olarak göster
        selected_option = st.radio(
            "",
            options=list(options.keys()),
            format_func=lambda x: f"{x} - {options[x]}",
            key=ders_key,
            horizontal=True,
            label_visibility="collapsed"
        )
        
        # Seçimi kaydet
        if selected_option:
            st.session_state.radio_selections[radio_key][ders_key] = True
            
            # Puanı sayıya çevir
            puan = int(selected_option)
            
            current_responses.append({
                "Sinif": st.session_state.selected_sinif, 
                "Ders": ders, 
                "Soru_No": s_no + 1, 
                "Puan": puan
            })
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Kaç dersin değerlendirildiğini göster
    selected_count = len(st.session_state.radio_selections[radio_key])
    total_count = len(aktif_dersler)
    
    # "TÜM DERSLERİ DEĞERLENDİRDİM" BUTONU - ÖNCE BU
    col_check1, col_check2, col_check3 = st.columns([1, 2, 1])
    with col_check2:
        if st.button("✓ Tüm Dersleri Değerlendirdim", key=f"check_{s_no}", use_container_width=True):
            # Tüm radio button'ların seçilip seçilmediğini kontrol et
            all_selected = True
            missing_dersler = []
            
            for ders in aktif_dersler:
                ders_key = f"{radio_key}_{ders}"
                if ders_key not in st.session_state.radio_selections[radio_key]:
                    all_selected = False
                    missing_dersler.append(ders)
            
            if all_selected:
                st.success("✓ Tüm dersleri değerlendirdiniz! Şimdi sayfa başına gidip 'Sonraki Soru' butonunu kullanabilirsiniz.")
                st.rerun()
            else:
                missing_list = ", ".join(missing_dersler)
                st.error(f"❌ Hala bazı dersleri değerlendirmediniz! Lütfen şu dersleri değerlendirin: {missing_list}")
    
    # Dersler bittikten sonra HER SORU İÇİN MESAJ (1-12. sorular için) - SONRA BU
    if s_no < 12:  # Sadece 1-12. sorular için
        st.markdown("""
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 5px solid #ffc107; margin: 15px 0; color: #000000;">
        <h4 style="color: #856404; margin-top: 0;">📋 Önemli Hatırlatma</h4>
        <p><strong>Şimdi cevaplarınızı kontrol ederek sayfa başına gidiniz ve sonraki soruya geçiniz.</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Değerlendirme durumu bilgisi
    if selected_count < total_count:
        st.warning(f"⚠️ **{selected_count}/{total_count} dersi değerlendirdiniz.** Lütfen tüm dersleri değerlendirip yukarıdaki 'Tüm Dersleri Değerlendirdim' butonuna basınız.")
    
    # Buton tıklandıysa ve tüm radio button'lar seçildiyse işle
    if next_button_clicked:
        if all_radio_selected:
            # Verileri kaydet
            st.session_state.all_data.extend(current_responses)
            st.session_state.current_step += 1
            st.rerun()
        else:
            st.error("❌ **Lütfen tüm dersleri değerlendiriniz!** Her bir ders için bir puan seçmelisiniz.")

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
                        st.session_state.radio_selections = {}
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