# 🚀 CADLift – Her Şeyi 3D'ye Dönüştür

<div align="center">

**CAD dosyalarından görsellerden ve metin promptlarından — CADLift saniyeler içinde üretim kalitesinde 3D modeller oluşturur.**

[![Status](https://img.shields.io/badge/durum-active-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![React](https://img.shields.io/badge/react-18+-61dafb)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

[🎯 Canlı Demo](#) · [📖 Dokümantasyon](backend/docs/) · [🐛 Hata Bildir](https://github.com/vartmor/cadlift/issues)

🌍 Türkçe | [English](README.md)

</div>

---

## ✨ 3D Oluşturmanın Üç Yolu

| 🏗️ CAD Dosyaları | 🖼️ Görseller | 💬 Metin Promptları |
|:---:|:---:|:---:|
| DWG veya DXF yükle | Herhangi bir görsel yükle | Ne istediğini tarif et |
| Katmanları otomatik algıla | Yapay zeka destekli rekonstrüksiyon | Stable Diffusion + TripoSR |
| 3D'ye extrude et | TripoSR AI modeli | Hayal et, oluştur |

---

## 🎯 CADLift'i Özel Yapan Ne?

### 🏗️ DWG/DXF'den 3D'ye
- **DWG Desteği** – ODA File Converter ile yerel AutoCAD dosyaları
- **DXF Desteği** – Tüm versiyonlar, tüm katmanlar
- **Akıllı Algılama** – Kapalı şekilleri, duvarları, kapıları, pencereleri otomatik algılar
- **co2tools Entegrasyonu** – Sağlam extrusion motoru

### 🖼️ Görselden 3D'ye  
- **Her Görsel** – Fotoğraflar, çizimler, renderlar, ekran görüntüleri
- **TripoSR AI** – Tek görselten 3D rekonstrüksiyon
- **Arka Plan Kaldırma** – Otomatik konu izolasyonu

### 💬 Prompttan 3D'ye
- **Doğal Dil** – Sadece ne istediğini tarif et
- **Stable Diffusion** – AI destekli referans görsel oluşturma
- **Uçtan Uca** – Metinden görüntülenebilir 3D modele

### 📦 Çoklu Format Export
| Format | Kullanım Alanı |
|--------|------------|
| **GLB** | Web 3D, oyun motorları (Unity, Unreal, Three.js) |
| **STL** | 3D baskı (Cura, PrusaSlicer) |
| **DXF** | CAD yazılımları (AutoCAD, FreeCAD) |
| **STEP** | Mühendislik CAD (SolidWorks, Fusion 360) |

---

## ⚠️ Sadece Yerel Çalışan Özellikler

Bazı özellikler GPU gereksinimleri nedeniyle yerel kurulum gerektirir:

| Özellik | Gereksinim | Cloud'da Mevcut |
|---------|------------|-----------------|
| DWG/DXF'den 3D'ye | ODA Converter | ✅ |
| Prompttan 3D'ye (Hassas) | OpenAI API | ✅ |
| Prompttan 3D'ye (Kreatif) | TripoSR + SD | ❌ Sadece yerel |
| Görselden 3D'ye | TripoSR | ❌ Sadece yerel |

> **Not:** GPU destekli özellikler için lütfen [CADLift'i yerelde çalıştırın](#-hızlı-başlangıç).

---

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.11+
- Node.js 20+
- [ODA File Converter](https://www.opendesign.com/guestfiles/oda_file_converter) (DWG desteği için)

### Backend Kurulumu

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend Kurulumu

```bash
npm install
npm run dev
```

### Ortam Değişkenleri

`backend/.env` oluşturun:

```env
DATABASE_URL=sqlite+aiosqlite:///./cadlift.db
STORAGE_PATH=./storage
JWT_SECRET_KEY=gizli-anahtar
ENABLE_TASK_QUEUE=false
LOG_LEVEL=INFO
```

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! [CONTRIBUTING.md](CONTRIBUTING.md) dosyasına bakın.

**Katkı fikirleri:**
- Ek export formatları (FBX, DAE)
- Çok katlı bina algılama
- Doku ve malzeme desteği
- Mobil uygulama

---

## 📄 Lisans

MIT Lisansı - [LICENSE](LICENSE) dosyasına bakın

---

<div align="center">

**❤️ ile [Vartmor](https://github.com/vartmor) tarafından yapıldı**

⭐ CADLift işinize yaradıysa yıldız verin!

</div>
