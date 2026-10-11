# 🎥 District Assembly — OBS Live Overlays

**Municipality of Lopez, Quezon**

Live, editable broadcast graphics for recording the **District Assembly** presentations of 95 barangay captains and sectoral presidents in OBS. Pick a speaker from a control panel inside OBS, and every scene updates instantly with a slide-in animation: names, district, role and logo.

![Scenes](https://img.shields.io/badge/scenes-4-e8262c) ![Barangays](https://img.shields.io/badge/barangays-95-141416) ![Districts](https://img.shields.io/badge/districts-9-b0141a) ![Python](https://img.shields.io/badge/python-standard%20library-3776ab)

---

## 📁 What's inside

| File / folder | What it does |
|---|---|
| `start.bat` | **Double-click to start.** Keep its window open while recording. |
| `server.py` | Tiny local server (Python standard library only, nothing to install). |
| `control.html` | Control panel: pick who's on air, fix typos, change the event title. |
| `overlay.html` | The graphics OBS shows as Browser Sources. |
| `roster.csv` | Speaker list. Edit in Excel or Notepad. |
| `logos/` | Seals + all 95 barangay logos. |
| `fonts/` | Poppins + Inter, bundled so it works offline. |
| `push_to_github.bat` | Uploads your changes to GitHub. |

---

## 🚀 Quick start

### 1. Start the server *(every recording day)*
Double-click **`start.bat`**. A black window opens saying the server is running.

> ⚠️ **Leave that window open.** Closing it freezes the overlays on the last speaker.

### 2. Add the control panel to OBS *(one time)*
1. In OBS, go to **Docks → Custom Browser Docks…**
2. **Dock Name:** `Assembly Control` · **URL:** `http://127.0.0.1:8765/`
3. Click **Apply**, then drag the dock wherever you like.

> 💡 You can also open `http://127.0.0.1:8765/` in Chrome.

### 3. Add the overlays to your scenes *(one time)*
Add each one as **Sources → + → Browser**, **1920 × 1080**.
Untick **Shutdown source when not visible** and **Refresh browser when scene becomes active**.

> 💡 Every link is also in the control panel under **Preview & OBS links**, with **Copy** buttons.

#### 🎬 Title Card
| Source | Setting |
|---|---|
| Assembly Title | `http://127.0.0.1:8765/overlay.html?scene=title` |

#### 🎬 Presenter + Presentation *(top → bottom)*
| Source | Setting |
|---|---|
| Assembly FG 2 | `http://127.0.0.1:8765/overlay.html?scene=2&layer=fg` |
| Camera | X `1520` · Y `465` · Bounds **Cover** `360 × 480` · ✅ Crop Bounds |
| Slides | X `40` · Y `135` · Bounds **Cover** `1440 × 810` · ✅ Crop Bounds |
| Assembly BG 2 | `http://127.0.0.1:8765/overlay.html?scene=2&layer=bg` |

#### 🎬 Presenter Only
*The side card shows the presenter's name; the lower third shows only the district and barangay.*

| Source | Setting |
|---|---|
| Assembly FG 3 | `http://127.0.0.1:8765/overlay.html?scene=3&layer=fg` |
| Camera | X `40` · Y `135` · Bounds **Cover** `1440 × 810` · ✅ Crop Bounds |
| Assembly BG 3 | `http://127.0.0.1:8765/overlay.html?scene=3&layer=bg` |

#### 🎬 Presentation Only
| Source | Setting |
|---|---|
| Assembly FG 4 | `http://127.0.0.1:8765/overlay.html?scene=4&layer=fg` |
| Slides | X `40` · Y `135` · Bounds **Cover** `1600 × 900` · ✅ Crop Bounds |
| Assembly BG 4 | `http://127.0.0.1:8765/overlay.html?scene=4&layer=bg` |

> 💡 **Tip:** add Camera and Slides once, then **right-click → Copy** and **Paste (Reference)** in the other scenes.

---

## 🎛️ During recording

- **Double-click a name** in the roster, or press **Next speaker ▶**. All scenes switch at once.
- **Typo?** Click the row, fix the text, press **PUT ON AIR**. **Save to roster** makes it permanent.
- **Lower third** switch hides or shows the name bar.
- **Event settings** changes "DISTRICT ASSEMBLY" and the header lines.

---

## 📋 Roster (`roster.csv`)

| Column | Meaning |
|---|---|
| `order` | Position in the list. **Next speaker** follows this. |
| `district` | e.g. `Poblacion`. Blank = municipal-level sectoral group. |
| `kind` | `barangay` or `sector` |
| `name` | Barangay or group name |
| `person` | Presenter, e.g. `Kap. Juan Dela Cruz` |
| `role` | Blank = *Punong Barangay* / *Sectoral President* |
| `logo` | File name inside `logos/`, e.g. `gomez.png` |

After editing in Excel, save as **CSV**, then press **↻** in the control panel.

> ⚠️ Close Excel before using **Save to roster**, because Excel locks the file.

### 🗺️ Districts

| # | District | Barangays |
|:-:|---|:-:|
| 1 | Poblacion | 7 |
| 2 | Mahogany | 11 |
| 3 | Ilang-Ilang | 11 |
| 4 | Molave | 9 |
| 5 | Rosal | 10 |
| 6 | Sampaguita | 11 |
| 7 | Daisy | 11 |
| 8 | Champaca | 14 |
| 9 | Magnolia | 11 |
| | **Total** | **95** |

---

## 🖼️ Logos

| File | Used for |
|---|---|
| `logos/province_seal.png` | Province of Quezon seal (header) |
| `logos/municipal_seal.png` | Municipality of Lopez seal (header) |
| `logos/<name>.png` | Barangay / sector logos named in `roster.csv` |

Square PNGs work best (about 600 px). Missing logos show a grey placeholder.

> 💡 After replacing a seal, right-click each **BG** and **Title** source in OBS → **Refresh**.

---

## 💻 Using it on another PC

**Repo:** https://github.com/StanleyPangaruy/lopez-district-assembly

**Upload changes from this PC:** double-click `push_to_github.bat`. The first time, it may open a GitHub sign-in window.

**On the other PC** *(needs Git + Python)*:
```bat
cd %USERPROFILE%\Documents
git clone https://github.com/StanleyPangaruy/lopez-district-assembly.git "District Assembly OBS"
```
Then open the folder, double-click `start.bat`, and set up OBS as in steps 2–3.

**Get later updates:**
```bat
git pull
```

> 💡 No Git? On GitHub, click **Code → Download ZIP**, unzip it, and run `start.bat`.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---|---|
| Overlay stuck on an old name | Is the `start.bat` window still open? |
| Overlay blank in OBS | Right-click the Browser Source → **Refresh** |
| *"Port 8765 is already in use"* | The server is already running in another window. |
| *"Python was not found"* | Install from [python.org](https://www.python.org/downloads/) and tick **Add python.exe to PATH**. |
| Need to move the camera/slide boxes | Edit `LAYOUT` near the top of the script in `overlay.html`. |

---

<sub>Fonts: Poppins and Inter, SIL Open Font License.</sub>
