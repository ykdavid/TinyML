# TinyGesture: IMU Gesture Recognition on Arduino Nano 33 BLE Sense

## Project Overview

This project implements a TinyML-based IMU gesture recognition system using the Arduino Nano 33 BLE Sense and Edge Impulse. The system uses onboard IMU acceleration and gyroscope data to classify hand gestures, then maps the predicted gesture to the onboard RGB LED for real-time feedback.

The supported gesture classes are:

- idle
- circle
- move_down
- move_up
- swipe_left
- swipe_right

## Hardware

- Arduino Nano 33 BLE Sense
- USB cable
- Onboard IMU sensor
- Onboard RGB LED

No external soldering is required for the final demo because the onboard RGB LED is used.

## Repository Structure

```text
TinyML/
├── README.md
├── arduino/
│   └── tinygestrue_onboard_rgb_demo.ino
├── data/
│   └── raw_imu.csv
├── docs/
│   ├── 1.jpg
│   ├── 2.png
│   └── 3.png
├── python/
│   └── collect_imu.py
└── ei-tinygesture-imu-gesture-control-arduino-1.0.2-impulse-#1.zip
```

## Data Collection

The IMU data was collected from the Arduino Nano 33 BLE Sense using the onboard accelerometer and gyroscope.

The Python data collection script is located at:

```text
python/collect_imu.py
```

The collected raw IMU dataset is located at:

```text
data/raw_imu.csv
```

## Edge Impulse Training

The gesture classifier was trained using Edge Impulse.

Main Edge Impulse settings:

- Sensor type: IMU
- Window size: 2000 ms
- Processing block: Spectral features
- Learning block: Classification
- Deployment target: Arduino library
- Inference engine: EON Compiler
- Deployment model: Quantized int8 model

The exported Edge Impulse Arduino library is included in this repository:

```text
ei-tinygesture-imu-gesture-control-arduino-1.0.2-impulse-#1.zip
```

## Arduino Deployment

1. Open Arduino IDE.
2. Install the Arduino Nano 33 BLE board package if it is not already installed.
3. Install the Edge Impulse exported Arduino library:

```text
Sketch → Include Library → Add .ZIP Library
```

4. Select the exported ZIP file:

```text
ei-tinygesture-imu-gesture-control-arduino-1.0.2-impulse-#1.zip
```

5. Open the final Arduino demo sketch:

```text
arduino/tinygestrue_onboard_rgb_demo.ino
```

6. Select the board:

```text
Arduino Nano 33 BLE Sense
```

7. Select the correct USB port.
8. Upload the sketch to the board.
9. Open Serial Monitor to view prediction results.

## Demo Behavior

The Arduino collects IMU data over a sampling window, runs inference using the Edge Impulse model, and updates the onboard RGB LED based on the predicted gesture.

Example LED mapping:

| Gesture | LED Behavior |
|---|---|
| idle | LED off or white |
| circle | purple |
| move_down | yellow |
| move_up | blue |
| swipe_left | green |
| swipe_right | red |

## Documentation

The `docs/` folder contains screenshots related to the Edge Impulse workflow and project results:

```text
docs/1.jpg
docs/2.png
docs/3.png
```

## Reproduction Steps

To reproduce the project:

1. Clone or download this repository.
2. Open Arduino IDE.
3. Install the Arduino Nano 33 BLE board package.
4. Install the Edge Impulse Arduino ZIP library from the repository root.
5. Open and upload the final Arduino sketch from `arduino/tinygestrue_onboard_rgb_demo.ino`.
6. Open Serial Monitor.
7. Perform one of the supported gestures and observe the predicted label and LED output.

## Notes

In testing, the model performed best on `circle`, `idle`, and `move_down`. Some confusion remained between `move_up` and `move_down`, and between `swipe_left` and `swipe_right`.

## Authors

EEP564 Final Project Team
