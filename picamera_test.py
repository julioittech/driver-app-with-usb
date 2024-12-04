from picamera2 import Picamera2
import cv2
import time

def init_camera():
    try:
        picam2 = Picamera2()
        config = picam2.create_preview_configuration()
        picam2.configure(config)
        picam2.start()
        time.sleep(2)
        return picam2
    except Exception as e:
        print(f"Error initializing camera: {e}")
        return None

def run_video_with_recording():
    camera = init_camera()
    
    if not camera:
        print("Failed to initialize camera")
        return
        
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640,480))
    
    try:
        while True:
            frame = camera.capture_array()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Write the frame
            out.write(frame)
            
            # Display frame
            cv2.imshow("Camera Feed", frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error during video capture: {e}")
    
    finally:
        # Cleanup
        camera.stop()
        out.release()
        cv2.destroyAllWindows()
        print("Camera stopped and video saved")

if __name__ == "__main__":
    run_video_with_recording()
