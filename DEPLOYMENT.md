# CADLift Deployment Guide 🚀

## Gereksinimler
- GitHub hesabı (repo public veya private)
- Render.com hesabı (ücretsiz)
- OpenAI API anahtarı

---

## Adım 1: GitHub'a Push

```powershell
# Proje klasörüne git
cd C:\Users\Muhammed\Desktop\cadlift

# Değişiklikleri ekle
git add .

# Commit yap
git commit -m "Add Render deployment config"

# Push et
git push origin main
```

---

## Adım 2: Render Hesabı Oluştur

1. https://render.com adresine git
2. **"Get Started for Free"** tıkla
3. **GitHub ile giriş yap** (önerilir)
4. E-postayı doğrula

---

## Adım 3: Backend Deploy (API)

### 3.1 Yeni Web Service Oluştur
1. Dashboard'da **"New +"** → **"Web Service"**
2. **"Build and deploy from a Git repository"** seç
3. GitHub repo'nu bağla: `vartmor/CADLift`

### 3.2 Ayarları Yapılandır
| Alan | Değer |
|------|-------|
| **Name** | `cadlift-api` |
| **Region** | Frankfurt (EU) veya en yakın |
| **Branch** | `main` |
| **Runtime** | Docker |
| **Dockerfile Path** | `./Dockerfile` |
| **Instance Type** | Free |

### 3.3 Ortam Değişkenleri
**"Advanced"** → **"Add Environment Variable"**:

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `sqlite+aiosqlite:///./cadlift.db` |
| `STORAGE_PATH` | `/app/storage` |
| `JWT_SECRET_KEY` | (Generate tıkla veya rastgele string) |
| `OPENAI_API_KEY` | `sk-...` (kendi anahtarın) |
| `CORS_ORIGINS` | `https://cadlift-frontend.onrender.com` |
| `LOG_LEVEL` | `INFO` |
| `ENABLE_TASK_QUEUE` | `false` |

### 3.4 Disk Ekle (Storage için)
**"Advanced"** → **"Add Disk"**:
- **Name:** `cadlift-storage`
- **Mount Path:** `/app/storage`
- **Size:** 1 GB

### 3.5 Deploy
**"Create Web Service"** tıkla ve bekle (~5-10 dk)

---

## Adım 4: Frontend Deploy (Static Site)

### 4.1 Yeni Static Site Oluştur
1. Dashboard'da **"New +"** → **"Static Site"**
2. Aynı GitHub repo'yu seç

### 4.2 Ayarları Yapılandır
| Alan | Değer |
|------|-------|
| **Name** | `cadlift-frontend` |
| **Branch** | `main` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

### 4.3 Ortam Değişkeni
| Key | Value |
|-----|-------|
| `VITE_API_URL` | `https://cadlift-api.onrender.com` |

### 4.4 Redirect Rule Ekle
**"Redirects/Rewrites"** → **"Add Rule"**:
- **Source:** `/*`
- **Destination:** `/index.html`
- **Action:** Rewrite

### 4.5 Deploy
**"Create Static Site"** tıkla

---

## Adım 5: CORS Güncelle

Backend deploy olduktan sonra frontend URL'ini CORS'a ekle:

1. Backend service'e git
2. **"Environment"** tab
3. `CORS_ORIGINS` değerini güncelle:
   ```
   https://cadlift-frontend.onrender.com,http://localhost:5173
   ```
4. **"Save Changes"** → Otomatik redeploy olur

---

## Adım 6: Test Et

1. Frontend URL'ine git: `https://cadlift-frontend.onrender.com`
2. Kayıt ol / Giriş yap
3. **Prompt to 3D** dene: "a coffee mug"
4. Sonucu kontrol et ✅

---

## Çalışan Özellikler

| Özellik | Durum |
|---------|-------|
| Prompt to 3D (Precision) | ✅ Çalışır |
| DWG/DXF to 3D | ✅ Çalışır |
| Image to 3D (TripoSR) | ❌ GPU gerekli |
| Stable Diffusion | ❌ GPU gerekli |

---

## Sorun Giderme

### Build Hatası
- Logs sekmesini kontrol et
- Dockerfile syntax'ını kontrol et

### API Erişim Hatası
- CORS ayarlarını kontrol et
- VITE_API_URL değişkenini kontrol et

### Cold Start Yavaşlığı
- Free tier'da normal (30-60 sn ilk istek)
- Aktif tutmak için cron job kullanılabilir

---

## URL'ler

- **Frontend:** `https://cadlift-frontend.onrender.com`
- **Backend API:** `https://cadlift-api.onrender.com`
- **API Docs:** `https://cadlift-api.onrender.com/docs`
