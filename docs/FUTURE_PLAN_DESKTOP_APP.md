# 🚀 CADLift Desktop App - Future Plan

**Status:** Planning  
**Priority:** Post-MVP  
**Estimated Effort:** 2-3 weeks  
**Target:** One-click installer for Windows, macOS, Linux

---

## 📋 Executive Summary

Transform CADLift from a developer-setup project into a **consumer-ready desktop application** with:
- Professional installer (setup.exe / .dmg / .deb)
- Beautiful first-run onboarding wizard
- Intelligent model download manager
- System auto-detection & recommendations

---

## 🎯 Goals

1. **Zero technical knowledge required** to install and use CADLift
2. **Cross-platform support** (Windows, macOS, Linux)
3. **Smart defaults** based on user's hardware
4. **Offline-capable** after initial download
5. **Professional appearance** matching commercial software

---

## 🏗️ Architecture

### Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CADLift Desktop                          │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────┐  ┌───────────────────────────────┐  │
│  │   Electron Shell  │  │    React Frontend             │  │
│  │   - Window mgmt   │  │    - Main app UI              │  │
│  │   - System tray   │  │    - Onboarding wizard        │  │
│  │   - Auto-updates  │  │    - Download manager UI      │  │
│  └─────────┬─────────┘  └───────────────┬───────────────┘  │
│            │                            │                   │
│            │         HTTP API           │                   │
│            │      (localhost:8000)      │                   │
│            │                            │                   │
│  ┌─────────▼────────────────────────────▼───────────────┐  │
│  │              Python Backend (FastAPI)                 │  │
│  │  - All existing CADLift code                         │  │
│  │  - Bundled via PyInstaller                           │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              AI Models (Downloaded on demand)         │  │
│  │  - Stable Diffusion v1.5 (~4GB)                      │  │
│  │  - TripoSR (~1.5GB)                                  │  │
│  │  - Stored in AppData/Local                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### File Structure

```
cadlift-desktop/
├── electron/
│   ├── main.js              # Electron main process
│   ├── preload.js           # Bridge to renderer
│   ├── backend-manager.js   # Spawns/manages Python backend
│   ├── download-manager.js  # Model download with progress
│   └── system-detector.js   # GPU/RAM/disk detection
│
├── src/                     # React frontend
│   ├── App.tsx
│   ├── pages/
│   │   ├── Onboarding/
│   │   │   ├── Welcome.tsx
│   │   │   ├── SystemScan.tsx
│   │   │   ├── ModelSelection.tsx
│   │   │   ├── APIKeys.tsx
│   │   │   ├── Download.tsx
│   │   │   └── Complete.tsx
│   │   └── Main/            # Existing CADLift UI
│   └── components/
│       └── DownloadProgress.tsx
│
├── backend/                 # Existing Python backend
│   └── (bundled with PyInstaller)
│
├── assets/
│   ├── icon.ico             # Windows icon
│   ├── icon.icns            # macOS icon
│   └── icon.png             # Linux icon
│
├── build/
│   ├── installer.nsh        # NSIS customization
│   └── entitlements.mac.plist
│
├── package.json
└── electron-builder.yml
```

---

## 📱 User Experience Flow

### Phase 1: Download & Install (~1 min)

```
User downloads:  CADLift-Setup-1.0.0.exe  (~80-100MB)
                 ├── Electron runtime
                 ├── React UI
                 ├── Python backend (bundled)
                 └── Download manager

Windows Installer:
  → UAC prompt
  → Install to C:\Program Files\CADLift
  → Create Start Menu shortcut
  → Create Desktop shortcut (optional)
  → Register uninstaller
  → ~30 seconds total
```

### Phase 2: First Launch - Onboarding Wizard

