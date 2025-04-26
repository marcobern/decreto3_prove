# Decreto3 Eolico

## Prerequisite
### 1. Create virtual environment
```
python -m venv venv
```
### 2. Activate the virtual environment
for Linux and MacOS:
```
source venv/bin/activate
```
for Windows:
```
venv\Scripts\activate
```
### 3. Install poetry
```
pip install poetry
```
### 4. Install dependencies
```
poetry install
```

## Generate desktop app

- MacOS
```
pyinstaller --onefile --windowed --name "Decreto3Eolico" --icon=assets/icon/icon.icns decreto3_eolico.py
```

- Windows
```
pyinstaller --onefile --windowed --name "Decreto3Eolico" --icon=assets/icon/icon.ico decreto3_eolico.py
```
