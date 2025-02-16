# InstaUnliker
Instagram Unliker tool with some added features:
 - Added GUI
 - Added ability to run from executable file for Windows and Linux
 - Added Ability to repeat chunks of unliking with a custome delay between them

## Instructions to run script 🐍
1. Install dependencies
 - ``pip install -r requirements.txt`` 
  - May need to install tkinter seperatly: ``sudo apt-get install python3-tk``
2. Run script
 - ```python main.py```

## Instructions to compile for Windows 🪟
```pyinstaller --onefile --windowed --hidden-import instagrapi.exceptions --hidden-import tkinter --hidden-import colorsys --icon=instaul2.ico main.py```

## Instructions to compile for Linux (AppImage) 🐧
1. Install appimagetool
 - Install AppImage: 
  - ```wget https://github.com/AppImage/AppImageKit/releases/latest/download/appimagetool-x86_64.AppImage```

 - Set permissions to execute:
  - ```chmod +x appimagetool-x86_64.AppImage```

 - Add to bin directory:
  - ```sudo mv appimagetool-x86_64.AppImage /usr/local/bin/appimagetool```

 - Check to make sure its installed: 
  - ```appimagetool --version```

2. Compile binary:
```
    pyinstaller --onefile --windowed \
  --hidden-import instagrapi.exceptions \
  --hidden-import tkinter \
  --hidden-import colorsys \
  --collect-submodules instagrapi \
  --icon=instaul2.ico main.py
```

3. Set up AppDir:
 - Create the directories:
  - ```mkdir -p AppDir/usr/bin```
  - ```mkdir -p AppDir/usr/share/applications```

 - Copy the binary over:
  - ```cp dist/* AppDir/usr/bin/InstagramUnliker```
  - ```chmod +x AppDir/usr/bin/InstagramUnliker```

 - Add AppRun file:
  - ```printf '#!/bin/bash\nDIR="$(dirname "$(readlink -f "$0")")"\nexec "$DIR/usr/bin/InstagramUnliker" "$@"' >> AppDir/AppRun```
  - ```chmod +x AppDir/AppRun```
    
 - Add instagram.desktop:
  - ```printf '[Desktop Entry]\nName=InstagramUnliker\nExec=InstagramUnliker\nIcon=app\nType=Application\nCategories=Utility;' >> AppDir/instagram-unliker.desktop```
  - ```cp AppDir/instagram-unliker.desktop AppDir/usr/share/applications```

4. Compile (x86):
    ```ARCH=x86_64 appimagetool AppDir InstagramUnliker.AppImage```
    ```chmod +x InstagramUnliker.AppImage```



## 🚨 Important 🚨
Make sure to not unlike a large amount of photos in a short period of time. Not sure how the automation detection works but Instagram will lock/limit your account in the event that you are somehow flagged. I suggest rerunning the script once every day or so.
