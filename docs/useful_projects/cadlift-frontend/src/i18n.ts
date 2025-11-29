
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      common: {
        title: "CADLift",
        home: "Home",
        about: "About",
        theme_dark: "Dark Mode",
        theme_light: "Light Mode",
        footer_text: "© 2024 CADLift. All rights reserved.",
        convert: "Start Conversion",
        upload_title: "Upload File",
        upload_drag: "Drag and drop file here, or click to select",
        upload_hint_dxf: "Max size: 50MB. Format: .dxf",
        upload_hint_img: "Max size: 20MB. Formats: .jpg, .png",
        mode_label: "Conversion Mode",
        unit_label: "Unit",
        height_label: "Extrusion Height",
        mode_floor: "Floor Plan (Walls)",
        mode_mech: "Mechanical Part",
        status_pending: "Pending...",
        status_processing: "Processing...",
        status_completed: "Complete!",
        status_failed: "Failed",
        status_cancelled: "Cancelled",
        download_btn: "Download Model",
        start_new: "Start New Job",
        processing_step_1: "Analyzing input...",
        processing_step_2: "Generating geometry...",
        processing_step_3: "Finalizing mesh...",
      },
      dashboard: {
        workspace: "Workspace",
        ready: "Select a workflow to begin",
        logout: "Log Out",
        active_conversions: "Active Conversions",
        recent_activity: "Recent Jobs / History",
        presets_title: "Presets & Templates",
        settings_title: "Quick Settings",
        
        view_details: "View Details",
        cancel_job: "Cancel Job",
        cancel_success: "Job cancelled successfully",
        cancel_error: "Failed to cancel job",
        
        search_placeholder: "Search by filename...",
        filter_all_status: "All Status",
        filter_completed: "Completed",
        filter_failed: "Failed",
        filter_cancelled: "Cancelled",
        filter_all_types: "All Types",
        filter_date_from: "From",
        filter_date_to: "To",
        clear_filters: "Clear Filters",
        
        table_job: "Job Name",
        table_type: "Type",
        table_output: "Output",
        table_status: "Status",
        table_date: "Created",
        table_action: "Actions",
        empty_state: "No recent conversions found.",
        empty_active: "No active conversions running.",
        empty_presets: "No presets saved yet.",
        
        action_download: "Download",
        action_retry: "Re-run",
        action_duplicate: "Duplicate",
        
        run_preset: "Apply Preset",
        save_preset: "Create Preset",
        delete_preset: "Delete",
        preset_name_placeholder: "Preset Name (e.g., Standard Walls)",
        create_preset_success: "Preset created!",
        delete_preset_success: "Preset deleted.",
        
        default_unit: "Default Unit",
        default_mode: "Default Mode",
        default_height: "Default Height",
        ui_language: "Language",
        ui_theme: "Theme",
        
        quick_links: "Resources",
        link_docs: "Docs",
        link_help: "Help",

        // Phase 2 New Keys
        tab_cad: "AutoCAD 2D",
        tab_image: "Image / Sketch",
        tab_prompt: "AI Prompt",
        
        prompt_label: "Description",
        prompt_placeholder: "Describe the object you want to generate (e.g. 'A hexagonal mechanical gear with 12 teeth')...",
        
        target_label: "Target Output",
        target_2d: "2D Vector (DXF)",
        target_3d: "3D Model (OBJ/FBX)",
        
        desc_cad: "Convert DXF drawings into 3D solids",
        desc_image: "Turn sketches or photos into CAD data",
        desc_prompt: "Generate 3D models from text descriptions"
      },
      about: {
        heading: "About CADLift",
        description: "CADLift transforms your 2D technical drawings into 3D models instantly. Using advanced geometry processing, we bridge the gap between drafting and modeling.",
        features_title: "Key Features",
        feature_1: "Instant DXF to 3D conversion",
        feature_2: "Intelligent closed-loop detection",
        feature_3: "Export to FBX/OBJ for AutoCAD & Blender",
        disclaimer: "This is a demo MVP version."
      }
    }
  },
  tr: {
    translation: {
      common: {
        title: "CADLift",
        home: "Anasayfa",
        about: "Hakkında",
        theme_dark: "Karanlık Mod",
        theme_light: "Aydınlık Mod",
        footer_text: "© 2024 CADLift. Tüm hakları saklıdır.",
        convert: "Dönüşümü Başlat",
        upload_title: "Dosya Yükle",
        upload_drag: "Dosyayı buraya sürükleyin veya seçin",
        upload_hint_dxf: "Maks: 50MB. Format: .dxf",
        upload_hint_img: "Maks: 20MB. Formatlar: .jpg, .png",
        mode_label: "Dönüştürme Modu",
        unit_label: "Birim",
        height_label: "Ekstrüzyon Yüksekliği",
        mode_floor: "Kat Planı (Duvarlar)",
        mode_mech: "Mekanik Parça",
        status_pending: "Bekleniyor...",
        status_processing: "İşleniyor...",
        status_completed: "Tamamlandı!",
        status_failed: "Başarısız",
        status_cancelled: "İptal",
        download_btn: "Modeli İndir",
        start_new: "Yeni İş Başlat",
        processing_step_1: "Girdi analiz ediliyor...",
        processing_step_2: "Geometri oluşturuluyor...",
        processing_step_3: "Mesh tamamlanıyor...",
      },
      dashboard: {
        workspace: "Çalışma Alanı",
        ready: "Başlamak için bir iş akışı seçin",
        logout: "Çıkış Yap",
        active_conversions: "Aktif Dönüşümler",
        recent_activity: "Son İşler / Geçmiş",
        presets_title: "Şablonlar",
        settings_title: "Hızlı Ayarlar",
        
        view_details: "Detaylar",
        cancel_job: "İptal",
        cancel_success: "İş başarıyla iptal edildi",
        cancel_error: "İş iptal edilemedi",
        
        search_placeholder: "Dosya adı ile ara...",
        filter_all_status: "Tüm Durumlar",
        filter_completed: "Tamamlandı",
        filter_failed: "Başarısız",
        filter_cancelled: "İptal Edildi",
        filter_all_types: "Tüm Türler",
        filter_date_from: "Başlangıç",
        filter_date_to: "Bitiş",
        clear_filters: "Filtreleri Temizle",
        
        table_job: "İş Adı",
        table_type: "Tür",
        table_output: "Çıktı",
        table_status: "Durum",
        table_date: "Tarih",
        table_action: "İşlemler",
        empty_state: "Geçmiş dönüşüm bulunamadı.",
        empty_active: "Çalışan dönüşüm yok.",
        empty_presets: "Henüz şablon kaydedilmedi.",
        
        action_download: "İndir",
        action_retry: "Tekrarla",
        action_duplicate: "Kopyala",
        
        run_preset: "Uygula",
        save_preset: "Şablon Oluştur",
        delete_preset: "Sil",
        preset_name_placeholder: "Şablon Adı (örn. Standart Duvar)",
        create_preset_success: "Şablon oluşturuldu!",
        delete_preset_success: "Şablon silindi.",
        
        default_unit: "Varsayılan Birim",
        default_mode: "Varsayılan Mod",
        default_height: "Varsayılan Yükseklik",
        ui_language: "Dil",
        ui_theme: "Tema",
        
        quick_links: "Kaynaklar",
        link_docs: "Belgeler",
        link_help: "Yardım",

        tab_cad: "AutoCAD 2D",
        tab_image: "Resim / Eskiz",
        tab_prompt: "Yapay Zeka",
        
        prompt_label: "Açıklama",
        prompt_placeholder: "Oluşturmak istediğiniz nesneyi tanımlayın...",
        
        target_label: "Hedef Çıktı",
        target_2d: "2D Vektör (DXF)",
        target_3d: "3D Model (OBJ/FBX)",

        desc_cad: "DXF çizimlerini 3D katılara dönüştür",
        desc_image: "Eskizleri veya fotoğrafları CAD verisine çevir",
        desc_prompt: "Metin açıklamalarından 3D modeller üret"
      },
      about: {
        heading: "CADLift Hakkında",
        description: "CADLift, 2D teknik çizimlerinizi anında 3D modellere dönüştürür. Gelişmiş geometri işleme teknolojisi kullanarak çizim ve modelleme arasındaki boşluğu dolduruyoruz.",
        features_title: "Temel Özellikler",
        feature_1: "Anında DXF'den 3D'ye dönüşüm",
        feature_2: "Akıllı kapalı döngü algılama",
        feature_3: "AutoCAD & Blender için FBX/OBJ çıktısı",
        disclaimer: "Bu bir demo MVP sürümüdür."
      }
    }
  }
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: "en", 
    fallbackLng: "en",
    interpolation: {
      escapeValue: false 
    }
  });

export default i18n;
