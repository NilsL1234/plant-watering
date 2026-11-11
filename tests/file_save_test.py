import json 

values = {
    "last_pump_timestamp": 12,
    "watering_cycle_timestamp": 56789,
    "pumps_in_cycle": 1
}

with open("src/state.json", "w") as file:
    json.dump(values, file)


    save_controller_data(data)