#### Screen 1: Welcome
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              🎨 Welcome to CADLift                      │
│                                                         │
│     Transform your ideas into 3D CAD models with AI    │
│                                                         │
│     ┌─────────────────────────────────────────────┐    │
│     │                                             │    │
│     │         [Beautiful hero illustration]       │    │
│     │                                             │    │
│     └─────────────────────────────────────────────┘    │
│                                                         │
│                   [ Get Started → ]                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Screen 2: System Scan
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              🔍 Analyzing Your System                   │
│                                                         │
│     ┌─────────────────────────────────────────────┐    │
│     │  GPU:    NVIDIA GeForce RTX 3050 Ti    ✓   │    │
│     │  VRAM:   4 GB                          ⚠   │    │
│     │  RAM:    16 GB                         ✓   │    │
│     │  Disk:   52 GB available               ✓   │    │
│     │  CUDA:   12.1 installed                ✓   │    │
│     └─────────────────────────────────────────────┘    │
│                                                         │
│     💡 Recommendation:                                  │
│     "Your GPU has limited VRAM. We recommend using     │
│      optimized settings for best performance."          │
│                                                         │
│         [ ← Back ]              [ Continue → ]          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Screen 3: Model Selection
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              📦 Choose Your Setup                       │
│                                                         │
│     ┌─────────────────────────────────────────────┐    │
│     │  ● Recommended Setup               ~5.5 GB  │    │
│     │    Best for your hardware                   │    │
│     │    ├─ ☑ Stable Diffusion (Low-Res)   3.8GB │    │
│     │    ├─ ☑ TripoSR                      1.5GB │    │
│     │    └─ ☑ Parametric CAD Engine        0.2GB │    │
│     └─────────────────────────────────────────────┘    │
│     ┌─────────────────────────────────────────────┐    │
│     │  ○ Cloud Mode (API Keys)           ~200 MB  │    │
│     │    No GPU required, uses cloud services     │    │
│     └─────────────────────────────────────────────┘    │
│     ┌─────────────────────────────────────────────┐    │
│     │  ○ Custom                                   │    │
│     │    Choose individual components             │    │
│     └─────────────────────────────────────────────┘    │
│                                                         │
│         [ ← Back ]              [ Download → ]          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Screen 4: Download Progress
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              ⬇️ Downloading Models                      │
│                                                         │
│     Stable Diffusion v1.5                              │
│     ████████████████████░░░░░░░░  68%                  │
│     2.6 GB / 3.8 GB  •  15 MB/s  •  1:23 remaining     │
│                                                         │
│     TripoSR                                [Queued]    │
│     ░░░░░░░░░░░░░░░░░░░░░░░░░░░░   0%                  │
│     0 / 1.5 GB                                         │
│                                                         │
│     ─────────────────────────────────────────────      │
│     Total: 2.6 GB / 5.3 GB                            │
│     Estimated time: 3 minutes                          │
│                                                         │
│         [ Pause ]    [ Run in Background ]             │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

#### Screen 5: Complete
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              ✅ You're All Set!                         │
│                                                         │
│     ┌─────────────────────────────────────────────┐    │
│     │                                             │    │
│     │         [Success animation/confetti]        │    │
│     │                                             │    │
│     └─────────────────────────────────────────────┘    │
│                                                         │
│     CADLift is ready to transform your ideas           │
│     into professional 3D CAD models.                   │
│                                                         │
│     ☑ Create desktop shortcut                          │
│     ☑ Start CADLift when Windows starts                │
│                                                         │
│                   [ 🚀 Launch CADLift ]                 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technical Implementation

### Tech Stack

| Component | Technology | Reason |
|-----------|------------|--------|
| Desktop Shell | Electron 28+ | Cross-platform, mature ecosystem |
| UI Framework | React + Vite | Matches existing CADLift frontend |
| Styling | TailwindCSS or CSS Modules | Modern, responsive |
| Backend | Python + FastAPI | Existing CADLift backend |
| Python Bundler | PyInstaller | Single .exe, includes dependencies |
| Installer | electron-builder | Auto-generates NSIS/DMG/DEB |
| Download Manager | Node.js (got/axios) | Resumable, progress events |
| Auto-Update | electron-updater | GitHub Releases integration |

### System Detection (Node.js)

