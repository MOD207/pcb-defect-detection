# PCB Defect Detector

A web application that automatically detects manufacturing defects on printed circuit boards (PCBs) from an uploaded image, built as a Spacelink Co internship project.

## What it does

Upload a photo of a PCB and the app will:
- Run it through a trained YOLOv8 object detection model
- Return the image annotated with bounding boxes around any detected defects
- Log the inspection (image, timestamp, defects found) to a database
- Let you browse a history of all past inspections

The model detects six defect types: **missing hole, mouse bite, open circuit, short, spur, and spurious copper.**

## How it works

1. **Classical CV baseline** — an initial approach using OpenCV image differencing (comparing a test board against a clean reference board) to establish a baseline before introducing machine learning.
2. **YOLOv8 model** — trained on the PKU-Market-PCB dataset (693 images, 6 defect classes) to detect and classify defects directly from a single image, without needing a reference board.
3. **Flask web app** — a simple interface for uploading an image and viewing results, backed by a MySQL database for inspection history.

## Project structure

```
pcb_webapp/
  app.py                 # Flask application (routes, model inference, DB logging)
  best.pt                 # trained YOLOv8 model weights
  static/
    style.css             # app styling
    uploads/               # uploaded images and annotated results
  templates/
    index.html             # upload page
    result.html             # detection result page
    history.html            # inspection history page
```

## Requirements

- Python 3.10+
- MySQL / MariaDB (e.g. via XAMPP)
- Python packages: `flask`, `ultralytics`, `opencv-python`, `mysql-connector-python`

Install packages:
```bash
pip install flask ultralytics opencv-python mysql-connector-python
```

## Database setup

Create a database named `pcb_inspection` with two tables:

```sql
CREATE TABLE inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_filename VARCHAR(255),
    result_filename VARCHAR(255),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE detections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id INT,
    defect_class VARCHAR(50),
    confidence FLOAT,
    FOREIGN KEY (inspection_id) REFERENCES inspections(id)
);
```

Update the database connection details (host, port, user, password) in  a new `.env` file to match your local MySQL setup.

## Running the app

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

- **Home page** — upload a PCB image to run an inspection
- **Result page** — view the annotated image and list of detected defects
- **History page** (`/history`) — browse all past inspections

## Model performance

Trained on the PKU-Market-PCB dataset (70/20/10 train/val/test split), the model reaches:
- **Test set mAP50: 0.942**
- **Test set mAP50-95: 0.512**

Per-class performance is strongest on missing hole, open circuit, and short, and comparatively weaker (though still solid) on spur, which is the most visually subtle defect type.

## Known limitations

- The model is trained on a relatively small, narrow dataset (12 unique board layouts). It performs very well on images similar to the training data, but does not generalize reliably to PCB photos from different sources, lighting conditions, or board designs — testing on an unrelated real-world photo produced a noticeable number of false positives, mostly `missing_hole` detections on ordinary through-holes and connectors.
- Production use would require training on a larger, more diverse dataset, ideally including real photos of the target hardware under actual inspection conditions.

## Project background

Built over a 20-day internship plan: starting with a classical computer vision baseline, progressing to a trained YOLOv8 model, and finishing with a web interface and database logging for practical use.