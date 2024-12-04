from picamera2 import Picamera2
import time

def init_camera():
    try:
        picam2 = Picamera2()
        
        # Configure camera
        config = picam2.create_still_configuration()
        picam2.configure(config)
        
        picam2.start()
        print("Camera initialized successfully")
        
        time.sleep(2)
        
        return picam2
        
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

def take_test_photo(camera):
    if camera:
        try:
            camera.capture_file("test_photo.jpg")
            print("Test photo captured successfully")
        except Exception as e:
            print(f"Error taking photo: {e}")

def main():
    camera = init_camera()
    
    if camera:
        take_test_photo(camera)
        camera.stop()
        print("Camera stopped")

if __name__ == "__main__":
    main()
