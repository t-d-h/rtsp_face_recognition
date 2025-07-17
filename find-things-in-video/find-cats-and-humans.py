import cv2
import numpy as np
import sys
import os
import subprocess

def download_yolo_files():
    """Checks for YOLO files and downloads them if they are missing."""
    files = {
        "yolov3.weights": "https://onboardcloud.dl.sourceforge.net/project/yolov3.mirror/v8/yolov3.weights?viasf=1",
        "yolov3.cfg": "https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg",
        "coco.names": "https://raw.githubusercontent.com/pjreddie/darknet/master/data/coco.names"
    }
    print("Checking for YOLO model files...")
    for filename, url in files.items():
        if not os.path.exists(filename):
            print(f"Downloading {filename}...")
            try:
                # Use wget to download the file
                subprocess.run(["wget", "-q", "--show-progress", url], check=True)
                print(f"Successfully downloaded {filename}")
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"Error: Failed to download {filename}.")
                print("Please make sure 'wget' is installed and you have an internet connection.")
                sys.exit(1)
    print("All required files are present.")


# --- Configuration ---
download_yolo_files()


# Load YOLO
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
classes = []
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

layer_names = net.getLayerNames()
output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
colors = np.random.uniform(0, 255, size=(len(classes), 3))

# --- Video File ---
if len(sys.argv) != 2:
    print("Usage: python find-cats-and-humans.py <video_file_path>")
    sys.exit()

video_path = sys.argv[1]
cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Error: Could not open video file.")
    exit()

# Get video properties to create the output file
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = cap.get(cv2.CAP_PROP_FPS)

# Define the codec and create VideoWriter object
output_path = video_path.rsplit('.', 1)[0] + '_output.mp4'
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
video_writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

print(f"Processing video and saving output to {output_path}")

frame_count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break # End of video

    frame_count += 1
    if frame_count % 100 == 0:
        print(f"Processing frame {frame_count}...")

    height, width, channels = frame.shape

    # Detecting objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    # Showing information on the screen
    class_ids = []
    confidences = []
    boxes = []
    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                # Object detected
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)

                # Rectangle coordinates
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)

                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

    # Flag to check if a cat or human was detected in the frame
    cat_or_human_detected = False
    for i in range(len(boxes)):
        if i in indexes:
            label = str(classes[class_ids[i]])
            if label in ["person", "cat"]:
                cat_or_human_detected = True
                x, y, w, h = boxes[i]
                color = (0, 255, 0)  # Green for cats and humans
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, label, (x, y + 30), cv2.FONT_HERSHEY_PLAIN, 2, color, 2)

    # Write the frame to the output file only if a cat or human was detected
    if cat_or_human_detected:
        video_writer.write(frame)

# Release everything when job is finished
print("Finished processing. Releasing resources.")
video_writer.release()
cap.release()