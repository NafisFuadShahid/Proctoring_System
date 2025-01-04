import cv2
import face_recognition
import os
import time
import pickle
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProctorMonitor:
    def __init__(self, target_employee_id, interval=60):
        self.target_employee_id = target_employee_id
        self.interval = interval  # interval in seconds
        self.flagged_dir = 'flagged_photos'
        self.encode_file = 'EncodeFile.p'
        self.camera = None
        
        # Create flagged photos directory if it doesn't exist
        os.makedirs(self.flagged_dir, exist_ok=True)
        
        # Load target employee's encoding
        self.load_target_encoding()
        
    def load_target_encoding(self):
        """Load the target employee's face encoding from the saved encodings"""
        try:
            with open(self.encode_file, 'rb') as file:
                encodings, ids = pickle.load(file)
                if self.target_employee_id in ids:
                    idx = ids.index(self.target_employee_id)
                    self.target_encoding = encodings[idx]
                    logger.info(f"Successfully loaded encoding for employee {self.target_employee_id}")
                else:
                    raise ValueError(f"Employee {self.target_employee_id} not found in database")
        except Exception as e:
            logger.error(f"Error loading target encoding: {str(e)}")
            raise
    
    def initialize_camera(self):
        """Initialize the webcam"""
        self.camera = cv2.VideoCapture(0)
        if not self.camera.isOpened():
            raise RuntimeError("Could not access webcam")
        logger.info("Camera initialized successfully")
    
    def capture_photo(self):
        """Capture a photo from the webcam"""
        ret, frame = self.camera.read()
        if not ret:
            raise RuntimeError("Failed to capture frame")
        return frame
    
    def check_presence(self, frame):
        """Check if the target employee is present in the frame"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Find faces in the frame
        face_locations = face_recognition.face_locations(rgb_frame)
        if not face_locations:
            logger.info("No faces detected in frame")
            return False
            
        # Get encodings for detected faces
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        # Check each detected face
        for face_encoding in face_encodings:
            # Compare with target encoding
            matches = face_recognition.compare_faces([self.target_encoding], face_encoding, tolerance=0.6)
            if matches[0]:
                logger.info("Target employee detected")
                return True
        
        logger.info("Target employee not detected")
        return False
    
    def save_flagged_photo(self, frame):
        """Save the frame when target employee is not detected"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.flagged_dir, f"flagged_{timestamp}.jpg")
        cv2.imwrite(filename, frame)
        logger.info(f"Flagged photo saved: {filename}")
    
    def run(self):
        """Main monitoring loop"""
        try:
            self.initialize_camera()
            logger.info(f"Starting monitoring for employee {self.target_employee_id}")
            
            while True:
                try:
                    # Capture frame
                    frame = self.capture_photo()
                    
                    # Check if target is present
                    if not self.check_presence(frame):
                        self.save_flagged_photo(frame)
                    
                    # Wait for next interval
                    time.sleep(self.interval)
                    
                except Exception as e:
                    logger.error(f"Error during monitoring: {str(e)}")
                    time.sleep(5)  # Wait before retrying
                    
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        finally:
            if self.camera is not None:
                self.camera.release()
            logger.info("Camera released")

if __name__ == "__main__":
    # Example usage
    monitor = ProctorMonitor(
        target_employee_id="1234",  # Replace with actual employee ID
        interval=5  # Check every 60 seconds
    )
    monitor.run()