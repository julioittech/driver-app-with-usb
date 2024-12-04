from picamera import PiCamera
import time

def init_camera():
    try:
        # Initialize camera
        camera = PiCamera()
        
        # Let camera warm up
        time.sleep(2)
        
        # Optional: rotate camera if needed
        # camera.rotation = 180
        
        print("Camera initialized successfully")
        return camera
        
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

def take_test_photo(camera):
    if camera:
        try:
            # Capture image
            camera.capture('test_photo.jpg')
            print("Test photo captured successfully")
        except Exception as e:
            print(f"Error taking photo: {e}")

def main():
    # Initialize camera
    camera = init_camera()
    
    if camera:
        # Take test photo
        take_test_photo(camera)
        
        # Close camera properly
        camera.close()
        print("Camera stopped")

if __name__ == "__main__":
    main()
