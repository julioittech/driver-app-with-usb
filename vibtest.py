import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
VIBRATION_PIN = 20

GPIO.setup(VIBRATION_PIN,GPIO.OUT)

try:
    while 1:
        for _ in range(3):
            print("Started vibration")
            GPIO.output(VIBRATION_PIN, GPIO.HIGH)
            time.sleep(0.2)
            GPIO.output(VIBRATION_PIN, GPIO.LOW)
            time.sleep(0.2)
        time.sleep(5)
finally:
    GPIO.cleanup()
    print("stopped")