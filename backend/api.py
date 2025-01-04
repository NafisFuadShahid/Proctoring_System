from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import cv2
import numpy as np
import pickle
import os
from typing import Optional
import shutil

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your Next.js domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

KNOWN_FACE_DIR = 'known_face'
ENCODE_FILE = 'EncodeFile.p'

def load_encodings():
    if os.path.exists(ENCODE_FILE):
        with open(ENCODE_FILE, 'rb') as file:
            return pickle.load(file)
    return [[], []]  # Empty encodings and IDs

def save_encodings(encodeListKnown, employeeIds):
    with open(ENCODE_FILE, 'wb') as file:
        pickle.dump([encodeListKnown, employeeIds], file)

@app.post("/api/enroll")
async def enroll_employee(file: UploadFile = File(...), employeeId: str = Form(...)):
    try:
        # Create employee directory
        employee_dir = os.path.join(KNOWN_FACE_DIR, employeeId)
        os.makedirs(employee_dir, exist_ok=True)

        # Save uploaded file
        file_path = os.path.join(employee_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process image for face encoding
        img = cv2.imread(file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(img)
        if not face_locations:
            os.remove(file_path)  # Clean up file if no face detected
            return {"success": False, "message": "No face detected in the image"}

        # Generate encoding
        encode = face_recognition.face_encodings(img, face_locations)[0]

        # Load existing encodings
        encodeListKnown, employeeIds = load_encodings()

        # Add new encoding
        encodeListKnown.append(encode)
        employeeIds.append(employeeId)

        # Save updated encodings
        save_encodings(encodeListKnown, employeeIds)

        return {"success": True, "message": f"Employee {employeeId} enrolled successfully"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

@app.post("/api/verify")
async def verify_face(file: UploadFile = File(...)):
    try:
        # Save uploaded file temporarily
        temp_path = f"temp_{file.filename}"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Process image
        img = cv2.imread(temp_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Load known encodings
        encodeListKnown, employeeIds = load_encodings()

        # Detect faces
        face_locations = face_recognition.face_locations(img)
        if not face_locations:
            return {"matched": False, "message": "No face detected in the image"}

        face_encodings = face_recognition.face_encodings(img, face_locations)

        for encodeFace in face_encodings:
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

            if matches and len(matches) > 0:
                matchIndex = np.argmin(faceDis)
                if matches[matchIndex]:
                    return {
                        "matched": True,
                        "employeeId": employeeIds[matchIndex],
                        "message": f"Match found: Employee {employeeIds[matchIndex]}"
                    }

        return {"matched": False, "message": "No match found"}

    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)