from enum import Enum, auto
from spidev import SpiDev
import RPi.GPIO as GPIO
from dataclasses import dataclass 
import time
import json
import signal
import os
import logging

##############################################################################################
# ENUMS

class State(Enum): 
    WAITING = auto()
    MEASURING = auto()
    PUMPING = auto()
    PAUSE = auto()
    ERROR = auto()
    END = auto()

##############################################################################################   
@dataclass
class ControllerData:
    state: State = State.WAITING
    last_pump_timestamp: float | None = None
    watering_cycle_timestamp: float | None = None
    pumps_in_cycle: int = 0

##############################################################################################
# CONSTS

MEASUREMENT_INTERVALL_SEC = 1
MAX_MEASUREMENT_ERRORS = 3

PUMPING_DURATION_SEC = 540  # 9min
WATER_ABSORBTION_PERIOD_SEC = 5400 # 90min
WATERING_COOLDOWN_PERIOD_SEC = 86400 #24h

UPPER_THRESHOLD_MEASUREMENT = 950
LOWER_THRESHOLD_MEASUREMENT = 600

MAX_SENSOR_VALUE = 1023
MIN_SENSOR_VALUE = 0
MAX_SENSOR_VALUE_GAP = 100

PUMP_PIN = 24
CHANNEL_MCP = 0

STATE_FILE_PATH = "data/state.json"

##############################################################################################

# FUNCTIONS

# Use spi to measure 5 times, once per second and get the average.
# returns None, when there is a 0 or 1023 as value
def measure(spi, channel):

    values = []

    for i in range(5):
        request = [1, (8 + channel) << 4, 0]
        response = spi.xfer2(request)
        value = ((response[1] & 3)<< 8) | response[2]
        # catch invalid values
        if value == 0 or value == 1023:
            return None
        values.append(value)
        time.sleep(1)
    if max(values) - min(values) > MAX_SENSOR_VALUE_GAP:
        return None
    result = sum(values) / len(values)
    return result

def save_controller_data(data: ControllerData):

    state_data = {
            "last_pump_timestamp": data.last_pump_timestamp,
            "watering_cycle_timestamp": data.watering_cycle_timestamp,
            "pumps_in_cycle": data.pumps_in_cycle
            }
    # temporary save of new data
    temp_path = STATE_FILE_PATH + ".tmp"

    # fill temp file and make sure its saved on sd lvl and not just in cache of programm or os
    with open(temp_path, "w") as file:
        json.dump(state_data, file)
        file.flush()
        os.fsync(file.fileno())
        
    os.replace(temp_path, STATE_FILE_PATH)

    #make sure replacement is on sd
    directory_fd = os.open("data", os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)

# gets state_data from json file and inits ControllerData
def load_controller_data(data: ControllerData):

    with open(STATE_FILE_PATH, "r") as file:
        state_data = json.load(file)

    data.last_pump_timestamp = state_data["last_pump_timestamp"]
    data.watering_cycle_timestamp = state_data["watering_cycle_timestamp"]
    data.pumps_in_cycle = state_data["pumps_in_cycle"]
    

# handle_measurement_result:
# - update state depending on timers and measurement_result
# - check for repumps
def handle_measurement_result(measurement_result: float, data: ControllerData):

    if data.pumps_in_cycle == 0:
        if measurement_result > UPPER_THRESHOLD_MEASUREMENT:
            data.state = State.PUMPING
            logging.info(f"Watering required. ADC: {measurement_result:.1f}")
        else: data.state = State.WAITING
  
    elif data.pumps_in_cycle == 1:
        # in case there is enough water after 1 cycle
        if (time.time() - data.watering_cycle_timestamp) > (WATERING_COOLDOWN_PERIOD_SEC + PUMPING_DURATION_SEC):
            data.pumps_in_cycle = 0
            data.watering_cycle_timestamp = None
            save_controller_data(data)
            data.state = State.WAITING
            return
        # not enough water
        if measurement_result > LOWER_THRESHOLD_MEASUREMENT:
            data.state = State.PUMPING
            logging.info(f"Second watering required. ADC: {measurement_result:.1f}")
        else:
            # waiting state in case only 1 pump in cycle happens
            data.state = State.WAITING
    
    elif data.pumps_in_cycle == 2:
        if (time.time() - data.watering_cycle_timestamp) < (WATERING_COOLDOWN_PERIOD_SEC + PUMPING_DURATION_SEC):
            data.state = State.WAITING
        else:
            data.pumps_in_cycle = 0
            data.watering_cycle_timestamp = None
            save_controller_data(data)
            data.state = State.WAITING
    
