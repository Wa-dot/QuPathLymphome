# QuPathLymphoma
An Add-on for QuPath to analyze Lymphoma with AI

## Requirements and Installation

### 0- QuPath
You can find QuPath 0.5.1 for [Windows](https://github.com/qupath/qupath/releases/download/v0.5.1/QuPath-v0.5.1-Windows.msi) or [Mac (M1/M2)](https://github.com/qupath/qupath/releases/download/v0.5.1/QuPath-v0.5.1-Mac-x64.pkg). For more information or other architectures, visit [here](https://qupath.github.io/).  
*Sometimes antivirus software may react. Click "more info" and then execute, or launch the installer in administrator mode.*

### 1- Python
You need Python 3 installed. You can find it here: [macOS 64-bit universal](https://www.python.org/ftp/python/3.11.3/python-3.11.3-macos11.pkg) or [Windows installer (64-bit)](https://www.python.org/ftp/python/3.11.3/python-3.11.3-amd64.exe).  
For more information, visit the [Python 3.11 page](https://www.python.org/downloads/release/python-3113/). *Don't forget to activate the environment PATH!*

### 2- Environment
Now that Python is installed, you need to prepare the work environment. To do this, execute the script **setup_windows** for Windows or **setup_linuxMac** for other OS. This will take a few minutes.

## Usage
1. Launch QuPath.
2. Import your image (you can also create a project or import a project with an image).
3. Create an annotation.   
   <img src="assetReadme/imageAnnotationMenu.png" alt="Image annotation menu" width="350"/>  
   <img src="assetReadme/imageAnnotation.png" alt="Image annotation in picture" width="350"/>

4. Rename annotations (annotation names must be unique): Annotations > Right-click > Set properties > Name.  
   <img src="assetReadme/renameAnnotation.png" alt="Rename annotation" width="450"/>

5. Select all your annotations.
6. Go to Automate > Script editor.
7. Import the Groovy file (C:\Users\user\[directory]\QuPathLymphoma\groovyFile).
8. Run the script.
9. Select your working file (the default is the project folder named QuPathLymphoma).
10. Wait for file creation and model execution. The execution time will depend on the model.

## Project Structure
Base project:
```
QuPathLymphoma/
│
├── .git/
├── assetReadme/                    # Images for README file             
├── groovyFile/             
│   └── script.groovy               # Groovy file to launch Python project
├── blendmaps2/
│   ├── libraries/
│   │   ├── asset                   # Styles
│   │   ├── models                  # Our model repository
│   │   │   └── generateDatas.py    # Our model (generates random data)
│   │   ├── get_datas.py            # Function to get data from JSON
│   │   └── layout_dashboard.py     # Layout for web app
│   └── launchApp.py                # Main script
├── pythonEnv/                      # Virtual environment directory (ignored by git)                
│   ├── Scripts/                    # Python + control environment
│   └── ...
├── requirements.txt                
├── .gitignore                      
├── setup_windows.bat               # Install Windows Python environment and requirements
├── setup_linuxMac.sh               # Install Mac and Linux Python environment and requirements
└── LICENSE
```

## JSON
The JSON created by the Groovy file will have this format:
```json
{
  "type": "Feature",
  "id": "86ec32e2-44e1-4222-99ea-6b02cc8c18fc",
  "geometry": {
    "type": "Polygon",
    "coordinates": [
      [
        [35561, 7252],
        [36292, 7252],
        [36292, 7740],
        [35561, 7740],
        [35561, 7252]
      ]
    ]
  },
  "properties": {
    "objectType": "annotation",
    "name": "Annotation 1"
  }
}
```

**Output format**
```json
{
  "wsi_id": "012B HES",
  "tiles": [
    {
      "annotation_id": "86ec32e2-44e1-4222-99ea-6b02cc8c18fc",
      "tile_id": "tile_0_0",
      "x": 0,
      "y": 0,
      "xmin": 35561,
      "xmax": 35611,
      "ymin": 7252,
      "ymax": 7302,
      "lymphoma_probability": 0.2840892066628261
    },
    {
      "annotation_id": "86ec32e2-44e1-4222-99ea-6b02cc8c18fc",
      "tile_id": "tile_1_0",
      "x": 1,
      "y": 0,
      "xmin": 35611,
      "xmax": 35661,
      "ymin": 7252,
      "ymax": 7302,
      "lymphoma_probability": 0.31737318473047416
    }
  ]
}
```

The program currently only accepts this format.

## Common Issues
- Sometimes the annotations are not selected correctly. Retry selecting them if the script doesn't work.
- Occasionally, a window may hide an action window. Minimize it to access the second (there are 2 action windows).
- Displaying tiles only works after data creation, so after running the Python script (you can't access the executed data beforehand).