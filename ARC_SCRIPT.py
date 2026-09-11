"""
ARC_SCRIPT.py
--------------
PASTE THIS INTO ARC'S SCRIPT EDITOR. Click Run (Alt-R) to start it.
Leave it running -- it loops forever, checking files every 0.5 seconds

BEFORE RUNNING, EDIT THESE 2 PATHS BELOW:
  1. SHARED_DIR      -- folder where VS Code and ARC both read/write files
  2. PICTURES_FOLDER  -- where ARC's "Camera Snapshot" skill saves photos
     (default is: C:/Users/<YourWindowsUsername>/Pictures/My Robot Pictures)

Make sure you've added the "Camera Snapshot" skill to your ARC project:
  Project -> Add Skill -> Camera -> Camera Snapshot
"""

import time
import os
import shutil

# ---- EDIT THESE TWO PATHS ----
SHARED_DIR = "C:/Users/Ahmed Ali/Documents/Coding/robotics"
PICTURES_FOLDER = "C:/Users/Ahmed Ali/OneDrive/Pictures/My Robot Pictures"
# -------------------------------

TRIGGER_FILE = SHARED_DIR + "/trigger.txt"
READY_FILE = SHARED_DIR + "/ready.txt"
SPEAK_FILE = SHARED_DIR + "/speak.txt"
SERVO_FILE = SHARED_DIR + "/servo.txt"
ARM_FILE = SHARED_DIR + "/arm.txt"
LED_FILE = SHARED_DIR + "/led.txt"
SNAPSHOT_DEST = SHARED_DIR + "/snapshot.jpg"

# Make sure the control files exist AND are empty at startup -- this
# prevents leftover text from a previous crashed/interrupted Python
# session (e.g. speak.txt still holding old text) from being acted on
# immediately when this script starts, before object_finder.py even runs.
for path in [TRIGGER_FILE, READY_FILE, SPEAK_FILE, SERVO_FILE, ARM_FILE, LED_FILE]:
    with open(path, "w") as f:
        f.write("")

print("ARC object-detection listener started. Waiting for requests...")

while True:
    try:
        # ---------------------------------------------------------
        # PART 1: check if VS Code wants a photo taken
        # ---------------------------------------------------------
        with open(TRIGGER_FILE, "r") as f:
            trigger = f.read().strip()

        if trigger == "1":
            print("Capture requested. Taking snapshot...")

            # Warm-up shot: the camera buffer can return a stale frame if
            # idle, so we take one throwaway snapshot first to flush it.
            ControlCommand("Camera Snapshot", "CameraSnapshot")
            time.sleep(1.0)

            # Real shot: this one should reflect the current scene.
            ControlCommand("Camera Snapshot", "CameraSnapshot")
            time.sleep(1.5)  # give ARC time to actually save the file

            files = [
                os.path.join(PICTURES_FOLDER, f)
                for f in os.listdir(PICTURES_FOLDER)
            ]
            if files:
                newest = max(files, key=os.path.getmtime)
                shutil.copy(newest, SNAPSHOT_DEST)
                print("Copied newest photo: " + newest)
            else:
                print("Warning: no files found in " + PICTURES_FOLDER)

            with open(TRIGGER_FILE, "w") as f:
                f.write("")
            with open(READY_FILE, "w") as f:
                f.write("1")

        # ---------------------------------------------------------
        # PART 2: check if VS Code sent back a description to speak
        # ---------------------------------------------------------
        with open(SPEAK_FILE, "r") as f:
            text_to_speak = f.read().strip()

        if text_to_speak:
            print("Speaking: " + text_to_speak)
            Audio.sayEZB(text_to_speak)
            with open(SPEAK_FILE, "w") as f:
                f.write("")

        # ---------------------------------------------------------
        # PART 3: check if VS Code sent a new head position
        # Format expected in servo.txt: "pan,tilt"  e.g. "90,90"
        # pan = D0 (left/right), tilt = D1 (up/down)
        # ---------------------------------------------------------
        with open(SERVO_FILE, "r") as f:
            servo_command = f.read().strip()

        if servo_command:
            try:
                parts = servo_command.split(",")
                pan = int(float(parts[0]))
                pan = max(0, min(180, pan))  # safety clamp
                Servo.setSpeed(d0, 4)  # 0=fastest, 10=slowest -- smooths out movement
                Servo.setPosition(d0, pan)
                try:
                    Servo.waitForPositionEquals(d0, pan, 1500)  # confirm arrival, 1.5s timeout
                except Exception:
                    pass  # if unsupported, fall back to the sleep() on the Python side

                if len(parts) > 1:
                    tilt = int(float(parts[1]))
                    tilt = max(0, min(180, tilt))  # safety clamp
                    Servo.setSpeed(d1, 4)
                    Servo.setPosition(d1, tilt)
                    try:
                        Servo.waitForPositionEquals(d1, tilt, 1500)
                    except Exception:
                        pass
                    print("Head moved to pan=" + str(pan) + ", tilt=" + str(tilt))
                else:
                    print("Head moved to pan=" + str(pan))
            except Exception as e:
                print("Servo command error: " + str(e))
            with open(SERVO_FILE, "w") as f:
                f.write("")

        # ---------------------------------------------------------
        # PART 4: check if VS Code sent an arm-pointing command
        # Format expected in arm.txt: "side:angle"  e.g. "RIGHT:60"
        #
        # TODO -- these ports and angles are PLACEHOLDERS. Test with
        # your real robot (using the Auto Position editor's "Port Edit
        # Mode", like you did for the head) to find the actual arm
        # servo ports and the angle that looks like "pointing".
        
        with open(ARM_FILE, "r") as f:
            arm_command = f.read().strip()

        if arm_command:
            try:
                side, angle_str = arm_command.split(":")
                angle = int(float(angle_str))
                angle = max(0, min(180, angle))  # safety clamp

                if side == "RIGHT":
                    Servo.setSpeed(d4, 4)   # TODO: confirm this is the right servo port
                    Servo.setPosition(d4, angle)
                    print("Right arm moved to: " + str(angle))
                elif side == "LEFT":
                    Servo.setSpeed(d8, 4)   # TODO: confirm this is the right servo port
                    Servo.setPosition(d8, angle)
                    print("Left arm moved to: " + str(angle))
                else:
                    print("Unknown arm side: " + side)
            except Exception as e:
                print("Arm command error: " + str(e))
            with open(ARM_FILE, "w") as f:
                f.write("")

        # ---------------------------------------------------------
        # PART 5: check if VS Code wants an RGB light effect triggered
        # Format expected in led.txt: "SUCCESS" or "IDLE"
        #
        # Confirmed command syntax from Synthiam docs:
        #   ControlCommand("RGB Animator", AutoPositionAction, "actionName")
        # ---------------------------------------------------------
        with open(LED_FILE, "r") as f:
            led_command = f.read().strip()

        if led_command:
            try:
                if led_command == "SUCCESS":
                    ControlCommand("RGB Animator", "AutoPositionAction", "Flash")
                    print("LED: success flash triggered")
            except Exception as e:
                print("LED command error: " + str(e))
            with open(LED_FILE, "w") as f:
                f.write("")

    except Exception as e:
        print("Error: " + str(e))

    time.sleep(0.5)