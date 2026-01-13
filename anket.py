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
    /* Rengarenk slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #ff4b4b 0%, #ffa726 25%, #ffeb3b 50%, #4caf50 75%, #2e7d32 100%);
        height: 10px;
    }
    
    .stSlider > div > div > div > div > div {
        height: 24px;
        width: 24px;
    }
    
    /* Ders başlıkları */
    .ders-baslik {
        font-size: 20px;
        font-weight: bold;
        color: #1e3a8a;
        margin-top: 10px;
        margin-bottom: 5px;
        padding: 10px;
        background-color: #f0f8ff;
        border-radius: 8px;
        border-left: 4px solid #1e3a8a;
    }
    
    /* Mini soru başlığı - her ders için */
    .mini-soru-baslik {
        font-size: 14px;
        color: #666;
        margin-bottom: 15px;
        padding: 8px;
        background-color: #f8f9fa;
        border-radius: 5px;
        border-left: 3px solid #3b82f6;
        font-style: italic;
    }
    
    /* Soru numarası */
    .soru-numara {
        font-size: 24px;
        font-weight: bold;
        color: #1e3a8a;
        margin-bottom: 5px;
    }
    
    /* Ana soru metni */
    .ana-soru-metni {
        font-size: 18px;
        color: #333;
        margin-bottom: 20px;
        padding: 15px;
        background-color: #e8f4fd;
        border-radius: 10px;
        border-left: 5px solid #1e3a8a;
    }
    
    /* Slider etiketleri */
    .slider-etiket-konteynir {
        display: flex;
        justify-content: space-between;
        margin-top: 5px;
        margin-bottom: 10px;
    }
    
    .slider-etiket-sol, .slider-etiket-sag {
        font-size: 11px;
        line-height: 1.2;
        text-align: center;
    }
    
    .etiket-buyuk {
        font-size: 16px;
        font-weight: bold;
        display: block;
    }
    
    .etiket-kucuk {
        font-size: 10px;
        display: block;
    }
    
    /* Başa Dön butonu */
    .basa-don-btn {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        background-color: #1e3a8a;
        color: white;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .basa-don-btn:hover {
        background-color: #3b82f6;
        transform: scale(1.1);
    }
    
    /* Ders konteynır */
    .ders-konteynir {
        margin-bottom: 15px;
        padding-bottom: 15px;
        border-bottom: 1px solid #e0e0e0;
    }
    
    @media (max-width: 768px) {
        .ders-baslik {
            font-size: 18px;
            padding: 8px;
        }
        
        .mini-soru-baslik {
            font-size: 13px;
        }
        
        .ana-soru-metni {
            font-size: 16px;
            padding: 12px;
        }
        
        .basa-don-btn {
            bottom: 15px;
            right: 15px;
            width: 45px;
            height: 45px;
            font-size: 20px;
        }
    }
</style>
""", unsafe_allow_html=True)

# --- "BAŞA DÖN" BUTONU İÇİN JAVASCRIPT ---
st.markdown("""
<script>
// Başa Dön butonu oluştur
function createScrollToTopButton() {
    if (!document.querySelector('.basa-don-btn')) {
        const button = document.createElement('button');
        button.className = 'basa-don-btn';
        button.innerHTML = '↑';
        button.title = 'Başa Dön';
        button.onclick = function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        };
        document.body.appendChild(button);
        
        // Scroll'a göre butonu göster/gizle
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                button.style.display = 'flex';
            } else {
                button.style.display = 'none';
            }
        });
    }
}

// Sayfa yüklendiğinde butonu oluştur
window.addEventListener('load', createScrollToTopButton);
document.addEventListener('DOMContentLoaded', createScrollToTopButton);

// Streamlit render olduğunda butonu oluştur
document.addEventListener('streamlit:render', function() {
    setTimeout(createScrollToTopButton, 100);
});
</script>
""", unsafe_allow_html=True)

# --- ANA SAYFA ---
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
    
    # Ana soru başlığı - sayfanın başında
    st.markdown(f'<div class="soru-numara">❓ Soru {s_no + 1} / 13</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="ana-soru-metni">{soru_metni}</div>', unsafe_allow_html=True)
    
    # Ölçek açıklaması
    st.markdown("""
    <div style="text-align: center; margin: 15px 0 25px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; border: 1px solid #e0e0e0;">
    <strong style="color: #1e3a8a;">Değerlendirme Ölçeği:</strong> 
    <span style="color: #ff4b4b;">1 = Kesinlikle Katılmıyorum</span> | 
    <span style="color: #2e7d32;">5 = Kesinlikle Katılıyorum</span>
    </div>
    """, unsafe_allow_html=True)
    
    current_responses = []
    
    # Dersleri alt alta gösteriyoruz - HER DERS İÇİN SORUYU TEKRAR GÖSTERİYORUZ
    for idx, ders in enumerate(aktif_dersler):
        # Her ders için bir container
        st.markdown('<div class="ders-konteynir">', unsafe_allow_html=True)
        
        # Ders başlığı
        st.markdown(f'<div class="ders-baslik">{idx+1}. {ders}</div>', unsafe_allow_html=True)
        
        # Mini soru başlığı - bu ders için soruyu hatırlat
        st.markdown(f'<div class="mini-soru-baslik"><strong>Soru:</strong> {soru_metni}</div>', unsafe_allow_html=True)
        
        # Slider etiketleri - kompakt iki satırlı
        st.markdown("""
        <div class="slider-etiket-konteynir">
            <div class="slider-etiket-sol">
                <span class="etiket-buyuk">1</span>
                <span class="etiket-kucuk">Kesinlikle<br>Katılmıyorum</span>
            </div>
            <div class="slider-etiket-sag">
                <span class="etiket-buyuk">5</span>
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
        
        # Puan göstergesi
        st.markdown(f"""
        <div style="text-align: center; margin: 15px 0;">
            <div style="font-size: 16px; font-weight: bold; color: #1e3a8a; margin-bottom: 8px;">
                Seçilen Puan: <span style="font-size: 22px; color: #3b82f6;">{puan}</span>
            </div>
            <div style="font-size: 24px; letter-spacing: 4px; color: #1e3a8a;">
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
    
    # Alt kısımda başa dön butonu (ekstra)
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; margin: 20px 0;">
            <button onclick="window.scrollTo({top: 0, behavior: 'smooth'})" 
                    style="padding: 10px 20px; background-color: #1e3a8a; color: white; 
                           border: none; border-radius: 5px; cursor: pointer;">
                ↑ Başa Dön
            </button>
        </div>
        """, unsafe_allow_html=True)
    
    # Dersler bittikten sonra boşluk
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # İlerleme butonu
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if s_no < 12:  # Soru 1-12 için
            button_label = f"➡️ Sonraki Soru ({s_no + 2}/13)"
        else:  # Son soru için
            button_label = "✅ Tüm Soruları Tamamla"
        
        if st.button(button_label, use_container_width=True, type="primary"):
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
<div style="text-align: center; color: #666; font-size: 14px; margin-top: 30px;">
<p><strong>SBKY Bölümü Ders Değerlendirme Anketi</strong></p>
<p>Bu anket, bölümümüzün eğitim kalitesini artırmak ve akreditasyon sürecine katkı sağlamak amacıyla düzenlenmiştir.</p>
</div>
""", unsafe_allow_html=True)