DISTRICT ASSEMBLY - OBS live overlays
=====================================

WHAT'S IN THIS FOLDER
  start.bat      Double-click to start the overlay server (keep its window open while recording)
  server.py      The server (Python, no extra installs needed)
  control.html   Control panel: pick who is on air, fix typos, change event title
  overlay.html   The graphics OBS shows (browser source)
  roster.csv     Your speaker list - edit in Excel or Notepad
  logos\         Put logo PNGs here
  fonts\         Poppins + Inter (bundled so it works offline)


1. START IT (every recording day)
   - Double-click start.bat. A black window opens saying the server is running.
   - Leave that window open. Closing it freezes the overlays on the last speaker.


2. ADD THE CONTROL PANEL INSIDE OBS (one time)
   - OBS menu: Docks > Custom Browser Docks...
   - Dock Name: Assembly Control     URL: http://127.0.0.1:8765/
   - Apply. Drag the dock wherever you like.
   (You can also just open http://127.0.0.1:8765/ in Chrome.)


3. ADD THE OVERLAYS TO YOUR SCENES (one time)
   Add each as: Sources > + > Browser. Width 1920, Height 1080.
   Untick "Shutdown source when not visible" and "Refresh browser when scene becomes active".
   Links are also listed in the control panel under "Preview & OBS links" with Copy buttons.

   Scene "Title Card"
     Assembly Title       http://127.0.0.1:8765/overlay.html?scene=title

   Scene "Presenter + Presentation"   (top to bottom)
     Assembly FG 2        http://127.0.0.1:8765/overlay.html?scene=2&layer=fg
     Camera               X 1520  Y 465   Bounds: Cover 360 x 480, Crop Bounds on
     Slides               X 40    Y 135   Bounds: Cover 1440 x 810, Crop Bounds on
     Assembly BG 2        http://127.0.0.1:8765/overlay.html?scene=2&layer=bg

   Scene "Presenter Only"
     Assembly FG 3        http://127.0.0.1:8765/overlay.html?scene=3&layer=fg
     Camera               X 40    Y 135   Bounds: Cover 1440 x 810, Crop Bounds on
     Assembly BG 3        http://127.0.0.1:8765/overlay.html?scene=3&layer=bg

   Scene "Presentation Only"
     Assembly FG 4        http://127.0.0.1:8765/overlay.html?scene=4&layer=fg
     Slides               X 40    Y 135   Bounds: Cover 1600 x 900, Crop Bounds on
     Assembly BG 4        http://127.0.0.1:8765/overlay.html?scene=4&layer=bg

   Tip: add Camera and Slides once, then use right-click > Copy, and
   "Paste (Reference)" in the other scenes.


4. DURING RECORDING
   - Double-click a name in the roster (or press "Next speaker") -> every scene updates,
     with a slide-in animation.
   - Typo? Click the row, fix the text, press PUT ON AIR. "Save to roster" makes it permanent.
   - "Lower third" switch hides/shows the name bar.
   - Event settings: change "DISTRICT ASSEMBLY", header lines, card note.


5. ROSTER (roster.csv)
   Columns: order, district, kind, name, person, role, logo
     kind      barangay  or  sector
     district  Poblacion, etc. Leave blank for municipal-level sectoral groups.
     role      blank = "Punong Barangay" / "Sectoral President"
     logo      file name inside the logos folder, e.g. gomez.png
   After editing in Excel: save as CSV, then press the refresh button in the panel.
   Close Excel before using "Save to roster" (Excel locks the file).


6. LOGOS
   logos\province_seal.png     Province of Quezon seal (header)
   logos\municipal_seal.png    Municipality of Lopez seal (header)
   logos\<anything>.png        Barangay / sector logos named in roster.csv
   Square PNGs work best. Missing logos show a grey placeholder.


IF SOMETHING LOOKS WRONG
   - Overlay stuck on an old name: is the start.bat window still open?
   - Overlay blank in OBS: right-click the browser source > Refresh.
   - "Port 8765 is already in use": the server is already running in another window.
   - Layout positions are in overlay.html (LAYOUT) if you ever change the camera/slide boxes.

Fonts: Poppins and Inter, SIL Open Font License (free to use).

USING IT ON ANOTHER PC (GitHub)
   Repo: https://github.com/StanleyPangaruy/lopez-district-assembly

   Upload changes from this PC:  double-click push_to_github.bat
   (first time it may open a GitHub sign-in window)

   On the other PC (needs Git + Python installed):
     1. Open Command Prompt in Documents and run:
          git clone https://github.com/StanleyPangaruy/lopez-district-assembly.git "District Assembly OBS"
     2. Open the folder, double-click start.bat, then set up OBS as in steps 2-3 above.
     3. To get later updates:  open Command Prompt in the folder and run   git pull
   (No Git? On GitHub click Code > Download ZIP, unzip, and run start.bat.)
