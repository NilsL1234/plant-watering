from enum import Enum, auto
from spidev import SpiDev
import RPi.GPIO as GPIO
import time

##############################################################################################

# ENUMS

class State(Enum): 
    WAITING = auto()
    MEASURING = auto()
    PUMPING = auto()
    PAUSE_PUMPING = auto()
    MEASURING_AFTER_PUMPING = auto()
    END = auto()

##############################################################################################   

# CONSTS

MEASUREMENT_INTERVALL_SECONDS = 10
MAX_MEASUREMENT_INTERVALLS = 10
PUMPING_SECONDS = 60
PAUSE_AFTER_PUMPING_SECONDS = 120

UPPTER_THRESHOLD_MEASUREMENT = 1000
LOWER_THRESHOLD_MEASUREMENT = 600


MAX_SENSOR_VALUE = 1023
MIN_SENSOR_VALUE = 0
MAX_RE_PUMPING = 5

PUMP_PIN = 24

CHANNEL_MCP = 0





##############################################################################################

# VARIABLES

current_state = State.WAITING
current_measurement_value = 0
current_number_measurements = 0
current_number_repumps = 0

##############################################################################################

# FUNCTIONS

def check_unusual_measurement_value(current_value):
    if current_value >= MAX_SENSOR_VALUE:
        print(f"Error: Unsual high measure value: {current_value}")
        return True
    
    if current_value == MIN_SENSOR_VALUE:
        print(f"Error: Unsual low measure value: {current_value}")
        return True
    
    return False

    
# Use spi to measure 5 times, once per second and get the average.
def measure(spi, channel):

    values = []

    for i in range(5):
        request = [1, (8 + channel) << 4, 0]
        response = spi.xfer2(request)
        value = ((response[1] & 3)<< 8) | response[2]
        values.append(value)
        time.sleep(1)
    
    result = sum(values) / len(values)
    print(f"Current measurement value:  {result}")
    return result

# Switching the current state according to the measurement
# During pumping cycle, the result needs to be under LOWER_THRESHOLD_MEASUREMENT, to exit the cycle
# Guaranties that the watering isnt just a bit below the threashold

def switch_current_state_after_measuring(measurement_result):
    if current_state == State.MEASURING:
        print("normal measurement:")
        if measurement_result >= UPPTER_THRESHOLD_MEASUREMENT:
            return State.PUMPING
        else:
            return State.WAITING

    if current_state == State.MEASURING_AFTER_PUMPING:
        print("measurement after pumping:")
        if measurement_result < LOWER_THRESHOLD_MEASUREMENT:
            return State.WAITING
        else: return State.PUMPING

def pumping():
    print(f"Pumpe läuft für {PUMPING_SECONDS} Sekunden")
    
    try:
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        time.sleep(PUMPING_SECONDS)
    finally:
        GPIO.output(PUMP_PIN, GPIO.LOW)
    
    print("Ende des Pumpdurchgangs...")


##############################################################################################

def main():
    
    # Init hardware
    spi = SpiDev()
    spi.open(0,0)
    spi.max_speed_hz = 1_000_000

    GPIO.setmode(GPIO.BCM)
    print("Initialisierung Pumpe...")
    GPIO.setup(PUMP_PIN, GPIO.OUT, initial=GPIO.LOW)


    # Loop that controlls the pump with different states. 
    # Each case of the current_state does something and then changes the current_state accordingly.
    # Then the loop starts again with the new state.
    try:
        while True:

            match current_state:
                case State.WAITING:
                    print(f"waiting {MEASUREMENT_INTERVALL_SECONDS} sec. ...")
                    time.sleep(MEASUREMENT_INTERVALL_SECONDS)
                    current_state = State.MEASURING

                case State.MEASURING:
                    print("measuring...")
                    current_measurement_value = measure(spi, CHANNEL_MCP)
                    if check_unusual_measurement_value(current_measurement_value):
                        break
                    current_number_measurements += 1
                    if current_number_measurements == MAX_MEASUREMENT_INTERVALLS:
                        print(f"maximum measurements of {MAX_MEASUREMENT_INTERVALLS} is reached...")
                        current_state = State.END
                        continue
                    #Rest repump-counter
                    current_number_repumps = 0
                    current_state = switch_current_state_after_measuring(current_measurement_value)

                case State.PUMPING:
                    print("pumping...")
                    pumping()
                    current_state = State.PAUSE_PUMPING
                
                case State.PAUSE_PUMPING:
                    print(f"pause for {PAUSE_AFTER_PUMPING_SECONDS} sec. after pumping...")
                    time.sleep(PAUSE_AFTER_PUMPING_SECONDS)
                    current_state = State.MEASURING_AFTER_PUMPING


                case State.MEASURING_AFTER_PUMPING:
                    print("measuring after pumping...")
                    current_measurement_value = measure(spi, CHANNEL_MCP)
                    if check_unusual_measurement_value(current_measurement_value):
                        break
                    current_number_measurements += 1
                    if current_number_measurements == MAX_MEASUREMENT_INTERVALLS:
                        print(f"maximum measurements of {MAX_MEASUREMENT_INTERVALLS} is reached...")
                        current_state = State.END
                        continue
                    current_number_repumps += 1
                    if current_number_repumps == MAX_RE_PUMPING:
                        print(f"maximum repumps of {MAX_RE_PUMPING} is reached, check the sensor")
                        current_state = State.END
                        continue
                    current_state = switch_current_state_after_measuring(current_measurement_value)

                case State.END:
                    print("programm ends now...")
                    break
                
    except KeyboardInterrupt:
        print("Manueller Abbruch")

    finally:
        GPIO.output(PUMP_PIN, GPIO.LOW)
        GPIO.cleanup()
        spi.close()


if __name__ == "__main__":
    main()
