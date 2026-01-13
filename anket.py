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

# --- STİL ---
st.markdown("""
<style>
    /* Rengarenk slider için özel stil */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #ff4b4b 0%, #ffa726 25%, #ffeb3b 50%, #4caf50 75%, #2e7d32 100%);
        height: 10px;
    }
    
    /* Slider handle */
    .stSlider > div > div > div > div > div {
        height: 24px;
        width: 24px;
    }
    
    /* Ders başlıkları - tüm ekranlar için optimize */
    .ders-baslik {
        font-size: 20px !important;
        font-weight: bold !important;
        color: var(--text-color) !important;
        margin-top: 15px !important;
        margin-bottom: 5px !important;
        padding: 8px 12px !important;
        background-color: var(--background-color) !important;
        border-radius: 8px !important;
        border-left: 4px solid #1e3a8a !important;
    }
    
    /* SABİT SORU BAŞLIĞI - STICKY */
    .soru-sticky-header {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%) !important;
        color: white !important;
        padding: 15px !important;
        z-index: 9999 !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
        border-bottom: 3px solid #ffd700 !important;
    }
    
    /* Soru başlığı içindeki metinler */
    .soru-sticky-header h3 {
        color: white !important;
        margin: 0 !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    
    .soru-sticky-header .soru-numara {
        font-size: 24px !important;
        font-weight: bold !important;
        color: #ffd700 !important;
        margin-right: 10px !important;
    }
    
    .soru-sticky-header .soru-metni {
        font-size: 16px !important;
        line-height: 1.4 !important;
    }
    
    .soru-sticky-header .toplam-soru {
        font-size: 14px !important;
        color: #cbd5e1 !important;
        margin-left: 5px !important;
    }
    
    /* Ana içeriği sticky header'ın altına itmek için */
    .main-content {
        padding-top: 150px !important;
    }
    
    @media (max-width: 768px) {
        .soru-sticky-header {
            padding: 12px !important;
        }
        .soru-sticky-header h3 {
            font-size: 16px !important;
        }
        .soru-sticky-header .soru-metni {
            font-size: 14px !important;
        }
        .main-content {
            padding-top: 140px !important;
        }
    }
    
    /* Bilgi kutusu */
    .bilgi-kutusu {
        background-color: #f0f8ff !important;
        padding: 20px !important;
        border-radius: 10px !important;
        border-left: 5px solid #1e3a8a !important;
        margin-bottom: 25px !important;
        color: #000000 !important;
    }
    
    .bilgi-kutusu h4 {
        color: #1e3a8a !important;
        margin-top: 0 !important;
    }
    
    .bilgi-kutusu p, .bilgi-kutusu li {
        color: #000000 !important;
        font-size: 16px !important;
    }
    
    /* Slider etiketleri - kompakt ve iki satır */
    .slider-etiket-konteynir {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-top: 5px;
        margin-bottom: 10px;
        width: 100%;
    }
    
    .slider-etiket-sol {
        text-align: left;
        font-size: 10px !important;
        line-height: 1.2;
        max-width: 45%;
    }
    
    .slider-etiket-sag {
        text-align: right;
        font-size: 10px !important;
        line-height: 1.2;
        max-width: 45%;
    }
    
    .etiket-buyuk {
        font-size: 14px !important;
        font-weight: bold;
    }
    
    .etiket-kucuk {
        font-size: 9px !important;
    }
    
    /* Puan daireleri */
    .puan-daireleri {
        text-align: center;
        margin-top: 5px;
        margin-bottom: 15px;
    }
    
    /* Ders konteynır */
    .ders-konteynir {
        margin-bottom: 15px !important;
        padding-bottom: 10px !important;
        border-bottom: 1px solid #e0e0e0;
    }
    
    /* Tema uyumlu renk değişkenleri */
    :root {
        --text-color: #000000;
        --background-color: #ffffff;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --text-color: #ffffff;
            --background-color: #0e1117;
        }
        .ders-baslik {
            background-color: #1e1e1e !important;
            border-left: 4px solid #4a90e2 !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- JavaScript for scrolling and sticky header ---
st.markdown("""
<script>
    // Sayfa yüklendiğinde başa git ve sticky header'ı ayarla
    function initPage() {
        // Sayfanın başına git
        window.scrollTo(0, 0);
        
        // Ana içeriği sticky header'ın altına it
        const mainContent = document.querySelector('.main .block-container');
        if (mainContent) {
            mainContent.classList.add('main-content');
        }
        
        // Soru başlığını sticky header'a taşı
        const soruBaslik = document.querySelector('.soru-baslik-container');
        if (soruBaslik && !document.querySelector('.soru-sticky-header')) {
            const stickyHeader = document.createElement('div');
            stickyHeader.className = 'soru-sticky-header';
            stickyHeader.innerHTML = soruBaslik.innerHTML;
            document.body.prepend(stickyHeader);
        }
    }
    
    // Sayfa yüklendiğinde çalıştır
    window.addEventListener('load', initPage);
    
    // Streamlit render olduğunda çalıştır
    document.addEventListener('streamlit:render', function() {
        setTimeout(initPage, 100);
    });
    
    // Her 100ms'de bir kontrol et (güvence için)
    setInterval(function() {
        if (!document.querySelector('.soru-sticky-header') && document.querySelector('.soru-baslik-container')) {
            initPage();
        }
    }, 100);
</script>
""", unsafe_allow_html=True)

# --- ANA SAYFA ---
st.title("🏛️ SBKY Bölümü Ders Değerlendirme Anketi")

# --- SORU 0: SINIF VE DERS SEÇİMİ ---
if st.session_state.current_step == 0:
    st.markdown("""
    <div class="bilgi-kutusu">
    <h4>📝 Değerli Öğrencimiz,</h4>
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
    
    # STICKY SORU BAŞLIĞI - JavaScript tarafından alınacak
    st.markdown(f'''
    <div class="soru-baslik-container">
        <h3>
            <span class="soru-numara">❓ Soru {s_no + 1}</span>
            <span class="toplam-soru">/ 13</span>
        </h3>
        <div class="soru-metni">{soru_metni}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    # Ölçek açıklaması
    st.markdown("""
    <div style="text-align: center; margin: 15px 0; font-size: 12px; color: #666; background: #f8f9fa; padding: 8px; border-radius: 5px;">
    <strong>Değerlendirme Ölçeği:</strong> 1 = Kesinlikle Katılmıyorum | 5 = Kesinlikle Katılıyorum
    </div>
    """, unsafe_allow_html=True)
    
    current_responses = []
    
    # Dersleri alt alta gösteriyoruz - daha kompakt
    for ders in aktif_dersler:
        # Her ders için bir container
        st.markdown(f'<div class="ders-konteynir">', unsafe_allow_html=True)
        
        # Ders başlığı - daha büyük ve görünür
        st.markdown(f'<div class="ders-baslik">{ders}</div>', unsafe_allow_html=True)
        
        # Slider etiketleri - kompakt iki satırlı
        st.markdown("""
        <div class="slider-etiket-konteynir">
            <div class="slider-etiket-sol">
                <span class="etiket-buyuk">1</span><br>
                <span class="etiket-kucuk">Kesinlikle<br>Katılmıyorum</span>
            </div>
            <div class="slider-etiket-sag">
                <span class="etiket-buyuk">5</span><br>
                <span class="etiket-kucuk">Kesinlikle<br>Katılıyorum</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Puanlama slider'ı (1-5)
        puan = st.slider(
            "",
            min_value=1,
            max_value=5,
            value=3,
            key=f"step_{s_no}_{ders}",
            label_visibility="collapsed"
        )
        
        # Puan göstergesi - daha kompakt
        st.markdown(f"""
        <div style="text-align: center; margin-top: 10px;">
            <div style="font-size: 14px; font-weight: bold; margin-bottom: 5px; color: #1e3a8a;">
                Seçilen Puan: <span style="font-size: 18px; color: #3b82f6;">{puan}</span>
            </div>
            <div style="font-size: 22px; letter-spacing: 3px; margin-top: 5px;">
                {"●" * puan}{"○" * (5 - puan)}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        current_responses.append({
            "Sinif": st.session_state.selected_sinif, 
            "Ders": ders, 
            "Soru_No": s_no + 1, 
            "Puan": puan
        })
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Dersler bittikten sonra boşluk ve buton
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Buton bölümü
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if s_no < 12:  # Soru 1-12 için
            button_label = f"➡️ Sonraki Soru ({s_no + 2}/13)"
        else:  # Son soru için
            button_label = "✅ Tüm Soruları Tamamla"
        
        if st.button(button_label, use_container_width=True, type="primary"):
            st.session_state.all_data.extend(current_responses)
            st.session_state.current_step += 1
            # Scroll için JavaScript - Streamlit'in render olmasını bekle
            st.markdown("""
            <script>
                // Butona basıldığında başa scroll yap
                window.scrollTo(0, 0);
                
                // Yeni sayfa render olduğunda tekrar başa git
                setTimeout(function() {
                    window.scrollTo(0, 0);
                }, 100);
            </script>
            """, unsafe_allow_html=True)
            st.rerun()

# --- GÖNDERME EKRANI ---
else:
    st.success("🎉 **Tebrikler! Tüm soruları tamamladınız.**")
    
    st.markdown("""
    <div class="bilgi-kutusu">
    <h4>📋 Yanıtlarınız Hazır</h4>
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
<div style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
<p><strong>SBKY Bölümü Ders Değerlendirme Anketi</strong></p>
<p>Bu anket, bölümümüzün eğitim kalitesini artırmak ve akreditasyon sürecine katkı sağlamak amacıyla düzenlenmiştir.</p>
</div>
""", unsafe_allow_html=True)