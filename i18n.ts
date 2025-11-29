import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const LANGUAGE_STORAGE_KEY = 'cadlift_language';

const getInitialLanguage = () => {
  if (typeof window === 'undefined') {
    return 'en';
  }
  try {
    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (stored === 'en' || stored === 'tr') {
      return stored;
    }
    return window.navigator.language?.toLowerCase().startsWith('tr') ? 'tr' : 'en';
  } catch {
    return 'en';
  }
};

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
        status_queued: "Queued",
        download_btn: "Download 3D Model",
        start_new: "Convert Another File",
        processing_step_1: "Parsing DXF entities...",
        processing_step_2: "Detecting closed loops...",
        processing_step_3: "Generating 3D mesh...",
      },
      navigation: {
        dashboard: "Dashboard",
        projects: "My Projects",
        docs: "Documentation",
        about: "About"
      },
      dashboard: {
        hero: {
          title: "Transform Your 2D Ideas into 3D Reality",
          subtitle: "Upload a drawing, an image, or simply describe it — CADLift infers closed regions and exports clean solids.",
          primaryCta: "Start a New Conversion",
          secondaryCta: "Learn How It Works",
          statUploads: "Files Converted",
          statTime: "Avg. Turnaround",
          statAccuracy: "Closed Loops Detected"
        },
        modes: {
          title: "Conversion Modes",
          subtitle: "Pick the workflow that matches your input. Every mode inherits your language and theme preferences.",
          cad: {
            title: "AutoCAD 2D → 3D Conversion",
            description: "Upload DXF/DWG drawings and automatically extrude clean architectural or mechanical solids.",
            badge: "DXF / DWG",
            cta: "Upload CAD File"
          },
          image: {
            title: "Image to 2D/3D Generator",
            description: "Turn sketches, floor plans, or product shots into CAD-ready references.",
            optionsLabel: "Available Outputs",
            option2d: "Vector 2D plan",
            option3d: "Watertight 3D mesh",
            cta: "Upload Image"
          },
          prompt: {
            title: "Text Prompt to 2D/3D",
            description: "Describe what you need and let CADLift draft the geometry automatically.",
            examplesLabel: "Prompt Ideas",
            exampleOne: "Draw a 3x4m room with a south-facing window.",
            exampleTwo: "Generate a lightweight L-bracket with two M6 holes.",
            cta: "Start Prompt Generation"
          },
          comingSoon: "Coming Soon",
          betaLabel: "Beta"
        },
        recent: {
          title: "Recent Activity",
          subtitle: "Monitor past runs, download solids, or retry failed jobs.",
          empty: "No jobs yet. Start a conversion to populate this timeline.",
          table: {
            type: "Job Type",
            input: "Input",
            output: "Output",
            status: "Status",
            created: "Created",
            actions: "Actions"
          },
          action: {
            view: "View",
            download: "Download",
            retry: "Retry"
          },
          time_two_hours: "2 hours ago",
          time_ten_minutes: "10 minutes ago",
          time_yesterday: "Yesterday",
          time_just_now: "Just now"
        },
        quickLinks: {
          title: "Resources",
          subtitle: "Guides, documentation, and support to keep you moving.",
          documentation: {
            title: "Documentation",
            description: "REST endpoints, webhooks, and payload schemas."
          },
          tutorials: {
            title: "Tutorial Videos",
            description: "Watch end-to-end walkthroughs in both EN and TR."
          },
          faq: {
            title: "FAQ",
            description: "Limits, supported formats, and troubleshooting."
          },
          support: {
            title: "Community & Support",
            description: "Join the forum or open a support ticket."
          }
        },
        workspace: {
          title: "Conversion Workspace",
          subtitle: "Upload a DXF, set extrusion parameters, and track progress in real time.",
          statusReady: "System ready. Waiting for input..."
        },
        quickStart: {
          title: "Quick Start",
          description: "Launch a workflow in one tap or use keyboard shortcuts.",
          actions: {
            uploadCad: "Upload CAD",
            uploadImage: "Upload Image",
            startPrompt: "Start Prompt"
          }
        },
        tips: {
          title: "Onboarding Tips",
          upload: "Upload a CAD file to begin the classic 2D → 3D extrusion.",
          prompt: "Try the prompt generator for text-first explorations.",
          dismiss: "Got it"
        },
        imageForm: {
          title: "Image to CAD Workflow",
          description: "Turn sketches, scans, or product photos into vector plans or meshes.",
          uploadLabel: "Drop an image or click to browse",
          uploadHint: "Supported: PNG, JPG, SVG up to 25MB",
          pickButton: "Choose Image",
          option2d: {
            title: "Vector 2D Output",
            desc: "Generate clean DXF curves and layers."
          },
          option3d: {
            title: "3D Mesh Output",
            desc: "Reconstruct watertight meshes ready for CAD apps."
          },
          notesLabel: "Notes",
          notesPlaceholder: "Tell us about scale, unit assumptions, or desired detail.",
          submit: "Generate from Image",
          submitLoading: "Processing image...",
          errors: {
            unsupported: "Unsupported file type. Please use PNG/JPG/SVG.",
            tooLarge: "Image exceeds 25MB limit.",
            required: "Please attach an image to continue."
          }
        },
        promptForm: {
          title: "Prompt to Geometry",
          description: "Describe the space or part. CADLift drafts loops and solids.",
          promptLabel: "What should we draw?",
          placeholder: "e.g. Cylindrical adapter with 50mm diameter and two bolt patterns...",
          option2d: {
            title: "2D Draft",
            desc: "Outputs DXF lines and arcs suitable for review."
          },
          option3d: {
            title: "3D Concept",
            desc: "Outputs lightweight STEP meshes."
          },
          detailLabel: "Detail Level",
          detailLow: "Loose",
          detailHigh: "Precise",
          submit: "Generate Prompt",
          submitLoading: "Synthesizing...",
          errors: {
            required: "Please describe what you need."
          }
        }
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
        status_queued: "Sırada",
        download_btn: "3D Modeli İndir",
        start_new: "Yeni Dosya Dönüştür",
        processing_step_1: "DXF varlıkları ayrıştırılıyor...",
        processing_step_2: "Kapalı döngüler tespit ediliyor...",
        processing_step_3: "3D ağ oluşturuluyor...",
      },
      navigation: {
        dashboard: "Panel",
        projects: "Projelerim",
        docs: "Dokümantasyon",
        about: "Hakkında"
      },
      dashboard: {
        hero: {
          title: "2D fikirlerinizi 3D gerçekliğe dönüştürün",
          subtitle: "Çizimi yükleyin, bir görüntü gönderin ya da sadece anlatın — CADLift kapalı bölgeleri bulur ve temiz katılar oluşturur.",
          primaryCta: "Yeni Dönüşüm Başlat",
          secondaryCta: "Nasıl Çalıştığını Gör",
          statUploads: "Tamamlanan dosya",
          statTime: "Ort. süre",
          statAccuracy: "Algılanan döngü"
        },
        modes: {
          title: "Dönüşüm Modları",
          subtitle: "Girdinize uygun iş akışını seçin. Dil ve tema tercihleriniz her moda otomatik aktarılır.",
          cad: {
            title: "AutoCAD 2D → 3D Dönüşüm",
            description: "DXF/DWG çizimlerini yükleyin, duvar ve parçalar otomatik olarak ekstrüde edilsin.",
            badge: "DXF / DWG",
            cta: "CAD Dosyası Yükle"
          },
          image: {
            title: "Görüntüden 2D/3D Üretimi",
            description: "Eskizleri, kat planlarını veya ürün fotoğraflarını CAD'e hazır referanslara çevirin.",
            optionsLabel: "Uygun Çıktılar",
            option2d: "Vektör 2D plan",
            option3d: "Sızdırmaz 3D mesh",
            cta: "Görüntü Yükle"
          },
          prompt: {
            title: "Metinden 2D/3D Üretimi",
            description: "İhtiyacınızı tarif edin, CADLift geometrileri otomatik çizsin.",
            examplesLabel: "Örnek İstekler",
            exampleOne: "Güney cepheli penceresi olan 3x4m bir oda çiz.",
            exampleTwo: "İki adet M6 delikli hafif bir L-braket üret.",
            cta: "İstekle Başlat"
          },
          comingSoon: "Çok Yakında",
          betaLabel: "Beta"
        },
        recent: {
          title: "Son Aktiviteler",
          subtitle: "Önceki işleri takip edin, çıktıları indirin veya yeniden deneyin.",
          empty: "Henüz bir iş yok. Bu zaman çizelgesini doldurmak için dönüştürme başlatın.",
          table: {
            type: "İş Tipi",
            input: "Girdi",
            output: "Çıktı",
            status: "Durum",
            created: "Oluşturulma",
            actions: "İşlemler"
          },
          action: {
            view: "Görüntüle",
            download: "İndir",
            retry: "Tekrarla"
          },
          time_two_hours: "2 saat önce",
          time_ten_minutes: "10 dakika önce",
          time_yesterday: "Dün",
          time_just_now: "Az önce"
        },
        quickLinks: {
          title: "Kaynaklar",
          subtitle: "Rehberler, dökümantasyon ve destek bağlantıları.",
          documentation: {
            title: "Dokümantasyon",
            description: "REST uç noktaları, webhooklar ve veri şemaları."
          },
          tutorials: {
            title: "Eğitim Videoları",
            description: "EN ve TR rehberli baştan sona anlatımlar."
          },
          faq: {
            title: "SSS",
            description: "Limitler, desteklenen formatlar ve sorun giderme."
          },
          support: {
            title: "Topluluk & Destek",
            description: "Foruma katılın veya destek talebi açın."
          }
        },
        workspace: {
          title: "Dönüşüm Çalışma Alanı",
          subtitle: "DXF yükleyin, ekstrüzyon parametrelerini belirleyin ve ilerlemeyi anlık takip edin.",
          statusReady: "Sistem hazır. Girdi bekleniyor..."
        },
        quickStart: {
          title: "Hızlı Başlangıç",
          description: "Bir tıkla iş akışı başlatın veya kısayolları kullanın.",
          actions: {
            uploadCad: "CAD Yükle",
            uploadImage: "Görüntü Yükle",
            startPrompt: "İstek Başlat"
          }
        },
        tips: {
          title: "Başlangıç İpuçları",
          upload: "Klasik 2D → 3D ekstrüzyon için CAD dosyası yükleyin.",
          prompt: "Metin tabanlı keşifler için prompt üreticisini deneyin.",
          dismiss: "Anladım"
        },
        imageForm: {
          title: "Görüntüden CAD'e",
          description: "Eskizleri, taramaları veya ürün fotoğraflarını vektör planlara ya da mesh'lere çevirin.",
          uploadLabel: "Görüntüyü bırakın veya göz atın",
          uploadHint: "Desteklenen formatlar: PNG, JPG, SVG (25MB'a kadar)",
          pickButton: "Görüntü Seç",
          option2d: {
            title: "Vektör 2D Çıktı",
            desc: "Temiz DXF eğrileri ve katmanları oluşturur."
          },
          option3d: {
            title: "3D Mesh Çıktı",
            desc: "CAD yazılımlarına hazır sızdırmaz mesh oluşturur."
          },
          notesLabel: "Notlar",
          notesPlaceholder: "Ölçek, birim veya beklenen detay hakkında bilgi verin.",
          submit: "Görüntüden Üret",
          submitLoading: "Görüntü işleniyor...",
          errors: {
            unsupported: "Desteklenmeyen dosya türü. Lütfen PNG/JPG/SVG kullanın.",
            tooLarge: "Görüntü 25MB limitini aşıyor.",
            required: "Devam etmek için bir görüntü ekleyin."
          }
        },
        promptForm: {
          title: "Prompt'tan Geometri",
          description: "Mekânı veya parçayı tarif edin. CADLift döngüleri ve katıları çizer.",
          promptLabel: "Ne çizelim?",
          placeholder: "Örn. 50mm çaplı silindirik adaptör ve iki cıvata paternli...",
          option2d: {
            title: "2D Taslak",
            desc: "Gözden geçirme için DXF çizgiler ve yaylar üretir."
          },
          option3d: {
            title: "3D Konsept",
            desc: "Hafif STEP mesh çıktısı verir."
          },
          detailLabel: "Detay Seviyesi",
          detailLow: "Kabaca",
          detailHigh: "Hassas",
          submit: "Prompt Oluştur",
          submitLoading: "Oluşturuluyor...",
          errors: {
            required: "Lütfen ihtiyacınızı tarif edin."
          }
        }
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

const initialLanguage = getInitialLanguage();

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: initialLanguage,
    fallbackLng: "en",
    interpolation: {
      escapeValue: false 
    }
  });

if (typeof window !== 'undefined') {
  i18n.on('languageChanged', (lng) => {
    try {
      window.localStorage.setItem(LANGUAGE_STORAGE_KEY, lng);
    } catch {
      // ignore storage errors
    }
  });
}

export default i18n;
