"""
vision.py
----------
Sends a camera frame to Gemini and gets back a short spoken-style
description of what's in the image. Uses the new google-genai SDK
(the old google-generativeai package is deprecated).
"""

import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()  # reads keys from your .env file

# Two separate API keys (from two different Google accounts) so each
# task gets its own independent daily quota (20/day free tier each).
client_object_search = genai.Client(api_key=os.environ["GEMINI_API_KEY_SEARCH"])
client_location = genai.Client(api_key=os.environ["GEMINI_API_KEY_LOCATION"])

MODEL_NAME = "gemini-flash-latest"

PROMPT = (
    "You are a robot's vision system. Look at this image and identify the "
    "main object(s) you see. Respond with ONLY a short, natural sentence "
    "naming what you see, suitable to be spoken out loud by a robot. "
    "Example: 'I see a coffee mug and a laptop.' "
    "If nothing recognizable is visible, say 'I don't see anything I recognize.'"
)


def identify_objects(image_bytes: bytes) -> str:
    response = client_location.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            PROMPT,
        ],
    )
    return response.text.strip()


def extract_target_object_offline(command_text: str) -> dict:
    """
    Fallback for when there's no internet (Gemini unavailable). Does a
    simple substring search through the COCO class list -- much dumber
    than Gemini, but works completely offline. Only catches simple
    phrasing like "find my bottle" or just "bottle".
    """
    from coco_classes import COCO_CLASSES

    text = command_text.lower()
    for obj in COCO_CLASSES:
        if obj in text:
            return {"object": obj, "supported": True}
    return {"object": None, "supported": False}


def extract_target_object(command_text: str) -> dict:
    """
    Uses Gemini to figure out what object the user wants to find, from a
    natural language command like "find my bottle" or "where is the cell phone".
    Falls back to offline keyword matching if Gemini is unreachable
    (e.g. no internet).

    Returns:
        {"object": "bottle", "supported": True}   -- if it's something
                                                       YOLO can recognize
        {"object": "keys", "supported": False}     -- if YOLO can't recognize it
    """
    from coco_classes import COCO_CLASSES

    prompt = (
        "A user gave this command to a robot: \"" + command_text + "\"\n\n"
        "Figure out what single object they want the robot to find. "
        "The robot can ONLY recognize objects from this exact list:\n"
        + ", ".join(COCO_CLASSES) + "\n\n"
        "Respond with ONLY the object name from that list, in lowercase, "
        "exactly as written in the list (e.g. 'bottle', 'cell phone'). "
        "If the object they want is NOT in that list, respond with exactly: "
        "UNSUPPORTED"
    )

    try:
        response = client_object_search.models.generate_content(model=MODEL_NAME, contents=[prompt])
        result = response.text.strip().lower()
        if result == "unsupported" or result not in COCO_CLASSES:
            return {"object": result, "supported": False}
        return {"object": result, "supported": True}
    except Exception as e:
        print(f"Gemini unavailable ({e}), falling back to offline matching...")
        return extract_target_object_offline(command_text)


def describe_object_location(image_bytes: bytes, object_label: str) -> str:
    """
    Given the photo where the object was found, asks Gemini to describe
    WHERE it is in natural language (e.g. "on the table near the desk"),
    instead of just saying "I found it."
    """
    prompt = (
        f"Look at this image. There is a {object_label} somewhere in it. "
        "Describe its location in a short, natural, spoken sentence -- "
        "mention what it's on, near, or next to. For example: "
        "'on the table near the desk' or 'on the floor next to the chair'. "
        "Keep it under 15 words. Respond with ONLY the location phrase, "
        "no extra commentary."
    )
    response = client_location.models.generate_content(
        model=MODEL_NAME,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
            prompt,
        ],
    )
    return response.text.strip()