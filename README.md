# AEGIS-JD — Object Detection & PID Tracking Module

This repository contains **my individual contribution** to AEGIS-JD (Autonomous Engagement & Guardian Intelligence System) — a unified, multi-modal control system built for the EZ-Robot JD Humanoid, developed during my robotics internship as part of a 5-member team.

The full AEGIS-JD platform integrates object detection, gesture/emotion/pose control, speech control, conversational AI, facial recognition, and a security gate. **This repo covers only the module I built: real-time object detection, AI-based target reasoning, and PID-based servo tracking.**

## My Contribution

Everything in this repo — `object_finder.py`, `yolo_detector.py`, `pid_controller.py`, `vision.py`, `coco_classes.py`, and `ARC_SCRIPT.py` — was designed and implemented by me as my individual module within the AEGIS-JD team project. This includes:

- The YOLOv8 detection pipeline and object-position extraction
- The Gemini-based reasoning layer (target extraction from natural language + spoken location description)
- The PID controller and its integration into the pan/tilt centering logic
- The file-based IPC architecture connecting Python (VS Code) to Synthiam ARC
- The ARC-side script that drives the robot's head, arm, and RGB LED servos

## What This Module Does

Given a spoken/typed command like *"find my bottle"*, the robot:

1. Uses the **Gemini API** to figure out which object the user is asking for
2. **Scans its surroundings** (pan/tilt sweep) while running **YOLOv8** object detection on each captured frame
3. Once the object is found, uses a **PID controller** to smoothly center the camera on it — no jerky or overshooting movement
4. Uses **Gemini** again to describe where the object is in natural, spoken language
5. **Speaks** the result back through the robot

Python (this module) communicates with the robot hardware via file-based IPC with `ARC_SCRIPT.py`, which runs inside Synthiam ARC and directly drives the JD's head (pan/tilt), arm, and RGB LED servos/effects.

## Files

| File | Purpose |
|---|---|
| `object_finder.py` | Main orchestrator — ties detection, reasoning, and PID tracking together |
| `yolo_detector.py` | Runs YOLOv8 on captured frames, returns detected objects + positions |
| `pid_controller.py` | Reusable PID controller for smooth servo tracking |
| `vision.py` | Gemini API integration — target extraction from natural language + location description |
| `coco_classes.py` | List of the 80 object classes YOLOv8 can recognize |
| `ARC_SCRIPT.py` | Runs inside Synthiam ARC — reads commands from shared files and drives the robot's pan/tilt head servos, arm/pointing servos, and RGB LED expressions |
| `requirements.txt` | Python dependencies |

> **Note:** In the full AEGIS-JD system, `object_finder.py` also calls into a face-recognition module built by another teammate (for "who is this?" style commands). That module is **not included here** — it belongs to a different contributor. This repo has been trimmed so that code path is inactive/removed, and it runs standalone without it.

## Tech Stack

- **Object Detection:** YOLOv8 (Ultralytics, local inference, no internet required)
- **AI Reasoning:** Google Gemini API (`google-genai` SDK, `gemini-flash-latest`)
- **Control:** Custom PID controller (Kp/Ki/Kd tuned for smooth servo tracking)
- **Hardware Bridge:** File-based IPC between Python and Synthiam ARC
- **Language:** Python
- **Platform:** Windows only — `object_finder.py` uses `msvcrt` for non-blocking keyboard input as a backup to voice commands. `yolo_detector.py` and `pid_controller.py` have no Windows-specific dependencies and can run on any OS.

## Setup

1. Clone this repo and install dependencies:
   ```
   pip install -r requirements.txt
   ```
2. Copy `_env.example` to `.env` and add your own Gemini API keys:
   ```
   GEMINI_API_KEY_SEARCH=your_key_here
   GEMINI_API_KEY_LOCATION=your_key_here
   ```
3. Edit `SHARED_DIR` in **both** `object_finder.py` and `ARC_SCRIPT.py` to match a folder on your own machine — this is the shared location Python and ARC use to exchange files.
4. The YOLOv8 model (`yolov8n.pt`) auto-downloads on first run — no manual download needed.
5. Paste `ARC_SCRIPT.py` into Synthiam ARC's script editor and run it (Alt-R) — it listens for commands via shared text files (`trigger.txt`, `servo.txt`, `arm.txt`, `led.txt`, `speak.txt`) and drives the physical robot accordingly.

Without a connected JD robot, `object_finder.py` won't have hardware to drive, but `yolo_detector.py` and `pid_controller.py` can be tested independently.

## About the Full Project

AEGIS-JD was built by a 5-member team as part of a robotics internship:

- **Object Detection & PID Servo Control** — this repo (my contribution)
- Gesture, Emotion, Pose & Speech Control, System Integration — teammate contribution
- Facial Recognition & Security Gate — teammate contribution
- Conversational AI ("Ask JD") — teammate contribution

This repo reflects only my individual work on the project.

## 🧑‍💻 Author

**Ahmed Ali**
Electrical Engineering Student | Tech Enthusiast
LinkedIn: [www.linkedin.com/in/ahmedali88](https://www.linkedin.com/in/ahmedali88)