def pumping():
    try:
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        time.sleep(PUMPING_DURATION_SEC)
    finally:
        GPIO.output(PUMP_PIN, GPIO.LOW)
    logging.info("Pump finished")

# 
def handle_sigterm(signum, frame):
    raise SystemExit(0)

##############################################################################################

def main():

    #init logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    last_measurement_log = 0

    # init controller
    logging.info("Controller started")
    data = ControllerData()
    try:
        load_controller_data(data)
    except FileNotFoundError:
        save_controller_data(data)
    
    # start in correct state
    if data.pumps_in_cycle == 1:
        data.state = State.PAUSE
    else: 
        data.state = State.WAITING

    measurement_errors = 0
    
    # init hardware
    spi = SpiDev()
    spi.open(0,0)
    spi.max_speed_hz = 100_000

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(PUMP_PIN, GPIO.OUT, initial=GPIO.LOW)

    # making sure pump gets stopped, when programm end via systemd 
    signal.signal(signal.SIGTERM, handle_sigterm)
 
    # Loop that controlls the pump with different states. 
    # Each case of the current_state does something and then changes the current_state accordingly.
    # Then the loop starts again with the new state.
    try:
        while True:

            match data.state:
                case State.WAITING:
                    time.sleep(MEASUREMENT_INTERVALL_SEC)
                    data.state = State.MEASURING
                    continue

                case State.MEASURING:
                    current_measurement_value = measure(spi, CHANNEL_MCP)
                    # handle measurement errors
                    if current_measurement_value is None:
                        measurement_errors += 1
                        logging.warning(f"Invalid measurement ({measurement_errors}/{MAX_MEASUREMENT_ERRORS})")
                        if measurement_errors >= MAX_MEASUREMENT_ERRORS:
                            data.state = State.ERROR

                        continue
                    measurement_errors = 0

                    #log value every 30min
                    if time.time() - last_measurement_log >= 1800:
                        logging.info(f"Soil moisture ADC: {current_measurement_value:.1f}")
                        last_measurement_log = time.time()

                    # update current state depending on measurement result and active timers
                    handle_measurement_result(current_measurement_value, data)
                    continue

                case State.PUMPING:
                    data.pumps_in_cycle += 1
                    data.last_pump_timestamp = time.time()
                    if data.pumps_in_cycle == 1:
                        data.watering_cycle_timestamp = time.time()
                        data.state = State.PAUSE
                    elif data.pumps_in_cycle == 2:
                        data.watering_cycle_timestamp = time.time()
                        data.state = State.WAITING
                    else:
                        data.state = State.ERROR
                        continue
                    logging.info(f"Pump started. Duration: {PUMPING_DURATION_SEC} sec")
                    if data.pumps_in_cycle == 1:
                        logging.info("Absorption pause active")
                    elif data.pumps_in_cycle == 2:
                        logging.info("Watering cooldown active")

                    save_controller_data(data)
                    pumping()
                        
                case State.PAUSE:
                    # reset timers
                    if (time.time() - data.last_pump_timestamp) >= (WATER_ABSORBTION_PERIOD_SEC + PUMPING_DURATION_SEC):
                        data.state = State.MEASURING
                    else:
                        time.sleep(10)
                    continue

                case State.END:
                    logging.info("Program ended")
                    break

                case State.ERROR:
                    logging.error("Measurement failed three times in a row")
                    break

    except KeyboardInterrupt:
        logging.info("Manual interrupt")

    finally:
        GPIO.output(PUMP_PIN, GPIO.LOW)
        GPIO.cleanup()
        spi.close()

if __name__ == "__main__":
    main()
