
import cv2
import numpy as np
import pandas as pd
import matplotlib
import torch
import supervision as sv
import streamlit
import scipy
import plotly
from ultralytics import YOLO

print("All libraries imported successfully!")

print("OpenCV:", cv2.__version__)
print("NumPy:", np.__version__)
print("Pandas:", pd.__version__)
print("PyTorch:", torch.__version__)
print("Supervision:", sv.__version__)
print("CUDA Available:", torch.cuda.is_available())
