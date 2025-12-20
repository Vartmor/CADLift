import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const LANGUAGE_STORAGE_KEY = 'cadlift_language';

const getInitialLanguage = () => {
  if (typeof window === 'undefined') {
    return 'en';
  }
  try {
    const stored = window.localStorage.getItem(LANGUAGE_STORAGE_KEY);
    if (stored === 'en' || stored === 'tr' || stored === 'de') {
      return stored;
    }
    const browserLang = window.navigator.language?.toLowerCase();
    if (browserLang?.startsWith('tr')) return 'tr';
    if (browserLang?.startsWith('de')) return 'de';
    return 'en';
  } catch {
    return 'en';
  }
};

const resources = {
  en: {
    translation: {
      common: {
        title: 'CADLift',
        home: 'Home',
        about: 'About',
        theme_dark: 'Dark Mode',
        theme_light: 'Light Mode',
        footer_text: '(c) 2024 CADLift. All rights reserved.',
        footer_made: 'Made with love by',
        footer_docs: 'Docs',
        footer_support: 'Support',
        footer_github: 'GitHub',
        convert: 'Convert to 3D',
        upload_title: 'Upload DXF File',
        upload_drag: 'Drag and drop your DXF file here, or click to select',
        upload_hint: 'Max file size: 50MB. Supported format: .dxf',
        mode_label: 'Conversion Mode',
        unit_label: 'Unit',
        height_label: 'Extrusion Height',
        mode_floor: 'Floor Plan (Walls)',
        mode_mech: 'Mechanical Part',
        status_pending: 'Pending...',
        status_processing: 'Processing Geometry...',
        status_completed: 'Conversion Complete!',
        status_failed: 'Conversion Failed',
        status_queued: 'Queued',
        status_cancelled: 'Cancelled',
        download_btn: 'Download 3D Model',
        start_new: 'Convert Another File',
        processing_step_1: 'Parsing DXF entities...',
        processing_step_2: 'Detecting closed loops...',
        processing_step_3: 'Generating 3D mesh...'
      },
      navigation: {
        dashboard: 'Dashboard',
        dashboard_btn: 'Go to Dashboard',
        docs: 'Documentation',
        about: 'About'
      },
      home: {
        hero: {
          badge: 'Free & Open Source',
          title1: 'Turn',
          title2: 'Anything',
          title3: 'Into',
          title4: '3D',
          subtitle: 'From',
          subtitleCad: 'CAD files',
          subtitleTo: 'to',
          subtitleImages: 'images',
          subtitlePrompts: 'text prompts',
          subtitleEnd: '— generate production-ready 3D models locally.',
          primaryCta: 'Open Dashboard',
          secondaryCta: 'View on GitHub',
          inputTypes: {
            dwg: 'DWG / DXF',
            images: 'Images',
            prompts: 'AI Prompts'
          }
        },
        features: {
          badge: 'Powerful Features',
          title: 'Three Ways to',
          titleAccent: 'Create',
          subtitle: 'Choose your input method. Everything runs locally on your machine.',
          cad: {
            title: 'DWG/DXF to 3D',
            description: 'Upload AutoCAD files directly. Layer detection and extrusion happens instantly on your device.',
            features: ['Native DWG support', 'Privacy focused', 'Auto layer detection', 'Closed shape extrusion']
          },
          image: {
            title: 'Image to 3D',
            description: 'Transform any image into a detailed 3D model using local AI models.'
          },
          prompt: {
            title: 'Prompt to 3D',
            description: 'Just describe it. AI generates an image and builds your user model entirely offline.'
          },
          viewer: {
            title: '3D Viewer',
            description: 'Preview before export'
          },
          export: {
            title: 'Multi-Format',
            description: 'GLB, STL, DXF, STEP'
          }
        },
        howItWorks: {
          title: 'How It',
          titleAccent: 'Works',
          subtitle: 'Three simple steps to 3D',
          steps: [
            { title: 'Download App', description: 'Get the desktop app from GitHub to start' },
            { title: 'Load Input', description: 'Drop your CAD file, image, or type a prompt' },
            { title: 'Local AI Processing', description: 'Your GPU generates the 3D model instantly' }
          ]
        },
        cta: {
          badge: '100% Free & Open Source',
          title: 'Ready to',
          titleAccent: 'Contribute',
          subtitle: 'Join our community on GitHub. Star the repo, fork the code, or download the latest release to get started.',
          button: 'Get Desktop App'
        }
      },
      resourcesPage: {
        heading: 'Resources',
        subheading: 'Guides, documentation, and support to keep you moving.',
        cards: {
          docs: { title: 'Documentation', desc: 'REST endpoints, webhooks, and payload schemas.' },
          videos: { title: 'Tutorial Videos', desc: 'Watch end-to-end walkthroughs in both EN and TR.' },
          faq: { title: 'FAQ', desc: 'Limits, supported formats, and troubleshooting.' },
          community: { title: 'Community & Support', desc: 'Join the forum or open a support ticket.' }
        }
      },
      dashboard: {
        hero: {
          greeting: 'Welcome back',
          newUser: 'Welcome to CADLift',
          tagline: 'Your 3D Creation Studio',
          quickAction: 'Quick Action',
          createNew: 'Create New',
          viewProjects: 'View Projects',
          stats: {
            conversions: 'Conversions',
            thisWeek: 'This Week',
            successRate: 'Success Rate',
            avgTime: 'Avg. Time'
          },
          emptyState: {
            title: 'Ready to create?',
            subtitle: 'Choose a workflow below to start your first 3D model'
          },
          signedInAs: 'Signed in as',
          signOut: 'Sign Out'
        },
        modes: {
          title: 'Conversion Modes',
          subtitle:
            'Pick the workflow that matches your input. Every mode inherits your language and theme preferences.',
          cad: {
            title: 'AutoCAD 2D → 3D Conversion',
            description: 'Upload DXF/DWG drawings and automatically extrude clean architectural or mechanical solids.',
            badge: 'DXF / DWG',
            cta: 'Upload CAD File'
          },
          image: {
            title: 'Image to 2D/3D Generator',
            description: 'Turn sketches, floor plans, or product shots into CAD-ready references.',
            optionsLabel: 'Available Outputs',
            option2d: 'Vector 2D plan',
            option3d: 'Watertight 3D mesh',
            cta: 'Upload Image'
          },
          prompt: {
            title: 'Text Prompt to 2D/3D',
            description: 'Describe what you need and let CADLift draft the geometry automatically.',
            examplesLabel: 'Prompt Ideas',
            exampleOne: 'Draw a 3x4m room with a south-facing window.',
            exampleTwo: 'Generate a lightweight L-bracket with two M6 holes.',
            cta: 'Start Prompt Generation'
          },
          comingSoon: 'Coming Soon',
          betaLabel: 'Beta'
        },
        recent: {
          title: 'Recent Activity',
          subtitle: 'Monitor past runs, download solids, or retry failed jobs.',
          empty: 'No jobs yet. Start a conversion to populate this timeline.',
          table: {
            type: 'Job Type',
            input: 'Input',
            output: 'Output',
            status: 'Status',
            created: 'Created',
            actions: 'Actions'
          },
          action: {
            view: 'View',
            download: 'Download',
            retry: 'Retry'
          },
          time_two_hours: '2 hours ago',
          time_ten_minutes: '10 minutes ago',
          time_yesterday: 'Yesterday',
          time_just_now: 'Just now'
        },
        quickLinks: {
          title: 'Resources',
          subtitle: 'Guides, documentation, and support to keep you moving.',
          documentation: {
            title: 'Documentation',
            description: 'REST endpoints, webhooks, and payload schemas.'
          },
          tutorials: {
            title: 'Tutorial Videos',
            description: 'Watch end-to-end walkthroughs in both EN and TR.'
          },
          faq: {
            title: 'FAQ',
            description: 'Limits, supported formats, and troubleshooting.'
          },
          support: {
            title: 'Community & Support',
            description: 'Join the forum or open a support ticket.'
          }
        },
        workspace: {
          title: 'Conversion Workspace',
          subtitle: 'Upload a DXF, set extrusion parameters, and track progress in real time.',
          statusReady: 'System ready. Waiting for input...'
        },
        quickStart: {
          title: 'Quick Start',
          description: 'Launch a workflow in one tap or use keyboard shortcuts.',
          actions: {
            uploadCad: 'Upload CAD',
            uploadImage: 'Upload Image',
            startPrompt: 'Start Prompt'
          }
        },
        tips: {
          title: 'Onboarding Tips',
          upload: 'Upload a CAD file to begin the classic 2D → 3D extrusion.',
          prompt: 'Try the prompt generator for text-first explorations.',
          dismiss: 'Got it'
        },
        imageForm: {
          title: 'Image to CAD Workflow',
          description: 'Turn sketches, scans, or product photos into vector plans or meshes.',
          uploadLabel: 'Drop an image or click to browse',
          uploadHint: 'Supported: PNG, JPG, SVG up to 25MB',
          pickButton: 'Choose Image',
          option2d: {
            title: 'Vector 2D Output',
            desc: 'Generate clean DXF curves and layers.'
          },
          option3d: {
            title: '3D Mesh Output',
            desc: 'Reconstruct watertight meshes ready for CAD apps.'
          },
          notesLabel: 'Notes',
          notesPlaceholder: 'Tell us about scale, unit assumptions, or desired detail.',
          submit: 'Generate from Image',
          submitLoading: 'Processing image...',
          errors: {
            unsupported: 'Unsupported file type. Please use PNG/JPG/SVG.',
            tooLarge: 'Image exceeds 25MB limit.',
            required: 'Please attach an image to continue.'
          }
        },
        promptForm: {
          title: 'Prompt to Geometry',
          description: 'Describe the space or part. CADLift drafts loops and solids.',
          promptLabel: 'What should we draw?',
          placeholder: 'e.g. Cylindrical adapter with 50mm diameter and two bolt patterns...',
          option2d: {
            title: '2D Draft',
            desc: 'Outputs DXF lines and arcs suitable for review.'
          },
          option3d: {
            title: '3D Concept',
            desc: 'Outputs lightweight STEP meshes.'
          },
          detailLabel: 'Detail Level',
          detailLow: 'Loose',
          detailHigh: 'Precise',
          submit: 'Generate Object',
          submitLoading: 'Generating...',
          errors: {
            required: 'Please describe what you need.'
          }
        }
      },
      aboutLegacy: {
        heading: 'About CADLift',
        description:
          'CADLift transforms your 2D technical drawings into 3D models instantly. Using advanced geometry processing, we bridge the gap between drafting and modeling.',
        features_title: 'Key Features',
        feature_1: 'Instant DWG/DXF to 3D conversion',
        feature_2: 'Intelligent closed-loop detection',
        feature_3: 'Export to FBX/OBJ for AutoCAD & Blender',
        disclaimer: 'This is a demo MVP version.'
      },
      auth: {
        signIn: {
          title: 'Welcome Back',
          subtitle: 'Enter your credentials to access the workspace',
          emailLabel: 'Email Address',
          emailPlaceholder: 'engineer@cadlift.io',
          passwordLabel: 'Password',
          forgot: 'Forgot?',
          submit: 'Sign In',
          submitting: 'Signing in...',
          or: 'Or',
          googleSignIn: 'Continue with Google',
          noAccount: 'New to CADLift?',
          createAccount: 'Create an account',
          failed: 'Sign in failed'
        },
        signUp: {
          title: 'Create Account',
          subtitle: 'Start your 3D journey today',
          nameLabel: 'Full Name',
          namePlaceholder: 'John Doe',
          emailLabel: 'Email Address',
          emailPlaceholder: 'engineer@cadlift.io',
          passwordLabel: 'Password',
          passwordHint: 'Minimum 8 characters',
          submit: 'Get Started',
          submitting: 'Creating account...',
          or: 'Or',
          googleSignUp: 'Sign up with Google',
          hasAccount: 'Already have an account?',
          signIn: 'Sign in',
          failed: 'Registration failed'
        },
        signOut: 'Sign Out'
      },
      profile: {
        title: 'Profile',
        memberSince: 'Member since',
        appVersion: 'App Version',
        localConversions: 'Local Conversions',
        openSource: 'Open Source',
        settings: {
          title: 'Settings',
          appearance: 'Appearance',
          language: 'Language',
          account: 'Account',
          security: 'Security',
          dangerZone: 'Danger Zone',
          system: 'System Resources',
          models: 'AI Models'
        },
        system: {
          title: 'System Resources',
          gpu: 'Detected GPU',
          vram: 'VRAM Allocation',
          vramLimit: 'Max VRAM Limit',
          cpuFallback: 'CPU Fallback',
          lowVram: 'Low VRAM Mode',
          autoDetect: 'Auto-detect Hardware'
        },
        models: {
          title: 'AI Model Management',
          path: 'Models Storage Path',
          autoUpdate: 'Auto-Update Models',
          purge: 'Purge Cache',
          verify: 'Verify Integrity',
          status: 'Status',
          ready: 'Ready',
          missing: 'Missing',
          downloading: 'Downloading...'
        },
        theme: {
          light: 'Light',
          dark: 'Dark'
        },
        actions: {
          editProfile: 'Edit Profile',
          changePassword: 'Change Password',
          twoFactor: 'Two-Factor Auth',
          activeSessions: 'Active Sessions',
          loginHistory: 'Login History',
          deleteData: 'Delete All Data',
          deleteAccount: 'Delete Account'
        },
        modals: {
          editProfile: {
            title: 'Edit Profile',
            displayName: 'Display Name',
            save: 'Save Changes',
            saving: 'Saving...',
            success: 'Profile updated successfully!',
            error: 'Failed to update profile'
          },
          changePassword: {
            title: 'Change Password',
            current: 'Current Password',
            new: 'New Password',
            confirm: 'Confirm Password',
            hint: 'Use at least 8 characters with mixed case and numbers',
            save: 'Update Password',
            saving: 'Updating...',
            success: 'Password changed successfully!',
            mismatch: 'Passwords do not match',
            error: 'Failed to change password'
          },
          sessions: {
            title: 'Active Sessions',
            current: 'Current Session',
            device: 'Device',
            browser: 'Browser',
            location: 'Location',
            lastActive: 'Last Active',
            revokeAll: 'Revoke All Other Sessions'
          },
          loginHistory: {
            title: 'Login History',
            recentLogins: 'Recent Logins',
            success: 'Success',
            failed: 'Failed'
          },
          deleteConfirm: {
            title: 'Are you sure?',
            warning: 'This action cannot be undone. This will permanently delete your data.',
            cancel: 'Cancel',
            confirm: 'Yes, Delete'
          },
          comingSoon: 'Coming Soon',
          twoFactorMessage: 'Two-factor authentication will be available in a future update.'
        }
      },
      footer: {
        brand: {
          description: 'Transform your 2D designs into stunning 3D models instantly. Powered by advanced geometry processing and AI.'
        },
        sections: {
          product: 'Product',
          resources: 'Resources',
          company: 'Company'
        },
        links: {
          dashboard: 'Dashboard',
          dwgTo3d: 'DWG/DXF to 3D',
          imageTo3d: 'Image to 3D',
          promptTo3d: 'Prompt to 3D',
          apiDocs: 'API Docs',
          resources: 'Resources',
          faq: 'FAQ',
          community: 'Community',
          about: 'About',
          github: 'GitHub',
          contact: 'Contact'
        },
        copyright: 'All rights reserved.',
        madeWith: 'Made with',
        by: 'by'
      },
      viewer: {
        title: '3D Model Viewer',
        download: 'Download',
        screenshot: 'Screenshot',
        screenshotSoon: 'Screenshot feature coming soon!',
        supportedFormats: 'Supported Formats',
        poweredBy: 'Powered by'
      },
      about: {
        badge: 'Free & Open Source Software',
        hero: {
          title1: 'The',
          titleHighlight: 'Open Source',
          title2: '3D Engine',
          subtitle: 'CADLift is a 100% free and open-source platform that runs locally on your machine. No cloud subscriptions, no data tracking.'
        },
        workflows: {
          title: 'Three Ways to Create 3D',
          subtitle: 'Choose the workflow that fits your needs.',
          dwg: {
            title: 'DWG/DXF to 3D',
            description: 'Upload AutoCAD files (DWG or DXF) and we extrude closed shapes into 3D models locally.'
          },
          image: {
            title: 'Image to 3D',
            description: 'Transform any 2D image into a detailed 3D model using local AI models.'
          },
          prompt: {
            title: 'Prompt to 3D',
            description: 'Describe your idea in text. Stable Diffusion generates an image, then TripoSR builds your 3D model offline.'
          }
        },
        features: {
          title: 'Plus These Features',
          viewer: 'Built-in 3D Viewer',
          export: 'GLB, STL, DXF, STEP Export',
          realtime: 'Real-Time Progress',
          local: '100% Local Processing'
        },
        tech: {
          title: 'Built With',
          subtitle: 'Powered by modern open-source technologies.',
          frontend: 'Frontend',
          backend: 'Backend',
          ai: 'AI Models',
          cad: 'CAD Tools'
        },
        cta: {
          title: 'Ready to Contribute?',
          subtitle: 'Join us on GitHub to shape the future of open-source CAD tools.',
          button: 'View on GitHub'
        },
        disclaimer: 'CADLift is an open-source project. Models run locally on your GPU.'
      }
    }
  },
  tr: {
    translation: {
      common: {
        title: 'CADLift',
        home: 'Anasayfa',
        about: 'Hakkında',
        theme_dark: 'Karanlık Mod',
        theme_light: 'Aydınlık Mod',
        footer_text: '(c) 2024 CADLift. Tüm hakları saklıdır.',
        footer_made: 'Sevgiyle geliştirildi:',
        footer_docs: 'Dokümanlar',
        footer_support: 'Destek',
        footer_github: 'GitHub',
        convert: "3D'ye Dönüştür",
        upload_title: 'DXF Dosyası Yükle',
        upload_drag: 'DXF dosyanızı buraya sürükleyin veya seçmek için tıklayın',
        upload_hint: 'Maks dosya boyutu: 50MB. Desteklenen format: .dxf',
        mode_label: 'Dönüştürme Modu',
        unit_label: 'Birim',
        height_label: 'Ekstrüzyon Yüksekliği',
        mode_floor: 'Kat Planı (Duvarlar)',
        mode_mech: 'Mekanik Parça',
        status_pending: 'Bekleniyor...',
        status_processing: 'Geometri işleniyor...',
        status_completed: 'Dönüşüm tamamlandı!',
        status_failed: 'Dönüşüm başarısız',
        status_queued: 'Sırada',
        status_cancelled: 'İptal Edildi',
        download_btn: '3D Modeli İndir',
        start_new: 'Yeni Dosya Dönüştür',
        processing_step_1: 'DXF varlıklar ayrıştırılıyor...',
        processing_step_2: 'Kapalı döngüler tespit ediliyor...',
        processing_step_3: '3D ağ oluşturuluyor...'
      },
      navigation: {
        dashboard: 'Panel',
        projects: 'Projelerim',
        docs: 'Dokümantasyon',
        resources: 'Kaynaklar',
        about: 'Hakkında'
      },
      home: {
        hero: {
          badge: 'Yapay Zeka Destekli 3D Üretimi',
          title1: 'Her Şeyi',
          title2: '3D',
          title3: "'ye",
          title4: 'Dönüştür',
          subtitle: '',
          subtitleCad: 'CAD dosyalarından',
          subtitleTo: '',
          subtitleImages: 'görüntülere',
          subtitlePrompts: 'metin promptlarına',
          subtitleEnd: '— saniyeler içinde üretime hazır 3D modeller oluşturun.',
          primaryCta: 'Oluşturmaya Başla',
          secondaryCta: 'Özellikleri Keşfet',
          inputTypes: {
            dwg: 'DWG / DXF',
            images: 'Görüntüler',
            prompts: 'AI Promptları'
          }
        },
        features: {
          badge: 'Güçlü Özellikler',
          title: 'Üç Farklı',
          titleAccent: 'Oluşturma Yolu',
          subtitle: 'Giriş yönteminizi seçin. Gerisini biz hallediyoruz.',
          cad: {
            title: "DWG/DXF'den 3D'ye",
            description: "AutoCAD dosyalarını doğrudan yükleyin. Katmanları, duvarları ve şekilleri otomatik algılar — sonra 3D modellere ekstrüde eder.",
            features: ['ODA ile yerel DWG desteği', 'Tüm DXF sürümleri', 'Otomatik katman algılama', 'Kapalı şekil ekstrüzyonu']
          },
          image: {
            title: "Görüntüden 3D'ye",
            description: 'Herhangi bir görüntü yükleyin — fotoğraflar, eskizler, renderlar. Yapay zekamız TripoSR kullanarak 3D olarak yeniden oluşturur.'
          },
          prompt: {
            title: "Prompttan 3D'ye",
            description: 'Sadece tarif edin. Stable Diffusion bir görüntü oluşturur, ardından TripoSR 3D modelinizi oluşturur.'
          },
          viewer: {
            title: '3D Görüntüleyici',
            description: 'İndirmeden önce önizleme'
          },
          export: {
            title: 'Çoklu Format',
            description: 'GLB, STL, DXF, STEP'
          }
        },
        howItWorks: {
          title: 'Nasıl',
          titleAccent: 'Çalışır',
          subtitle: "3D'ye üç basit adım",
          steps: [
            { title: 'Yükle veya Tarif Et', description: 'CAD dosyanızı, görüntünüzü bırakın veya bir prompt yazın' },
            { title: 'Yapay Zeka İşleme', description: 'Motorlarımız geometriyi algılar ve 3D oluşturur' },
            { title: 'Görüntüle ve İndir', description: '3D görüntüleyicide önizleyin, herhangi bir formatta dışa aktarın' }
          ]
        },
        cta: {
          badge: 'Ücretsiz başlayın',
          title: 'Oluşturmaya',
          titleAccent: 'Hazır mısın',
          subtitle: 'CAD dosyalarını, görüntüleri veya fikirleri 3D modellere dönüştürün. Kredi kartı gerekmez.',
          button: 'Paneli Aç'
        }
      },
      resourcesPage: {
        heading: 'Kaynaklar',
        subheading: 'Kılavuzlar, dokümanlar ve destek.',
        cards: {
          docs: { title: 'Dokümanlar', desc: 'REST uç noktalar, webhooklar ve payload şemaları.' },
          videos: { title: 'Eğitim Videoları', desc: 'EN ve TR uçtan uca videolar.' },
          faq: { title: 'SSS', desc: 'Limitler, desteklenen formatlar ve sorun giderme.' },
          community: { title: 'Topluluk & Destek', desc: 'Foruma katılın veya destek talebi açın.' }
        }
      },
      dashboard: {
        hero: {
          greeting: 'Tekrar hoş geldin',
          newUser: "CADLift'e Hoş Geldin",
          tagline: '3D Oluşturma Stüdyon',
          quickAction: 'Hızlı İşlem',
          createNew: 'Yeni Oluştur',
          viewProjects: 'Projeleri Gör',
          stats: {
            conversions: 'Dönüşüm',
            thisWeek: 'Bu Hafta',
            successRate: 'Başarı Oranı',
            avgTime: 'Ort. Süre'
          },
          emptyState: {
            title: 'Oluşturmaya hazır mısın?',
            subtitle: 'İlk 3D modelini başlatmak için aşağıdan bir iş akışı seç'
          },
          signedInAs: 'Oturum açık',
          signOut: 'Çıkış Yap'
        },
        modes: {
          title: 'Dönüşüm Modları',
          subtitle: 'Girdinize uygun iş akışını seçin. Dil ve tema tercihleriniz her moda otomatik aktarılır.',
          cad: {
            title: 'AutoCAD 2D → 3D Dönüşüm',
            description: 'DXF/DWG çizimlerini yükleyin, duvar ve parçalar otomatik olarak ekstrüde edilsin.',
            badge: 'DXF / DWG',
            cta: 'CAD Dosyası Yükle'
          },
          image: {
            title: 'Görüntüden 2D/3D Üretimi',
            description: 'Eskizleri, kat planlarını veya ürün fotoğraflarını CAD’e hazır referanslara çevirin.',
            optionsLabel: 'Uygun Çıktılar',
            option2d: 'Vektör 2D plan',
            option3d: 'Sızdırmaz 3D mesh',
            cta: 'Görüntü Yükle'
          },
          prompt: {
            title: 'Metinden 2D/3D Üretimi',
            description: 'İhtiyacınızı tarif edin, CADLift geometrileri otomatik çizsin.',
            examplesLabel: 'Örnek İstekler',
            exampleOne: 'Güney cepheli penceresi olan 3x4m bir oda çiz.',
            exampleTwo: 'İki adet M6 delikli hafif bir L-braket üret.',
            cta: 'İstekle Başlat'
          },
          comingSoon: 'Çok Yakında',
          betaLabel: 'Beta'
        },
        recent: {
          title: 'Son Aktiviteler',
          subtitle: 'Önceki işleri takip edin, çıktıları indirin veya yeniden deneyin.',
          empty: 'Henüz bir iş yok. Bu zaman çizelgesini doldurmak için dönüştürme başlatın.',
          table: {
            type: 'İş Tipi',
            input: 'Girdi',
            output: 'Çıktı',
            status: 'Durum',
            created: 'Oluşturulma',
            actions: 'İşlemler'
          },
          action: {
            view: 'Görüntüle',
            download: 'İndir',
            retry: 'Tekrarla'
          },
          time_two_hours: '2 saat önce',
          time_ten_minutes: '10 dakika önce',
          time_yesterday: 'Dün',
          time_just_now: 'Az önce'
        },
        quickLinks: {
          title: 'Kaynaklar',
          subtitle: 'Rehberler, dokümantasyon ve destek bağlantıları.',
          documentation: {
            title: 'Dokümantasyon',
            description: 'REST uç noktalar, webhooklar ve veri şemaları.'
          },
          tutorials: {
            title: 'Eğitim Videoları',
            description: 'EN ve TR rehberli baştan sona anlatımlar.'
          },
          faq: {
            title: 'SSS',
            description: 'Limitler, desteklenen formatlar ve sorun giderme.'
          },
          support: {
            title: 'Topluluk & Destek',
            description: 'Foruma katılın veya destek talebi açın.'
          }
        },
        workspace: {
          title: 'Dönüşüm Çalışma Alanı',
          subtitle: 'DXF yükleyin, ekstrüzyon parametrelerini belirleyin ve ilerlemeyi anlık takip edin.',
          statusReady: 'Sistem hazır. Girdi bekleniyor...'
        },
        quickStart: {
          title: 'Hızlı Başlangıç',
          description: 'Bir tıkla iş akışı başlatın veya kısayolları kullanın.',
          actions: {
            uploadCad: 'CAD Yükle',
            uploadImage: 'Görüntü Yükle',
            startPrompt: 'İstek Başlat'
          }
        },
        tips: {
          title: 'Başlangıç İpuçları',
          upload: 'Klasik 2D → 3D ekstrüzyon için CAD dosyası yükleyin.',
          prompt: 'Metin tabanlı keşifler için prompt üreticisini deneyin.',
          dismiss: 'Anladım'
        },
        imageForm: {
          title: "Görüntüden CAD'e",
          description: 'Eskizleri, taramaları veya ürün fotoğraflarını vektör planlara ya da mesh’lere çevirin.',
          uploadLabel: 'Görüntüyü bırakın veya göz atın',
          uploadHint: 'Desteklenen formatlar: PNG, JPG, SVG (25MB’a kadar)',
          pickButton: 'Görüntü Seç',
          option2d: {
            title: 'Vektör 2D Çıktı',
            desc: 'Temiz DXF eğrileri ve katmanlar oluşturur.'
          },
          option3d: {
            title: '3D Mesh Çıktı',
            desc: 'CAD yazılımlarına hazır sızdırmaz mesh oluşturur.'
          },
          notesLabel: 'Notlar',
          notesPlaceholder: 'Ölçek, birim veya beklenen detay hakkında bilgi verin.',
          submit: 'Görüntüden Üret',
          submitLoading: 'Görüntü işleniyor...',
          errors: {
            unsupported: 'Desteklenmeyen dosya türü. Lütfen PNG/JPG/SVG kullanın.',
            tooLarge: 'Görüntü 25MB limitini aşıyor.',
            required: 'Devam etmek için bir görüntü ekleyin.'
          }
        },
        promptForm: {
          title: "Prompt'tan Geometri",
          description: 'Mekanı veya parçayı tarif edin. CADLift döngüleri ve katıları çizer.',
          promptLabel: 'Ne çizelim?',
          placeholder: 'Örn. 50mm çaplı silindirik adaptör ve iki cıvata paternli...',
          option2d: {
            title: '2D Taslak',
            desc: 'Gözden geçirme için DXF çizgiler ve yaylar üretir.'
          },
          option3d: {
            title: '3D Konsept',
            desc: 'Hafif STEP mesh çıktısı verir.'
          },
          detailLabel: 'Detay Seviyesi',
          detailLow: 'Kabaca',
          detailHigh: 'Hassas',
          submit: 'Nesne Oluştur',
          submitLoading: 'Oluşturuluyor...',
          errors: {
            required: 'Lütfen ihtiyacınızı tarif edin.'
          }
        }
      },
      aboutLegacy: {
        heading: 'CADLift Hakkında',
        description:
          'CADLift, 2D teknik çizimlerinizi anında 3D modellere dönüştürür. Gelişmiş geometri işleme teknolojisiyle çizim ve modelleme arasındaki boşluğu kapatıyoruz.',
        features_title: 'Temel Özellikler',
        feature_1: "Anında DXF'den 3D'ye dönüşüm",
        feature_2: 'Akıllı kapalı döngü algılama',
        feature_3: 'AutoCAD & Blender için FBX/OBJ çıktısı',
        disclaimer: 'Bu bir demo MVP sürümüdür.'
      },
      auth: {
        signIn: {
          title: 'Tekrar Hoş Geldiniz',
          subtitle: 'Çalışma alanına erişmek için bilgilerinizi girin',
          emailLabel: 'E-posta Adresi',
          emailPlaceholder: 'muhendis@cadlift.io',
          passwordLabel: 'Şifre',
          forgot: 'Unuttunuz mu?',
          submit: 'Giriş Yap',
          submitting: 'Giriş yapılıyor...',
          or: 'Veya',
          googleSignIn: 'Google ile devam et',
          noAccount: "CADLift'te yeni misiniz?",
          createAccount: 'Hesap oluşturun',
          failed: 'Giriş başarısız'
        },
        signUp: {
          title: 'Hesap Oluştur',
          subtitle: '3D yolculuğunuza bugün başlayın',
          nameLabel: 'Ad Soyad',
          namePlaceholder: 'Ahmet Yılmaz',
          emailLabel: 'E-posta Adresi',
          emailPlaceholder: 'muhendis@cadlift.io',
          passwordLabel: 'Şifre',
          passwordHint: 'En az 8 karakter',
          submit: 'Başla',
          submitting: 'Hesap oluşturuluyor...',
          or: 'Veya',
          googleSignUp: 'Google ile kaydol',
          hasAccount: 'Zaten hesabınız var mı?',
          signIn: 'Giriş yapın',
          failed: 'Kayıt başarısız'
        },
        signOut: 'Çıkış Yap'
      },
      profile: {
        title: 'Profiliniz',
        memberSince: 'Üyelik başlangıcı',
        openSource: 'Açık Kaynak',
        settings: {
          title: 'Ayarlar',
          appearance: 'Görünüm',
          language: 'Dil',
          account: 'Hesap',
          security: 'Güvenlik',
          dangerZone: 'Tehlikeli Bölge'
        },
        theme: {
          light: 'Açık',
          dark: 'Koyu'
        },
        actions: {
          editProfile: 'Profili Düzenle',
          changePassword: 'Şifre Değiştir',
          twoFactor: 'İki Faktörlü Doğrulama',
          activeSessions: 'Aktif Oturumlar',
          loginHistory: 'Giriş Geçmişi',
          deleteData: 'Tüm Verileri Sil',
          deleteAccount: 'Hesabı Sil'
        },
        modals: {
          editProfile: {
            title: 'Profili Düzenle',
            displayName: 'Görünen Ad',
            save: 'Değişiklikleri Kaydet',
            saving: 'Kaydediliyor...',
            success: 'Profil başarıyla güncellendi!',
            error: 'Profil güncellenemedi'
          },
          changePassword: {
            title: 'Şifre Değiştir',
            current: 'Mevcut Şifre',
            new: 'Yeni Şifre',
            confirm: 'Şifreyi Onayla',
            hint: 'En az 8 karakter, büyük-küçük harf ve rakam kullanın',
            save: 'Şifreyi Güncelle',
            saving: 'Güncelleniyor...',
            success: 'Şifre başarıyla değiştirildi!',
            mismatch: 'Şifreler eşleşmiyor',
            error: 'Şifre değiştirilemedi'
          },
          sessions: {
            title: 'Aktif Oturumlar',
            current: 'Mevcut Oturum',
            device: 'Cihaz',
            browser: 'Tarayıcı',
            location: 'Konum',
            lastActive: 'Son Aktivite',
            revokeAll: 'Diğer Oturumları Sonlandır'
          },
          loginHistory: {
            title: 'Giriş Geçmişi',
            recentLogins: 'Son Girişler',
            success: 'Başarılı',
            failed: 'Başarısız'
          },
          deleteConfirm: {
            title: 'Emin misiniz?',
            warning: 'Bu işlem geri alınamaz. Verileriniz kalıcı olarak silinecektir.',
            cancel: 'İptal',
            confirm: 'Evet, Sil'
          },
          comingSoon: 'Çok Yakında',
          twoFactorMessage: 'İki faktörlü doğrulama gelecek bir güncellemede kullanıma sunulacak.'
        }
      },
      footer: {
        brand: {
          description: '2D tasarımlarınızı anında çarpıcı 3D modellere dönüştürün. Gelişmiş geometri işleme ve yapay zeka ile güçlendirilmiştir.'
        },
        sections: {
          product: 'Ürün',
          resources: 'Kaynaklar',
          company: 'Şirket'
        },
        links: {
          dashboard: 'Panel',
          dwgTo3d: "DWG/DXF'den 3D'ye",
          imageTo3d: "Görüntüden 3D'ye",
          promptTo3d: "Prompttan 3D'ye",
          apiDocs: 'API Belgeleri',
          resources: 'Kaynaklar',
          faq: 'SSS',
          community: 'Topluluk',
          about: 'Hakkında',
          github: 'GitHub',
          contact: 'İletişim'
        },
        copyright: 'Tüm hakları saklıdır.',
        madeWith: 'Sevgiyle yapıldı',
        by: ''
      },
      viewer: {
        title: '3D Model Görüntüleyici',
        download: 'İndir',
        screenshot: 'Ekran Görüntüsü',
        screenshotSoon: 'Ekran görüntüsü özelliği çok yakında!',
        supportedFormats: 'Desteklenen Formatlar',
        poweredBy: 'Altyapı'
      },
      about: {
        badge: 'Yapay Zeka Destekli 3D Üretim',
        hero: {
          title1: 'Her Şeyi',
          titleHighlight: '3D\'ye',
          title2: 'Dönüştür',
          subtitle: 'CADLift, yapay zeka ve gelişmiş geometri işleme kullanarak CAD dosyalarını, görselleri ve metin komutlarını üretime hazır 3D modellere dönüştüren açık kaynaklı bir platformdur.'
        },
        workflows: {
          title: '3D Oluşturmanın Üç Yolu',
          subtitle: 'İhtiyacınıza uygun iş akışını seçin.',
          dwg: {
            title: 'DWG/DXF\'ten 3D',
            description: 'AutoCAD dosyalarını (DWG veya DXF) yükleyin, kapalı şekilleri 3D modellere dönüştürelim. Duvar, kapı ve pencere algılama desteği.'
          },
          image: {
            title: 'Görüntüden 3D',
            description: 'TripoSR AI kullanarak herhangi bir 2D görüntüyü detaylı 3D modele dönüştürün. Fotoğraflar, eskizler ve renderlarla çalışır.'
          },
          prompt: {
            title: 'Metinden 3D',
            description: 'Fikrinizi metin olarak tanımlayın. Yapay zekamız Stable Diffusion ile bir görüntü oluşturur, ardından 3D\'ye dönüştürür.'
          }
        },
        features: {
          title: 'Ek Özellikler',
          viewer: 'Yerleşik 3D Görüntüleyici',
          export: 'GLB, STL, DXF, STEP Dışa Aktarma',
          realtime: 'Gerçek Zamanlı İlerleme',
          local: 'Yerel İşleme'
        },
        tech: {
          title: 'Kullanılan Teknolojiler',
          subtitle: 'Modern, açık kaynaklı teknolojiler.',
          frontend: 'Ön Uç',
          backend: 'Arka Uç',
          ai: 'Yapay Zeka Modelleri',
          cad: 'CAD Araçları'
        },
        cta: {
          title: 'Denemeye Hazır mısınız?',
          subtitle: 'CAD dosyalarından, görsellerden veya metin komutlarından hemen şimdi 3D modeller oluşturmaya başlayın.',
          button: 'Paneli Aç'
        },
        disclaimer: 'CADLift açık kaynaklı bir projedir. Yapay zeka özellikleri ilk kullanımda model indirmesi gerektirir.'
      }
    }
  },
  de: {
    translation: {
      common: {
        title: 'CADLift',
        home: 'Startseite',
        about: 'Über uns',
        theme_dark: 'Dunkelmodus',
        theme_light: 'Hellmodus',
        footer_text: '(c) 2024 CADLift. Alle Rechte vorbehalten.',
        footer_made: 'Mit Liebe entwickelt von',
        footer_docs: 'Dokumentation',
        footer_support: 'Support',
        footer_github: 'GitHub',
        convert: 'In 3D umwandeln',
        upload_title: 'DXF-Datei hochladen',
        upload_drag: 'DXF-Datei hier ablegen oder klicken zum Auswählen',
        upload_hint: 'Max. Dateigröße: 50MB. Unterstütztes Format: .dxf',
        mode_label: 'Konvertierungsmodus',
        unit_label: 'Einheit',
        height_label: 'Extrusionshöhe',
        mode_floor: 'Grundriss (Wände)',
        mode_mech: 'Mechanisches Teil',
        status_pending: 'Ausstehend...',
        status_processing: 'Geometrie wird verarbeitet...',
        status_completed: 'Konvertierung abgeschlossen!',
        status_failed: 'Konvertierung fehlgeschlagen',
        status_queued: 'In Warteschlange',
        status_cancelled: 'Abgebrochen',
        download_btn: '3D-Modell herunterladen',
        start_new: 'Weitere Datei konvertieren',
        processing_step_1: 'DXF wird analysiert...',
        processing_step_2: 'Geometrie wird extrudiert...',
        processing_step_3: 'STEP-Datei wird generiert...'
      },
      navigation: {
        dashboard: 'Dashboard',
        projects: 'Meine Projekte',
        docs: 'Dokumentation',
        resources: 'Ressourcen',
        about: 'Über uns'
      },
      home: {
        hero: {
          badge: 'KI-gestützte 3D-Generierung',
          title1: 'Verwandle',
          title2: 'Alles',
          title3: 'in',
          title4: '3D',
          subtitle: 'Von',
          subtitleCad: 'CAD-Dateien',
          subtitleTo: 'über',
          subtitleImages: 'Bilder',
          subtitlePrompts: 'Text-Prompts',
          subtitleEnd: '— generieren Sie produktionsreife 3D-Modelle in Sekunden.',
          primaryCta: 'Jetzt erstellen',
          secondaryCta: 'Funktionen entdecken',
          inputTypes: {
            dwg: 'DWG / DXF',
            images: 'Bilder',
            prompts: 'KI-Prompts'
          }
        },
        features: {
          badge: 'Leistungsstarke Funktionen',
          title: 'Drei Wege zum',
          titleAccent: 'Erstellen',
          subtitle: 'Wählen Sie Ihre Eingabemethode. Wir erledigen den Rest.',
          cad: {
            title: 'DWG/DXF zu 3D',
            description: 'Laden Sie AutoCAD-Dateien direkt hoch. Wir erkennen automatisch Ebenen, Wände und Formen — und extrudieren zu 3D-Modellen.',
            features: ['Native DWG-Unterstützung via ODA', 'Alle DXF-Versionen', 'Automatische Ebenenerkennung', 'Geschlossene Form-Extrusion']
          },
          image: {
            title: 'Bild zu 3D',
            description: 'Laden Sie beliebige Bilder hoch — Fotos, Skizzen, Render. Unsere KI rekonstruiert sie in 3D mit TripoSR.'
          },
          prompt: {
            title: 'Prompt zu 3D',
            description: 'Einfach beschreiben. Stable Diffusion generiert ein Bild, dann erstellt TripoSR Ihr 3D-Modell.'
          },
          viewer: {
            title: '3D-Viewer',
            description: 'Vorschau vor dem Download'
          },
          export: {
            title: 'Multi-Format',
            description: 'GLB, STL, DXF, STEP'
          }
        },
        howItWorks: {
          title: 'So',
          titleAccent: 'funktioniert es',
          subtitle: 'Drei einfache Schritte zu 3D',
          steps: [
            { title: 'Hochladen oder Beschreiben', description: 'CAD-Datei, Bild oder Prompt eingeben' },
            { title: 'KI-Verarbeitung', description: 'Unsere Engines erkennen Geometrie und generieren 3D' },
            { title: 'Ansehen & Herunterladen', description: 'Im 3D-Viewer prüfen, in jedem Format exportieren' }
          ]
        },
        cta: {
          badge: 'Kostenlos starten',
          title: 'Bereit zum',
          titleAccent: 'Erstellen',
          subtitle: 'Verwandeln Sie CAD-Dateien, Bilder oder Ideen in 3D-Modelle. Keine Kreditkarte erforderlich.',
          button: 'Dashboard öffnen'
        }
      },
      resourcesPage: {
        heading: 'Lernen & Erstellen',
        subheading: 'Erkunden Sie unsere Dokumentation, Tutorials und Community-Ressourcen.',
        cards: {
          docs: {
            title: 'API-Dokumentation',
            desc: 'Vollständige API-Referenz für die Integration von CADLift in Ihre Anwendungen.'
          },
          videos: {
            title: 'Video-Tutorials',
            desc: 'Schritt-für-Schritt-Anleitungen für häufige Arbeitsabläufe und Anwendungsfälle.'
          },
          faq: {
            title: 'FAQ',
            desc: 'Antworten auf häufig gestellte Fragen zur 3D-Konvertierung.'
          },
          community: {
            title: 'Community',
            desc: 'Treten Sie unserer Community bei, um Hilfe zu erhalten und Ihre Projekte zu teilen.'
          }
        }
      },
      dashboard: {
        hero: {
          greeting: 'Willkommen zurück',
          newUser: 'Willkommen bei CADLift',
          tagline: 'Ihr 3D-Kreativstudio',
          quickAction: 'Schnellaktion',
          createNew: 'Neu erstellen',
          viewProjects: 'Projekte ansehen',
          stats: {
            conversions: 'Konvertierungen',
            thisWeek: 'Diese Woche',
            successRate: 'Erfolgsrate',
            avgTime: 'Durchschn. Zeit'
          },
          emptyState: {
            title: 'Bereit zu erstellen?',
            subtitle: 'Wählen Sie unten einen Arbeitsablauf, um Ihr erstes 3D-Modell zu starten'
          },
          signedInAs: 'Angemeldet als',
          signOut: 'Abmelden'
        },
        modes: {
          title: 'Konvertierungsmodi',
          subtitle: 'Wählen Sie den Arbeitsablauf, der zu Ihrer Eingabe passt. Sprache und Design werden automatisch übernommen.',
          cad: {
            title: 'AutoCAD 2D → 3D Konvertierung',
            description: 'Laden Sie DXF/DWG-Zeichnungen hoch und extrudieren Sie automatisch saubere architektonische oder mechanische Körper.',
            badge: 'DXF / DWG',
            cta: 'CAD-Datei hochladen'
          },
          image: {
            title: 'Bild zu 2D/3D Generator',
            description: 'Verwandeln Sie Skizzen, Grundrisse oder Produktfotos in CAD-fertige Referenzen.',
            optionsLabel: 'Verfügbare Ausgaben',
            option2d: 'Vektor 2D-Plan',
            option3d: 'Wasserdichtes 3D-Mesh',
            cta: 'Bild hochladen'
          },
          prompt: {
            title: 'Text-Prompt zu 2D/3D',
            description: 'Beschreiben Sie, was Sie brauchen, und lassen Sie CADLift die Geometrie automatisch erstellen.',
            examplesLabel: 'Prompt-Ideen',
            exampleOne: 'Zeichne einen 3x4m Raum mit einem Südfenster.',
            exampleTwo: 'Erzeuge einen leichten L-Winkel mit zwei M6-Bohrungen.',
            cta: 'Prompt-Generierung starten'
          },
          comingSoon: 'Demnächst',
          betaLabel: 'Beta'
        },
        recent: {
          title: 'Letzte Aktivität',
          subtitle: 'Verfolgen Sie vergangene Aufträge, laden Sie Ergebnisse herunter oder wiederholen Sie fehlgeschlagene Jobs.',
          empty: 'Noch keine Jobs. Starten Sie eine Konvertierung, um diese Zeitleiste zu füllen.',
          table: {
            type: 'Job-Typ',
            input: 'Eingabe',
            output: 'Ausgabe',
            status: 'Status',
            created: 'Erstellt',
            actions: 'Aktionen'
          },
          action: {
            view: 'Ansehen',
            download: 'Herunterladen',
            retry: 'Wiederholen'
          },
          time_two_hours: 'Vor 2 Stunden',
          time_ten_minutes: 'Vor 10 Minuten',
          time_yesterday: 'Gestern',
          time_just_now: 'Gerade eben'
        },
        quickLinks: {
          title: 'Ressourcen',
          subtitle: 'Anleitungen, Dokumentation und Support für Ihren Fortschritt.',
          documentation: {
            title: 'Dokumentation',
            description: 'REST-Endpunkte, Webhooks und Payload-Schemas.'
          },
          tutorials: {
            title: 'Tutorial-Videos',
            description: 'Schritt-für-Schritt-Anleitungen auf EN und DE.'
          },
          faq: {
            title: 'FAQ',
            description: 'Limits, unterstützte Formate und Fehlerbehebung.'
          },
          support: {
            title: 'Community & Support',
            description: 'Treten Sie dem Forum bei oder eröffnen Sie ein Support-Ticket.'
          }
        },
        workspace: {
          title: 'Konvertierungs-Arbeitsbereich',
          subtitle: 'Laden Sie eine DXF hoch, legen Sie Extrusionsparameter fest und verfolgen Sie den Fortschritt in Echtzeit.',
          statusReady: 'System bereit. Warte auf Eingabe...'
        },
        quickStart: {
          title: 'Schnellstart',
          description: 'Starten Sie einen Arbeitsablauf mit einem Klick oder nutzen Sie Tastenkürzel.',
          actions: {
            uploadCad: 'CAD hochladen',
            uploadImage: 'Bild hochladen',
            startPrompt: 'Prompt starten'
          }
        },
        tips: {
          title: 'Onboarding-Tipps',
          upload: 'Laden Sie eine CAD-Datei hoch, um die klassische 2D → 3D Extrusion zu starten.',
          prompt: 'Probieren Sie den Prompt-Generator für textbasierte Erkundungen.',
          dismiss: 'Verstanden'
        },
        imageForm: {
          title: 'Bild zu CAD Arbeitsablauf',
          description: 'Verwandeln Sie Skizzen, Scans oder Produktfotos in Vektorpläne oder Meshes.',
          uploadLabel: 'Bild ablegen oder durchsuchen',
          uploadHint: 'Unterstützt: PNG, JPG, SVG bis 25MB',
          pickButton: 'Bild auswählen',
          option2d: {
            title: 'Vektor 2D-Ausgabe',
            desc: 'Erzeugt saubere DXF-Kurven und Ebenen.'
          },
          option3d: {
            title: '3D-Mesh-Ausgabe',
            desc: 'Erstellt wasserdichte Meshes für CAD-Apps.'
          },
          notesLabel: 'Notizen',
          notesPlaceholder: 'Geben Sie Informationen zu Maßstab, Einheiten oder gewünschtem Detailgrad an.',
          submit: 'Aus Bild generieren',
          submitLoading: 'Bild wird verarbeitet...',
          errors: {
            unsupported: 'Nicht unterstützter Dateityp. Bitte PNG/JPG/SVG verwenden.',
            tooLarge: 'Bild überschreitet 25MB-Limit.',
            required: 'Bitte fügen Sie ein Bild hinzu, um fortzufahren.'
          }
        },
        promptForm: {
          title: 'Prompt zu Geometrie',
          description: 'Beschreiben Sie den Raum oder das Teil. CADLift erstellt Schleifen und Körper.',
          promptLabel: 'Was sollen wir zeichnen?',
          placeholder: 'z.B. Zylindrischer Adapter mit 50mm Durchmesser und zwei Schraubenmustern...',
          option2d: {
            title: '2D-Entwurf',
            desc: 'Gibt DXF-Linien und -Bögen zur Überprüfung aus.'
          },
          option3d: {
            title: '3D-Konzept',
            desc: 'Gibt leichte STEP-Meshes aus.'
          },
          detailLabel: 'Detailstufe',
          detailLow: 'Grob',
          detailHigh: 'Präzise',
          submit: 'Objekt generieren',
          submitLoading: 'Wird generiert...',
          errors: {
            required: 'Bitte beschreiben Sie, was Sie benötigen.'
          }
        }
      },
      auth: {
        signIn: {
          title: 'Willkommen zurück',
          subtitle: 'Geben Sie Ihre Anmeldedaten ein',
          emailLabel: 'E-Mail-Adresse',
          emailPlaceholder: 'ingenieur@cadlift.io',
          passwordLabel: 'Passwort',
          forgot: 'Vergessen?',
          submit: 'Anmelden',
          submitting: 'Wird angemeldet...',
          or: 'Oder',
          googleSignIn: 'Mit Google fortfahren',
          noAccount: 'Neu bei CADLift?',
          createAccount: 'Konto erstellen',
          failed: 'Anmeldung fehlgeschlagen'
        },
        signUp: {
          title: 'Konto erstellen',
          subtitle: 'Starten Sie noch heute Ihre 3D-Reise',
          nameLabel: 'Vollständiger Name',
          namePlaceholder: 'Max Mustermann',
          emailLabel: 'E-Mail-Adresse',
          emailPlaceholder: 'ingenieur@cadlift.io',
          passwordLabel: 'Passwort',
          passwordHint: 'Mindestens 8 Zeichen',
          submit: 'Loslegen',
          submitting: 'Konto wird erstellt...',
          or: 'Oder',
          googleSignUp: 'Mit Google registrieren',
          hasAccount: 'Bereits ein Konto?',
          signIn: 'Anmelden',
          failed: 'Registrierung fehlgeschlagen'
        },
        signOut: 'Abmelden'
      },
      profile: {
        title: 'Ihr Profil',
        memberSince: 'Mitglied seit',
        openSource: 'Open Source',
        settings: {
          title: 'Einstellungen',
          appearance: 'Erscheinungsbild',
          language: 'Sprache',
          account: 'Konto',
          editProfile: 'Profil bearbeiten',
          changePassword: 'Passwort ändern'
        },
        preferences: {
          title: 'Einstellungen',
          theme: 'Thema',
          themeLight: 'Hell',
          themeDark: 'Dunkel'
        },
        security: {
          title: 'Sicherheit',
          twoFactor: 'Zwei-Faktor-Authentifizierung',
          activeSessions: 'Aktive Sitzungen',
          loginHistory: 'Anmeldeverlauf'
        },
        activity: {
          title: 'Letzte Aktivität',
          empty: 'Noch keine Aktivität'
        },
        danger: {
          title: 'Gefahrenzone',
          deleteData: 'Alle Daten löschen',
          deleteAccount: 'Konto löschen'
        }
      },
      footer: {
        brand: {
          description: 'Verwandeln Sie Ihre 2D-Designs sofort in beeindruckende 3D-Modelle.'
        },
        sections: {
          product: 'Produkt',
          resources: 'Ressourcen',
          company: 'Unternehmen'
        },
        links: {
          dashboard: 'Dashboard',
          dwgTo3d: 'DWG/DXF zu 3D',
          imageTo3d: 'Bild zu 3D',
          promptTo3d: 'Prompt zu 3D',
          apiDocs: 'API-Dokumentation',
          resources: 'Ressourcen',
          faq: 'FAQ',
          community: 'Community',
          about: 'Über uns',
          github: 'GitHub',
          contact: 'Kontakt'
        },
        copyright: 'Alle Rechte vorbehalten.',
        madeWith: 'Entwickelt mit',
        by: 'von'
      },
      viewer: {
        title: '3D-Modell-Viewer',
        download: 'Herunterladen',
        screenshot: 'Screenshot',
        screenshotSoon: 'Screenshot-Funktion kommt bald!',
        supportedFormats: 'Unterstützte Formate',
        poweredBy: 'Powered by'
      },
      about: {
        badge: 'KI-gestützte 3D-Generierung',
        hero: {
          title1: 'Verwandle',
          titleHighlight: 'Alles',
          title2: 'in 3D',
          subtitle: 'CADLift ist eine Open-Source-Plattform, die CAD-Dateien, Bilder und Textbefehle mithilfe von KI in produktionsreife 3D-Modelle konvertiert.'
        },
        workflows: {
          title: 'Drei Wege zu 3D',
          subtitle: 'Wählen Sie den Arbeitsablauf, der zu Ihren Anforderungen passt.',
          dwg: {
            title: 'DWG/DXF zu 3D',
            description: 'Laden Sie AutoCAD-Dateien hoch und wir extrudieren geschlossene Formen zu 3D-Modellen.'
          },
          image: {
            title: 'Bild zu 3D',
            description: 'Verwandeln Sie jedes 2D-Bild mit TripoSR-KI in ein detailliertes 3D-Modell.'
          },
          prompt: {
            title: 'Prompt zu 3D',
            description: 'Beschreiben Sie Ihre Idee in Text. Unsere KI generiert ein Bild und konvertiert es zu 3D.'
          }
        },
        features: {
          title: 'Zusätzliche Funktionen',
          viewer: 'Integrierter 3D-Viewer',
          export: 'GLB, STL, DXF, STEP Export',
          realtime: 'Echtzeit-Fortschritt',
          local: 'Lokale Verarbeitung'
        },
        tech: {
          title: 'Technologie-Stack',
          subtitle: 'Moderne Open-Source-Technologien.',
          frontend: 'Frontend',
          backend: 'Backend',
          ai: 'KI-Modelle',
          cad: 'CAD-Tools'
        },
        cta: {
          title: 'Bereit zum Ausprobieren?',
          subtitle: 'Starten Sie jetzt mit der Generierung von 3D-Modellen aus CAD-Dateien, Bildern oder Textbefehlen.',
          button: 'Dashboard öffnen'
        },
        disclaimer: 'CADLift ist ein Open-Source-Projekt. KI-Funktionen erfordern beim ersten Gebrauch einen Modell-Download.'
      }
    }
  }
};

const initialLanguage = getInitialLanguage();

i18n.use(initReactI18next).init({
  resources,
  lng: initialLanguage,
  fallbackLng: 'en',
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
