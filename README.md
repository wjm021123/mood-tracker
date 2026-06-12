# 🌤️Mood Tracker😊
Mood Tracker is a personal mood and lifestyle tracking app built with Streamlit. 

It helps users record:
- Mood, focus level, irritability, and depression
- Sleep patterns
- Environmental conditions including weather and air quality
- Lifestyle factors, such as exercise and outdoor activity
- and Free-text daily journals.

The app also generates statistics, enabling users to explore the dynamics between mood and environmental factors over time.

This document will guide you through the installation process. 

## 1. Install Python 3 
This app requires python to run. Please install python before proceeding.

You can skip this section if Python is already installed on your device. 

### [Windows]
(1) Download the Python installation Manager from the official website: https://www.python.org/downloads/    
- press the Yellow "Download Python 3.xx" Button. 
- Follow the instruction provided by the installation manager. 
(2) Run the installation manager.    
(3) Follow the installation steps.    
- The detail of the installation process may vary depending on the device. 
- Make sure to check **'Add Python to PATH'**. (Answer 'y' if prompted.)
(4) Finish installation.    

You can verify installation by using the PowerShell/Terminal app and type the following prompt:
```python
python --version 
```
or
```python
pip --version
```

### [macOS]
Python is usually preinstalled. 

you can verify installation in Terminal by typing the following prompt:
```python
python3 --version
```

## 2. Launch the App
Download and unzip the folder. 
Please keep all files inside the same folder. 

Example:
```text
Mood Tracker/
├ app.py
├ Run_MoodTracker
├ Run_MoodTracker.bat
├ requirements.txt
├ translations.csv
├ settings.json
└ fonts/
```

### [Windows]
Double-click `Run_MoodTracker.bat` file. 
The file extension (`.bat`) may be hidden depending on your system settings. 

### [macOS]
Double-click `Mood Tracker.app`
The file extension (`.app`) may be hidden depending on your system settings. 

### Closing the app
Closing the browser without clicking the Exit App button usually does not cause problems, but for more stable operation we recommend closing the app using the **Exit App** button.
If only the browser window is closed, the app may continue running in the background.

## 3. Customization (Optional)
These steps are completely optional, but they can make the app feel more polished and easier to access.

### [Windows]
(1) create shortcut for `Run_MoodTracker.bat`   
- The shortcut can be place anywhere on your device.
- Do not move the actual files out of the folder.  
(2) Right-click, and open **Properties**    
(3) Select **Change Icon**    
(4) Select **logo.ico** from the folder you downloaded.     

### [macOS]
If the app icon is missing or reset, or you want to make an Alias:
(1) Locate `logo.png` (or another icon image)   
(2) Open the image in Preview   
(3) Press `⌘ + A`, then `⌘ + C`    
(4) Right-click `Mood Tracker.app` → **Get Info**    
(5) Click the small icon in the top-left corner    
(6) Press `⌘ + V`    

Your custom icon should now appear in Finder and Launchpad.

### Settings
In the Settings section of the app, you can customize:
- Language
- Default sleep schedule
- Region/location
- Default journal text

Settings are automatically stored in the `settings.json` file. 

## 4. Troubleshooting
(1)App does not launch     
Reboot the computer.
Make sure you use the **Exit app** button before closing the browser. 

(2) Weather data could not be loaded    
This may happen temporarily due to network issues or server load.
Please try again later or use manual weather input.

(3) Settings are not saved    
Make sure the downloaded folder has write permission.
Do not move individual files outside the Release folder.

