import time
import RPi.GPIO as GPIO

PUMP_PIN = 24
PUMP_DURATION = 50

GPIO.setmode(GPIO.BCM)
print("Start:")
GPIO.setup(PUMP_PIN, GPIO.OUT, initial=GPIO.LOW)
print(f"AN für {PUMP_DURATION} Sekunden")
GPIO.output(PUMP_PIN, GPIO.HIGH)
time.sleep(PUMP_DURATION)
GPIO.output(PUMP_PIN, GPIO.LOW)

print("Ende")
GPIO.cleanup()