```javascript
// system-detector.js
const si = require('systeminformation');

async function detectSystem() {
  const [gpu, mem, disk, os] = await Promise.all([
    si.graphics(),
    si.mem(),
    si.diskLayout(),
    si.osInfo()
  ]);

  const nvidia = gpu.controllers.find(g => g.vendor.includes('NVIDIA'));
  
  return {
    gpu: nvidia ? {
      name: nvidia.model,
      vram: nvidia.vram,
      cuda: await checkCudaVersion()
    } : null,
    ram: Math.round(mem.total / 1024 / 1024 / 1024),
    diskFree: Math.round(disk[0].size / 1024 / 1024 / 1024),
    os: os.platform
  };
}

function getRecommendation(system) {
  if (!system.gpu) {
    return { mode: 'cloud', reason: 'No GPU detected' };
  }
  if (system.gpu.vram < 4) {
    return { mode: 'cloud', reason: 'Low VRAM' };
  }
  if (system.gpu.vram < 8) {
    return { mode: 'optimized', reason: 'Limited VRAM, using optimized settings' };
  }
  return { mode: 'full', reason: 'Powerful GPU detected' };
}
```

### Download Manager

```javascript
// download-manager.js
const got = require('got');
const fs = require('fs');
const path = require('path');

class DownloadManager {
  constructor(modelsDir) {
    this.modelsDir = modelsDir;
    this.downloads = new Map();
  }

  async downloadModel(modelId, url, onProgress) {
    const destPath = path.join(this.modelsDir, modelId);
    const tempPath = destPath + '.download';
    
    // Check for partial download (resume support)
    let startByte = 0;
    if (fs.existsSync(tempPath)) {
      startByte = fs.statSync(tempPath).size;
    }

    const options = startByte > 0 
      ? { headers: { Range: `bytes=${startByte}-` } }
      : {};

    const stream = got.stream(url, options);
    
    stream.on('downloadProgress', ({ transferred, total, percent }) => {
      onProgress({
        modelId,
        downloaded: startByte + transferred,
        total: startByte + total,
        percent: Math.round(percent * 100),
        speed: stream.downloadSpeed
      });
    });

    const writeStream = fs.createWriteStream(tempPath, { flags: 'a' });
    stream.pipe(writeStream);

    return new Promise((resolve, reject) => {
      writeStream.on('finish', () => {
        fs.renameSync(tempPath, destPath);
        resolve(destPath);
      });
      stream.on('error', reject);
    });
  }

  pause(modelId) {
    // Implementation: abort stream, keep partial file
  }

  resume(modelId) {
    // Implementation: restart with Range header
  }
}
```

### Backend Manager

```javascript
// backend-manager.js
const { spawn } = require('child_process');
const path = require('path');
const http = require('http');

class BackendManager {
  constructor() {
    this.process = null;
    this.port = 8000;
  }

  async start() {
    const backendPath = path.join(__dirname, '../backend/cadlift-backend.exe');
    
    this.process = spawn(backendPath, [], {
      env: { ...process.env, PORT: this.port }
    });

    this.process.stdout.on('data', (data) => {
      console.log(`Backend: ${data}`);
    });

    // Wait for health check
    await this.waitForReady();
  }

  async waitForReady(timeout = 30000) {
    const start = Date.now();
    while (Date.now() - start < timeout) {
      try {
        await this.healthCheck();
        return true;
      } catch {
        await new Promise(r => setTimeout(r, 500));
      }
    }
    throw new Error('Backend failed to start');
  }

  healthCheck() {
    return new Promise((resolve, reject) => {
      http.get(`http://localhost:${this.port}/health`, (res) => {
        res.statusCode === 200 ? resolve() : reject();
      }).on('error', reject);
    });
  }

  stop() {
    if (this.process) {
      this.process.kill();
      this.process = null;
    }
  }
}
```

---

## 📦 Build & Distribution

### electron-builder.yml

```yaml
appId: com.cadlift.desktop
productName: CADLift
directories:
  output: dist
  buildResources: assets

files:
  - "**/*"
  - "!backend/**/*.py"  # Exclude source, use bundled .exe

extraResources:
  - from: "backend/dist/cadlift-backend/"
    to: "backend"

win:
  target:
    - target: nsis
      arch: [x64]
  icon: assets/icon.ico
  
