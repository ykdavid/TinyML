# TinyGesture: IMU Gesture Recognition on Arduino Nano 33 BLE Sense

## Project Overview

This project implements a TinyML-based IMU gesture recognition system using the Arduino Nano 33 BLE Sense and Edge Impulse. The system uses onboard IMU acceleration and gyroscope data to classify hand gestures, then maps the predicted gesture to the onboard RGB LED for real-time feedback.

The gesture classes are:

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
│   ├── imu_streamer/
│   │   └── imu_streamer.ino
│   └── tinygesture_onboard_rgb_demo/
│       └── tinygesture_onboard_rgb_demo.ino
├── python/
│   └── collect_imu.py
├── edge_impulse/
│   ├── edge_impulse_trials/
│   └── tinygesture_edge_impulse_arduino_library.zip
├── data/
│   └── raw_imu.csv
└── docs/
    └── screenshots/
```

## Data Collection

The IMU data was collected from the Arduino Nano 33 BLE Sense using the onboard accelerometer and gyroscope.

To collect data, upload the IMU streaming Arduino sketch:

```text
arduino/imu_streamer/imu_streamer.ino
```

Then run the Python script:

```bash
cd python
python collect_imu.py
```

The collected raw IMU data is stored in:

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

The exported Edge Impulse Arduino library is included here:

```text
edge_impulse/tinygesture_edge_impulse_arduino_library.zip
```

## Arduino Deployment

1. Open Arduino IDE.
2. Install the Arduino Nano 33 BLE board package if it is not already installed.
3. Install the Edge Impulse exported Arduino library:

```text
Sketch → Include Library → Add .ZIP Library
```

4. Select the ZIP file:

```text
edge_impulse/tinygesture_edge_impulse_arduino_library.zip
```

5. Open the final demo sketch:

```text
arduino/tinygesture_onboard_rgb_demo/tinygesture_onboard_rgb_demo.ino
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

## Reproduction Steps

To reproduce the project:

1. Clone or download this repository.
2. Open Arduino IDE.
3. Install the Arduino Nano 33 BLE board package.
4. Install the Edge Impulse Arduino ZIP library from the `edge_impulse/` folder.
5. Open and upload the final Arduino sketch from `arduino/tinygesture_onboard_rgb_demo/`.
6. Open Serial Monitor.
7. Perform one of the supported gestures and observe the predicted label and LED output.

## Notes

In testing, the model performed best on `circle`, `idle`, and `move_down`. Some confusion remained between `move_up` and `move_down`, and between `swipe_left` and `swipe_right`.

## Authors

EEP564 Final Project Team
