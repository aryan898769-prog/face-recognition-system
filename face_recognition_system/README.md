# Face Recognition Security System

A Python-based project scaffold for an employee face recognition and access control system.

## Components

- `database.py`: stores employee names, IDs, and allowed areas
- `train.py`: encodes employee faces using a pretrained recognition model
- `recognize.py`: identifies faces from a camera with the pretrained model and logs timestamped entries
- `access_control.py`: validates area access and notifies admins on violations
- `requirements.txt`: Python dependencies

## Setup

```bash
cd face_recognition_system
python -m venv venv
# Windows
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

1. Use the web interface to register employees and upload face images:

```bash
python app/webapp.py
```

2. Open `http://127.0.0.1:5000` in your browser.
3. Add employee name, ID, allowed area, and face images.
4. Train encodings:

```bash
python app/train.py
```

5. Run recognition:

```bash
python app/recognize.py <AreaName>
```

`recognize.py` will log detections in `access_log.csv` and notify the admin on area violations.