nsis:
  oneClick: false
  allowToChangeInstallationDirectory: true
  createDesktopShortcut: true
  createStartMenuShortcut: true
  installerIcon: assets/icon.ico
  uninstallerIcon: assets/icon.ico
  
mac:
  target: [dmg, zip]
  icon: assets/icon.icns
  category: public.app-category.graphics-design
  
linux:
  target: [AppImage, deb]
  icon: assets/icon.png
  category: Graphics
```

### Build Commands

```bash
# Bundle Python backend first
cd backend
pyinstaller --onedir --name cadlift-backend app/main.py

# Build Electron app
cd ..
npm run build
npx electron-builder --win --mac --linux
```

### Output

```
dist/
├── CADLift-Setup-1.0.0.exe      # Windows NSIS installer
├── CADLift-1.0.0.dmg            # macOS disk image
├── CADLift-1.0.0.AppImage       # Linux portable
└── CADLift-1.0.0.deb            # Debian/Ubuntu package
```

---

## 🔄 Auto-Update System

### GitHub Releases Integration

```javascript
// In main.js
const { autoUpdater } = require('electron-updater');

autoUpdater.checkForUpdatesAndNotify();

autoUpdater.on('update-available', () => {
  // Show notification to user
});

autoUpdater.on('update-downloaded', () => {
  // Prompt user to restart
});
```

### Update Flow

1. App checks GitHub Releases on startup
2. If update available, show notification
3. Download in background
4. Prompt to install when ready
5. Restart and apply update

---

## 📅 Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up Electron project structure
- [ ] Bundle Python backend with PyInstaller
- [ ] Create basic Electron shell (window, tray icon)
- [ ] Implement backend process spawning
- [ ] Create simple "loading" screen

### Phase 2: Onboarding Wizard (Week 1-2)
- [ ] Design onboarding UI mockups
- [ ] Implement system detection
- [ ] Build Welcome screen
- [ ] Build System Scan screen
- [ ] Build Model Selection screen
- [ ] Build API Keys screen (optional)

### Phase 3: Download Manager (Week 2)
- [ ] Implement download core (resumable)
- [ ] Build download progress UI
- [ ] Add pause/resume functionality
- [ ] Add checksum verification
- [ ] Handle download errors gracefully

### Phase 4: Integration (Week 2-3)
- [ ] Connect to existing CADLift frontend
- [ ] Implement first-run detection
- [ ] Store user preferences
- [ ] Create settings page for model management

### Phase 5: Packaging (Week 3)
- [ ] Configure electron-builder
- [ ] Build Windows installer (NSIS)
- [ ] Build macOS installer (DMG)
- [ ] Build Linux packages (AppImage, DEB)
- [ ] Test on all platforms

### Phase 6: Polish (Week 3)
- [ ] Add auto-update system
- [ ] Add crash reporting
- [ ] Add analytics (opt-in)
- [ ] Create installer graphics/branding
- [ ] Write user documentation

---

## 🎨 Design Guidelines

### Color Palette
- Primary: `#6366f1` (Indigo)
- Background: `#0f172a` (Dark slate)
- Surface: `#1e293b`
- Success: `#22c55e`
- Warning: `#f59e0b`
- Error: `#ef4444`

### Typography
- Headings: Inter Bold
- Body: Inter Regular
- Monospace: JetBrains Mono

### Animations
- Page transitions: 300ms ease-out
- Progress bars: Smooth, no janky updates
- Success state: Subtle confetti or checkmark animation

---

## 📊 Success Metrics

| Metric | Target |
|--------|--------|
| Install success rate | >95% |
| First-run completion | >90% |
| Average setup time | <10 minutes |
| Crash-free sessions | >99% |
| User satisfaction | 4.5+/5 stars |

---

## 🔮 Future Enhancements

1. **Silent/Enterprise Install** - MSI with Group Policy support
2. **Portable Mode** - Run from USB without install
3. **Model Marketplace** - Download additional models
4. **Cloud Sync** - Sync projects across devices
5. **Plugin System** - Third-party extensions
6. **GPU Benchmark** - Built-in performance test
7. **Tutorial Mode** - Interactive first-project walkthrough

---

*Document created: 2025-12-09*
*Last updated: 2025-12-09*
