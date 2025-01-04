import pickle
import numpy as np
import cv2
import face_recognition
from tkinter import Tk
from tkinter import filedialog

def load_encodings(file_path="EncodeFile.p"):
    """
    Load known face encodings and corresponding IDs from a file.
    """
    with open(file_path, 'rb') as file:
        encodeListKnownWithIds = pickle.load(file)
    return encodeListKnownWithIds[0], encodeListKnownWithIds[1]  # encodeListKnown, studentIds

def select_image():
    """
    Open a file dialog to select an image.
    :return: Path to the selected image.
    """
    # Initialize Tkinter and hide the root window
    root = Tk()
    root.withdraw()  # Hide the Tkinter root window
    image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    root.destroy()  # Destroy the Tkinter root window
    return image_path

def test_face_recognition(encodings_file="EncodeFile.p"):
    """
    Test if a face in the selected image matches any in the known encodings.

    :param encodings_file: Path to the file containing known face encodings.
    :return: Matched ID if found, otherwise None.
    """
    # Allow user to select an image
    image_path = select_image()
    if not image_path:
        print("No image selected.")
        return None

    # Load the known encodings
    encodeListKnown, studentIds = load_encodings(encodings_file)

    # Load and process the selected image
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Detect face locations and encodings in the image
    face_locations = face_recognition.face_locations(img)
    face_encodings = face_recognition.face_encodings(img, face_locations)

    for encodeFace, faceLoc in zip(face_encodings, face_locations):
        # Compare the test image encoding with the known encodings
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        if matches:
            # Get the index of the best match
            matchIndex = np.argmin(faceDis)
            if matches[matchIndex]:
                return studentIds[matchIndex]  # Return the matched ID

    return None  # No match found

# Example usage
if __name__ == "__main__":
    result = test_face_recognition()
    if result:
        print(f"Matched ID: {result}")
    else:
        print("No match found.")
