# AI-Powered Smart Traffic Management System

An AI-powered traffic monitoring and analysis system built with **Python, YOLO, OpenCV, ByteTrack, and Streamlit**. The system detects, tracks, and counts vehicles in traffic videos and generates analytical reports through an interactive dashboard.

## Project Overview

The AI-Powered Smart Traffic Management System uses computer vision and deep learning techniques to monitor road traffic automatically.

It processes traffic videos, detects vehicles, assigns tracking IDs, counts vehicles crossing a virtual line, and generates traffic analytics. The Streamlit dashboard provides a user-friendly interface to upload videos, run traffic analysis, and view results.

The project aims to demonstrate how Artificial Intelligence and Computer Vision can support intelligent traffic monitoring and data-driven traffic management.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| YOLO11 | Vehicle detection |
| OpenCV | Video processing and image analysis |
| ByteTrack | Multi-object tracking |
| NumPy | Numerical operations |
| Pandas | Data processing and reporting |
| Matplotlib | Data visualization |
| Plotly | Interactive charts |
| Streamlit | Interactive web dashboard |
| CSV | Traffic report storage |

## Key Features

### 1. Vehicle Detection
- Detects vehicles in traffic videos using YOLO11.
- Supports common road vehicle classes:
  - Cars
  - Motorcycles
  - Buses
  - Trucks

### 2. Vehicle Tracking
- Uses ByteTrack for multi-object tracking.
- Assigns unique IDs to detected vehicles.
- Maintains vehicle identities across video frames where tracking is successful.

### 3. Vehicle Counting
- Uses a virtual counting line to detect vehicle movement.
- Counts vehicles crossing the line.
- Maintains separate counts for different vehicle categories.

### 4. Traffic Analytics
- Calculates total vehicle counts.
- Analyzes vehicle categories.
- Estimates traffic flow.
- Calculates average visible vehicle count.
- Classifies traffic status as Low, Moderate, or Heavy based on configured thresholds.

### 5. Interactive Streamlit Dashboard
- Upload different traffic videos.
- Run backend traffic analysis from the dashboard.
- View vehicle statistics and traffic analytics.
- Explore interactive charts.
- View and download CSV reports.

## Project Structure

```text
AI-Traffic-Management-System/
│
├── dataset/
│   ├── traffic_videos/
│   ├── images/
│   └── kaggle_dataset/
│
├── models/
│
├── outputs/
│   ├── processed_videos/
│   └── reports/
│
├── src/
│   ├── utils/
│   ├── video_reader.py
│   ├── detection.py
│   ├── tracking.py
│   ├── counting.py
│   └── analytics.py
│
├── notebooks/
│
├── app.py
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Installation and Setup

### Prerequisites

- Python 3.12 or compatible version
- Git
- Visual Studio Code (recommended)

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Traffic-Management-System.git
```

### Step 2: Open the Project Folder

```bash
cd AI-Traffic-Management-System
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

### Step 4: Activate the Virtual Environment

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## How to Run the Project

### Run the Streamlit Dashboard

Start the dashboard using:

```bash
python -m streamlit run app.py
```

Open the local dashboard in your browser:

```text
http://localhost:8501
```

### Run Traffic Analysis Directly

You can also run the vehicle counting backend from the terminal:

```bash
python src/counting.py --video dataset/traffic_videos/traffic.mp4 --no-display
```

Replace the video path with your own video file.

## Dashboard Screenshots

Add screenshots of your working dashboard in a folder named `screenshots`.

For example:

```text
screenshots/
├── dashboard-overview.png
├── vehicle-analytics.png
└── traffic-analytics.png
```

Display them in this section:

### Dashboard Overview

![Dashboard Overview](screenshots/dashboard-overview.png)

### Vehicle Analytics

![Vehicle Analytics](screenshots/vehicle-analytics.png)

### Traffic Analytics

![Traffic Analytics](screenshots/traffic-analytics.png)

*Replace these image paths with your actual screenshots.*

## Output and Reports

The system generates traffic reports in CSV format.

Default report location:

```text
outputs/reports/traffic_report.csv
```

The report contains information such as:

- Total vehicles detected
- Vehicle counts by category
- Traffic flow
- Average visible vehicles
- Traffic status
- Report date and time

## Future Improvements

The following features can be added in future versions:

- Real-time traffic monitoring using CCTV cameras.
- Traffic congestion prediction using Machine Learning.
- Automatic traffic signal control.
- Emergency vehicle detection and priority management.
- Multiple camera integration.
- Vehicle speed estimation.
- Number plate recognition (ANPR).
- Historical traffic analysis and reporting.
- Cloud-based traffic monitoring.

## Project Limitations

- Detection accuracy depends on video quality, lighting, camera angle, and model performance.
- Vehicle counting may be affected by missed detections or tracking ID changes.
- Traffic density is currently estimated using visible vehicle counts, not calibrated road-area measurements.
- The current detection configuration is designed for common road vehicles. Aircraft detection requires a suitable model and different class configuration.

## Author

**Muhammad Fahad**

AI & Machine Learning Enthusiast | Python Developer | Data Analyst

GitHub: [Your GitHub Profile](https://github.com/YOUR_USERNAME)

LinkedIn: [Muhammad Fahad](https://www.linkedin.com/in/muhammad-fahad-analyst/)

---

## License

This project is available for educational and learning purposes. A formal open-source license can be added when the repository license is selected.
