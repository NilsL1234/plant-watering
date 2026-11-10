# Project: PLANT-WATERING

## 1. Project Overview

This plant-watering-system is designed to automate the watering of a plant. It uses a Raspberry Pi 5 as the controlling unit.
A 12 V DC Perestaltic Pump is used to transport the water through a tube to the plant. The system uses a humidity sensor to observe when watering is required.

The raspberry pi controls the 12 V pump via a GPIO pin that drives a MOSFET. For the sensor data the Pi is in contact with a ADC-Converter (MCP3008) 
that converts the analog sensor data into a digital one. The communication between the Converter and the Pi happens via SPI.
The code is written in python. The Logic is implemented via a state maschine that represents the current status like measuring or pumping.

## 2. Hardware Components

## Hardware Components

| Component | Description |
|---|---|
| Raspberry Pi 5 | Main controller running Raspberry Pi OS |
| MCP3008 | 10-bit ADC with SPI interface |
| Soil Moisture Sensor | Analog sensor with interface module |
| 12 V DC Peristaltic Pump | Pumps water to the plant |
| DFRobot MOSFET Module | Controls the pump via a GPIO signal |
| 12 V Power Supply | External power supply for the pump |
| Flyback Diode | Protects against voltage spikes from the pump motor |
| Breadboard & Jumper Wires | Electrical connections between components |

## 3. Hardware Setup / Wiring

## 4. Software Architecture

## 5. Watering Logic & Calibration

## 6. Installation & Setup

## 7. Automatic Startup (systemd)

## 8. Error Handling & Safety

## 9. Testing

## 10. Project Stucture