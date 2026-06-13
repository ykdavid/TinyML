import csv
import os
import time
from pathlib import Path
from datetime import datetime

import serial

# 修改成你的端口，例如 /dev/cu.usbmodem1201
PORT = "/dev/cu.usbmodem1201"
BAUD_RATE = 115200

ROOT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_CSV = ROOT_DIR / "data" / "raw_imu.csv"
RECORD_SECONDS = 2.0

# 每个 label 的目标 trial 数；只用于显示进度，不影响采集
TARGET_TRIALS_PER_LABEL = 50

LABELS = [
    "swipe_left",
    "swipe_right",
    "move_up",
    "move_down",
    "circle",
    "idle",
]


FIELDNAMES = [
    "trial_id",
    "label",
    "sample_index",
    "t_ms",
    "ax",
    "ay",
    "az",
    "gx",
    "gy",
    "gz",
]


def ensure_output_file(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def count_trials_by_label(path: Path) -> dict[str, int]:
    """
    Count how many completed trials each label has in the CSV.

    Important:
    - This counts unique trial_id values, not CSV rows.
    - One 2-second trial usually contains about 100 rows.
    """
    trial_ids_by_label = {label: set() for label in LABELS}

    if not path.exists() or path.stat().st_size == 0:
        return {label: 0 for label in LABELS}

    with open(path, "r", newline="") as f:
        reader = csv.DictReader(f)

        if not reader.fieldnames:
            return {label: 0 for label in LABELS}

        if "label" not in reader.fieldnames or "trial_id" not in reader.fieldnames:
            raise ValueError(
                f"{path} must contain 'label' and 'trial_id' columns. "
                f"Current columns: {reader.fieldnames}"
            )

        for row in reader:
            label = row.get("label", "").strip()
            trial_id = row.get("trial_id", "").strip()

            if label in trial_ids_by_label and trial_id:
                trial_ids_by_label[label].add(trial_id)

    return {label: len(trial_ids) for label, trial_ids in trial_ids_by_label.items()}


def print_collection_status(path: Path) -> None:
    counts = count_trials_by_label(path)

    print("\nCurrent trial counts:")
    for i, label in enumerate(LABELS):
        print(f"{i}: {label:<12} {counts[label]:>3}/{TARGET_TRIALS_PER_LABEL}")

    total_trials = sum(counts.values())
    target_total = TARGET_TRIALS_PER_LABEL * len(LABELS)
    print(f"Total trials: {total_trials}/{target_total}")


def parse_imu_line(line: str):
    """
    Expected Arduino line:
    t_ms,ax,ay,az,gx,gy,gz
    """
    line = line.strip()

    if not line or line.startswith("#"):
        return None

    parts = line.split(",")
    if len(parts) != 7:
        return None

    try:
        t_ms = int(parts[0])
        values = [float(x) for x in parts[1:]]
    except ValueError:
        return None

    return t_ms, values


def record_one_trial(ser: serial.Serial, label: str) -> int:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    trial_id = f"{label}_{timestamp}"

    counts_before = count_trials_by_label(OUTPUT_CSV)
    print(
        f"\nCurrent '{label}' trials before recording: {counts_before[label]}/{TARGET_TRIALS_PER_LABEL}"
    )

    print(f"\nPrepare gesture: {label}")
    print("Start from a neutral position.")
    input("Press Enter, then perform the gesture after the countdown...")

    for i in [3, 2, 1]:
        print(i)
        time.sleep(1)

    print("Recording...")

    # Clear any old data before starting
    ser.reset_input_buffer()
    time.sleep(0.1)
    ser.reset_input_buffer()

    # Tell Arduino to start streaming
    ser.write(b"S\n")
    ser.flush()

    rows = []
    start_time = time.monotonic()
    sample_index = 0

    try:
        while time.monotonic() - start_time < RECORD_SECONDS:
            raw = ser.readline().decode("utf-8", errors="ignore")
            parsed = parse_imu_line(raw)

            if parsed is None:
                continue

            t_ms, values = parsed
            ax, ay, az, gx, gy, gz = values

            rows.append(
                {
                    "trial_id": trial_id,
                    "label": label,
                    "sample_index": sample_index,
                    "t_ms": t_ms,
                    "ax": ax,
                    "ay": ay,
                    "az": az,
                    "gx": gx,
                    "gy": gy,
                    "gz": gz,
                }
            )

            sample_index += 1

    finally:
        # Tell Arduino to stop streaming
        ser.write(b"E\n")
        ser.flush()

    with open(OUTPUT_CSV, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerows(rows)

    print(f"Saved {len(rows)} samples for trial {trial_id}")
    print(f"CSV path: {OUTPUT_CSV}")

    expected = int(RECORD_SECONDS * 50)
    if len(rows) < expected * 0.7 or len(rows) > expected * 1.3:
        print(
            f"Warning: expected about {expected} samples, "
            f"but got {len(rows)}. Check serial streaming or sampling rate."
        )

    counts_after = count_trials_by_label(OUTPUT_CSV)
    print(
        f"Updated '{label}' trials after recording: {counts_after[label]}/{TARGET_TRIALS_PER_LABEL}"
    )
    print_collection_status(OUTPUT_CSV)

    return len(rows)


def main():
    ensure_output_file(OUTPUT_CSV)

    print("Allowed labels:")
    for i, label in enumerate(LABELS):
        print(f"{i}: {label}")

    print_collection_status(OUTPUT_CSV)

    print(f"\nOpening serial port: {PORT}")
    print("Make sure Arduino Serial Monitor is closed.")

    with serial.Serial(PORT, BAUD_RATE, timeout=1) as ser:
        time.sleep(2)
        ser.reset_input_buffer()
        ser.write(b"E\n")
        ser.flush()
        time.sleep(0.2)
        ser.reset_input_buffer()

        while True:
            counts = count_trials_by_label(OUTPUT_CSV)
            user_input = input(
                "\nEnter label number/name, s to show counts, or q to quit: "
            ).strip()

            if user_input.lower() == "q":
                break

            if user_input.lower() == "s":
                print_collection_status(OUTPUT_CSV)
                continue

            if user_input.isdigit():
                idx = int(user_input)
                if idx < 0 or idx >= len(LABELS):
                    print("Invalid label number.")
                    continue
                label = LABELS[idx]
            else:
                label = user_input

            if label not in LABELS:
                print(f"Invalid label. Choose from: {LABELS}")
                continue

            print(
                f"Selected label: {label} ({counts[label]}/{TARGET_TRIALS_PER_LABEL} trials collected)"
            )
            record_one_trial(ser, label)

    print(f"\nDone. Data saved to {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
