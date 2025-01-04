import os
import cv2
import face_recognition
import pickle
from tkinter import Tk
from tkinter import filedialog

# Directory where employee folders are stored
KNOWN_FACE_DIR = 'known_face'

# Load existing encodings (if any)
def load_existing_encodings():
    if os.path.exists("EncodeFile.p"):
        with open("EncodeFile.p", 'rb') as file:
            return pickle.load(file)
    else:
        return [], []

# Save encodings to file
def save_encodings(encodeListKnownWithIds):
    with open("EncodeFile.p", 'wb') as file:
        pickle.dump(encodeListKnownWithIds, file)

# Process images and update encodings
def update_encodings(employee_id, image_path):
    # Read the image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Generate the face encoding
    encode = face_recognition.face_encodings(img)[0]

    # Load existing encodings and IDs
    encodeListKnown, employeeIds = load_existing_encodings()

    # Add the new encoding and employee ID
    encodeListKnown.append(encode)
    employeeIds.append(employee_id)

    # Save updated encodings
    save_encodings([encodeListKnown, employeeIds])
    print(f"Encoding updated for ID: {employee_id}!")

# Ask for employee ID and photo
def intake_photos():
    # Ask for employee ID
    employee_id = input("Enter the employee ID: ").strip()

    # Create the directory for the employee if it doesn't exist
    employee_dir = os.path.join(KNOWN_FACE_DIR, employee_id)
    os.makedirs(employee_dir, exist_ok=True)

    # Initialize Tkinter and hide the root window
    print("Select a photo to upload for the employee.")
    root = Tk()
    root.withdraw()  # Hide the Tkinter root window

    # Open a file dialog to select a photo
    photo_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    root.destroy()  # Destroy the root window after use

    if photo_path:
        # Copy the image to the employee's directory
        file_name = os.path.basename(photo_path)
        destination_path = os.path.join(employee_dir, file_name)
        os.rename(photo_path, destination_path)
        print(f"Photo added to {employee_dir}!")

        # Update the encodings
        update_encodings(employee_id, destination_path)
    else:
        print("No photo selected.")

# Main function
if __name__ == "__main__":
    # Ensure the `known_face` directory exists
    os.makedirs(KNOWN_FACE_DIR, exist_ok=True)

    # Run the intake process
    intake_photos()
