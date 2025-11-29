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
        convert: "Convert to 3D",
        upload_title: "Upload DXF File",
        upload_drag: "Drag and drop your DXF file here, or click to select",
        upload_hint: "Max file size: 50MB. Supported format: .dxf",
        mode_label: "Conversion Mode",
        unit_label: "Unit",
        height_label: "Extrusion Height",
        mode_floor: "Floor Plan (Walls)",
        mode_mech: "Mechanical Part",
        status_pending: "Pending...",
        status_processing: "Processing Geometry...",
        status_completed: "Conversion Complete!",
        status_failed: "Conversion Failed",
        download_btn: "Download 3D Model",
        start_new: "Convert Another File",
        processing_step_1: "Parsing DXF entities...",
        processing_step_2: "Detecting closed loops...",
        processing_step_3: "Generating 3D mesh...",
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
        convert: "3D'ye Dönüştür",
        upload_title: "DXF Dosyası Yükle",
        upload_drag: "DXF dosyanızı buraya sürükleyin veya seçmek için tıklayın",
        upload_hint: "Maks dosya boyutu: 50MB. Desteklenen format: .dxf",
        mode_label: "Dönüştürme Modu",
        unit_label: "Birim",
        height_label: "Ekstrüzyon Yüksekliği",
        mode_floor: "Kat Planı (Duvarlar)",
        mode_mech: "Mekanik Parça",
        status_pending: "Bekleniyor...",
        status_processing: "Geometri İşleniyor...",
        status_completed: "Dönüşüm Tamamlandı!",
        status_failed: "Dönüşüm Başarısız",
        download_btn: "3D Modeli İndir",
        start_new: "Yeni Dosya Dönüştür",
        processing_step_1: "DXF varlıkları ayrıştırılıyor...",
        processing_step_2: "Kapalı döngüler tespit ediliyor...",
        processing_step_3: "3D ağ oluşturuluyor...",
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