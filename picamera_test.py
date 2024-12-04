from picamera2 import Picamera2
import time

def init_camera():
    try:
        # Initialize camera
        picam2 = Picamera2()
        
        # Configure camera
        config = picam2.create_still_configuration()
        picam2.configure(config)
        
        # Start camera
        picam2.start()
        print("Camera initialized successfully")
        
        # Let camera warm up
        time.sleep(2)
        
        return picam2
        
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

def take_test_photo(camera):
    if camera:
        try:
            # Capture image
            camera.capture_file("test_photo.jpg")
            print("Test photo captured successfully")
        except Exception as e:
            print(f"Error taking photo: {e}")

def main():
    # Initialize camera
    camera = init_camera()
    
    if camera:
        # Take test photo
        take_test_photo(camera)
        
        # Stop camera properly
        camera.stop()
        print("Camera stopped")

if __name__ == "__main__":
    main()
