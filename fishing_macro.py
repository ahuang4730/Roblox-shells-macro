"""
Fishing Minigame Macro - Scout & Predict Version
=================================================
HOW TO USE:
1. Install dependencies (run once in terminal):
      pip install mss opencv-python pyautogui numpy

2. Run this script:
      python fishing_macro.py

3. Choose option 1 to calibrate first, then option 2 to run.

EMERGENCY STOP: Move mouse to the TOP-LEFT corner of your screen.

HOW IT WORKS:
  Phase 1 - Scout:   Finds the white zone angle at the start of each round.
  Phase 2 - Track:   Watches the red bar for a couple rotations to measure speed/direction.
  Phase 3 - Predict: Calculates exactly when the bar will hit the white zone and clicks then.
  Phase 4 - Reset:   Detects direction reversal after a click, then scouts again for new round.
"""

import mss
import cv2
import numpy as np
import pyautogui
import time
import math
import json
import os
from collections import deque

pyautogui.FAILSAFE = True

SAVE_FILE = "fishing_macro_config.json"

# ── How many milliseconds of system click lag to compensate for ──
CLICK_LAG_MS = 15

# ── How many frames to average speed over (smoothing) ──
SPEED_HISTORY = 8

# ── Minimum red pixels to consider the bar "found" ──
MIN_RED_PIXELS = 50
# ── Minimum white pixels on ring to consider it a valid white zone ──
MIN_WHITE_PIXELS = 80

# ── If white zone jumps more than this many degrees, treat as new round ──
WHITE_JUMP_THRESHOLD = 25

# ── If direction flips, treat as new round ──
# (a flip means the sign of angular velocity reversed)

# ── Cooldown after a click before we start scouting again (seconds) ──
POST_CLICK_COOLDOWN = 0.4


# ─────────────────────────────────────────────────────────────
#  COLOR RANGES (HSV)
# ─────────────────────────────────────────────────────────────

# Red bar (two ranges because red wraps in HSV)
RED_LO1 = np.array([0,   140, 140])
RED_HI1 = np.array([12,  255, 255])
RED_LO2 = np.array([160, 140, 140])
RED_HI2 = np.array([180, 255, 255])

# White zone — strict so we don't pick up off-whites or grey
WHITE_LO = np.array([0,   0, 210])
WHITE_HI = np.array([180, 25, 255])


# ─────────────────────────────────────────────────────────────
#  CALIBRATION
# ─────────────────────────────────────────────────────────────

def calibrate():
    print("\n=== CALIBRATION ===")
    print("Make sure your game is visible on screen.")
    input("Press Enter to take a screenshot...")
    time.sleep(0.5)

    with mss.mss() as sct:
        monitor = sct.monitors[3]
        raw = sct.grab(monitor)
        screenshot = np.array(raw)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    # Store monitor offset so we can map screenshot coords to real screen coords
    mon_left = sct.monitors[3]["left"]
    mon_top  = sct.monitors[3]["top"]

    clicks = []
    instructions = [
        "CLICK 1: Click the CENTER of the spinning circle",
        "CLICK 2: Click the OUTER EDGE of the ring",
        "CLICK 3: Click the INNER EDGE of the ring",
    ]

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            clicks.append((x, y))
            cv2.circle(screenshot, (x, y), 8, (0, 255, 0), -1)
            cv2.circle(screenshot, (x, y), 8, (255, 255, 255), 2)
            cv2.imshow("Calibration", screenshot)

    cv2.namedWindow("Calibration", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Calibration", 1280, 720)
    cv2.setMouseCallback("Calibration", mouse_callback)

    for instruction in instructions:
        display = screenshot.copy()
        cv2.rectangle(display, (0, 0), (1000, 60), (30, 30, 30), -1)
        cv2.putText(display, instruction + " — then press any key", (10, 38),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.85, (0, 255, 180), 2)
        for c in clicks:
            cv2.circle(display, c, 8, (0, 255, 0), -1)
            cv2.circle(display, c, 8, (255, 255, 255), 2)
        cv2.imshow("Calibration", display)

        prev_len = len(clicks)
        while len(clicks) == prev_len:
            cv2.waitKey(50)

    cv2.destroyAllWindows()

    center_x, center_y = clicks[0]
    outer_x,  outer_y  = clicks[1]
    inner_x,  inner_y  = clicks[2]

    outer_radius = math.dist((center_x, center_y), (outer_x, outer_y))
    inner_radius = math.dist((center_x, center_y), (inner_x, inner_y))

    radius    = int((outer_radius + inner_radius) / 2)
    thickness = max(int(outer_radius - inner_radius), 20) + 10

    # Convert screenshot coords to real screen coords
    real_cx = center_x + mon_left
    real_cy = center_y + mon_top

    config = {
        "center_x":  real_cx,
        "center_y":  real_cy,
        "radius":    radius,
        "thickness": thickness,
        "mon_index": 3,
    }

    with open(SAVE_FILE, "w") as f:
        json.dump(config, f, indent=2)

    print(f"\n  Calibration saved!")
    print(f"  Screen center: ({real_cx}, {real_cy})")
    print(f"  Radius:        {radius}px")
    print(f"  Thickness:     {thickness}px")

    return config


def load_config():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r") as f:
        return json.load(f)


# ─────────────────────────────────────────────────────────────
#  GEOMETRY HELPERS
# ─────────────────────────────────────────────────────────────

def pixel_to_angle(px, py, cx, cy):
    """Returns angle in degrees (0 = right, clockwise positive)."""
    angle = math.degrees(math.atan2(py - cy, px - cx))
    return angle % 360


def angle_diff(a, b):
    """Signed difference from angle a to angle b, in [-180, 180]."""
    diff = (b - a) % 360
    if diff > 180:
        diff -= 360
    return diff


def angle_in_zone(angle, zone_center, zone_half_width):
    """Check if angle is within zone_center ± zone_half_width."""
    return abs(angle_diff(zone_center, angle)) <= zone_half_width


def find_centroid_angle(mask, cx, cy):
    """Find the average angle of all white pixels in mask, relative to (cx, cy)."""
    coords = cv2.findNonZero(mask)
    if coords is None or len(coords) < MIN_WHITE_PIXELS:
        return None, 0
    pts = coords[:, 0, :]
    avg_x = pts[:, 0].mean()
    avg_y = pts[:, 1].mean()
    angle = pixel_to_angle(avg_x, avg_y, cx, cy)
    return angle, len(coords)


# ─────────────────────────────────────────────────────────────
#  MAIN MACRO
# ─────────────────────────────────────────────────────────────

def run_macro(config):
    cx        = config["center_x"]
    cy        = config["center_y"]
    radius    = config["radius"]
    thickness = config["thickness"]
    mon_index = config.get("mon_index", 1)

    print(f"\n=== MACRO RUNNING ===")
    print(f"Circle center: ({cx}, {cy})  Radius: {radius}px")
    print(f"Starting in 4 seconds — switch to your game window!")
    print(f"Press Q in the debug window to stop.\n")
    time.sleep(4)

    # Capture region around the circle
    pad = radius + thickness + 30
    region = {
        "top":    cy - pad,
        "left":   cx - pad,
        "width":  pad * 2,
        "height": pad * 2,
    }

    # Center within the captured region
    rcx = pad
    rcy = pad

    # Build ring mask — only look at pixels ON the ring band
    ring_mask = np.zeros((pad * 2, pad * 2), dtype=np.uint8)
    cv2.circle(ring_mask, (rcx, rcy), radius + thickness // 2, 255, thickness)

    # ── State machine ──
    STATE_SCOUT   = "SCOUT"    # finding white zone
    STATE_TRACK   = "TRACK"    # measuring red bar speed
    STATE_PREDICT = "PREDICT"  # waiting for right moment to click
    STATE_COOLDOWN = "COOLDOWN" # just clicked, waiting before next scout

    state = STATE_SCOUT

    white_zone_angle  = None   # locked-in white zone angle for this round
    prev_white_angle  = None   # to detect jumps

    red_angle_history = deque(maxlen=SPEED_HISTORY)  # recent red angles
    speed_history     = deque(maxlen=SPEED_HISTORY)  # recent speeds (deg/frame)
    prev_red_angle    = None
    prev_direction    = None   # +1 clockwise, -1 counter-clockwise

    last_click_time   = 0
    frame_times       = deque(maxlen=10)  # for measuring actual FPS

    print(f"State: SCOUT — looking for white zone...")

    with mss.mss() as sct:
        while True:
            t0 = time.time()

            # ── Grab frame ──
            raw   = sct.grab(region)
            frame = np.array(raw)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            hsv   = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # ── Detect red bar on ring ──
            red1        = cv2.inRange(hsv, RED_LO1, RED_HI1)
            red2        = cv2.inRange(hsv, RED_LO2, RED_HI2)
            red_on_ring = cv2.bitwise_and(cv2.bitwise_or(red1, red2), ring_mask)

            red_coords  = cv2.findNonZero(red_on_ring)
            red_angle   = None
            if red_coords is not None and len(red_coords) >= MIN_RED_PIXELS:
                pts     = red_coords[:, 0, :]
                red_angle = pixel_to_angle(pts[:, 0].mean(), pts[:, 1].mean(), rcx, rcy)

            # ── Detect white zone on ring ──
            white_on_ring = cv2.bitwise_and(
                cv2.inRange(hsv, WHITE_LO, WHITE_HI), ring_mask)
            current_white_angle, white_count = find_centroid_angle(
                white_on_ring, rcx, rcy)

            # ── Detect new round (white zone jumped or direction reversed) ──
            new_round = False
            if current_white_angle is not None and prev_white_angle is not None:
                if abs(angle_diff(prev_white_angle, current_white_angle)) > WHITE_JUMP_THRESHOLD:
                    new_round = True
                    print(f"  New round detected! White zone moved: "
                          f"{prev_white_angle:.1f} -> {current_white_angle:.1f}")

            if current_white_angle is not None:
                prev_white_angle = current_white_angle

            # ── Track red bar speed and direction ──
            current_speed     = None
            current_direction = None
            if red_angle is not None and prev_red_angle is not None:
                diff = angle_diff(prev_red_angle, red_angle)
                current_speed     = diff          # deg/frame (signed)
                current_direction = 1 if diff >= 0 else -1

                # Detect direction reversal → new round
                if prev_direction is not None and current_direction != prev_direction:
                    if abs(diff) > 2:  # ignore tiny jitter
                        new_round = True
                        print(f"  New round detected! Bar reversed direction.")

                speed_history.append(current_speed)

            if red_angle is not None:
                prev_red_angle    = red_angle
                prev_direction    = current_direction

            # ── Handle new round ──
            if new_round and state != STATE_COOLDOWN:
                state            = STATE_SCOUT
                white_zone_angle = None
                red_angle_history.clear()
                speed_history.clear()
                prev_red_angle   = None
                prev_direction   = None
                print(f"State: SCOUT — finding new white zone...")

            # ── Measure actual ms per frame ──
            frame_times.append(time.time() - t0)
            ms_per_frame = (sum(frame_times) / len(frame_times)) * 1000

            # ═══════════════════════════════
            #  STATE MACHINE
            # ═══════════════════════════════

            if state == STATE_SCOUT:
                # Lock in white zone as soon as we see it clearly
                if current_white_angle is not None and white_count >= MIN_WHITE_PIXELS:
                    white_zone_angle = current_white_angle
                    state = STATE_TRACK
                    print(f"State: TRACK — white zone at {white_zone_angle:.1f}°, "
                          f"measuring speed...")

            elif state == STATE_TRACK:
                # Collect speed samples, then move to predict
                if red_angle is not None:
                    red_angle_history.append(red_angle)

                if len(speed_history) >= SPEED_HISTORY:
                    avg_speed = sum(speed_history) / len(speed_history)
                    if abs(avg_speed) > 0.1:  # bar is actually moving
                        state = STATE_PREDICT
                        print(f"State: PREDICT — speed: {avg_speed:.2f} deg/frame, "
                              f"white zone: {white_zone_angle:.1f}°")

            elif state == STATE_PREDICT:
                if red_angle is not None and white_zone_angle is not None and len(speed_history) >= 3:
                    avg_speed = sum(speed_history) / len(speed_history)

                    if abs(avg_speed) > 0.1:
                        # How many degrees until we reach the white zone?
                        degrees_to_go = angle_diff(red_angle, white_zone_angle)

                        # Are we going the right direction?
                        going_right_way = (avg_speed > 0 and degrees_to_go > 0) or \
                                          (avg_speed < 0 and degrees_to_go < 0)

                        if not going_right_way:
                            # Need to go the long way around
                            if degrees_to_go > 0:
                                degrees_to_go -= 360
                            else:
                                degrees_to_go += 360

                        # How many frames until arrival?
                        frames_to_go = degrees_to_go / avg_speed

                        # Convert click lag to frames
                        lag_frames = CLICK_LAG_MS / max(ms_per_frame, 1)

                        # Click when we're lag_frames away from the white zone
                        if 0 <= frames_to_go <= lag_frames:
                            pyautogui.click()
                            last_click_time = time.time()
                            state = STATE_COOLDOWN
                            print(f"  CLICKED! Red: {red_angle:.1f}°  "
                                  f"White: {white_zone_angle:.1f}°  "
                                  f"Speed: {avg_speed:.2f} deg/frame")

            elif state == STATE_COOLDOWN:
                # Wait a moment after clicking before scouting again
                if time.time() - last_click_time > POST_CLICK_COOLDOWN:
                    state = STATE_SCOUT
                    white_zone_angle = None
                    red_angle_history.clear()
                    speed_history.clear()
                    prev_red_angle  = None
                    prev_direction  = None
                    print(f"State: SCOUT — ready for next round...")

            # If nothing has been clicked in 5 seconds, click to restart the minigame
            if time.time() - last_click_time > 3.5 and last_click_time != 0:
                pyautogui.click()
                last_click_time = time.time()
                print(f"  Auto-restarting minigame...")

            # ═══════════════════════════════
            #  DEBUG WINDOW
            # ═══════════════════════════════

            debug = frame.copy()

            # Draw ring band
            cv2.circle(debug, (rcx, rcy), radius + thickness // 2,
                       (60, 60, 60), thickness)

            # Draw detected white zone in green
            white_display = cv2.cvtColor(white_on_ring, cv2.COLOR_GRAY2BGR)
            white_display[:, :, 0] = 0
            white_display[:, :, 2] = 0
            debug = cv2.addWeighted(debug, 1.0, white_display, 1.0, 0)

            # Draw locked white zone as a green arc marker
            if white_zone_angle is not None:
                rad = math.radians(white_zone_angle)
                wx  = int(rcx + radius * math.cos(rad))
                wy  = int(rcy + radius * math.sin(rad))
                cv2.circle(debug, (wx, wy), 10, (0, 255, 80), 3)

            # Draw red bar highlight
            red_display = cv2.cvtColor(red_on_ring, cv2.COLOR_GRAY2BGR)
            red_display[:, :, 0] = 0
            red_display[:, :, 1] = 0
            debug = cv2.addWeighted(debug, 1.0, red_display, 1.5, 0)

            # Draw red angle line
            if red_angle is not None:
                rad  = math.radians(red_angle)
                tip_x = int(rcx + radius * math.cos(rad))
                tip_y = int(rcy + radius * math.sin(rad))
                cv2.line(debug, (rcx, rcy), (tip_x, tip_y), (0, 80, 255), 2)

            # Status text
            avg_spd = (sum(speed_history) / len(speed_history)) if speed_history else 0
            lines = [
                f"State: {state}",
                f"Red: {red_angle:.1f}" if red_angle is not None else "Red: --",
                f"White zone: {white_zone_angle:.1f}" if white_zone_angle else "White zone: --",
                f"Speed: {avg_spd:.2f} deg/frame",
                f"Frame: {ms_per_frame:.1f}ms",
            ]
            cv2.rectangle(debug, (0, 0), (260, 18 + 22 * len(lines)), (20, 20, 20), -1)
            for i, line in enumerate(lines):
                col = (0, 255, 100) if state == STATE_PREDICT else (180, 220, 255)
                cv2.putText(debug, line, (6, 18 + 22 * i),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, col, 1)

            cv2.imshow("Fishing Macro (Q to stop)", debug)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            time.sleep(0.002)

    cv2.destroyAllWindows()
    print("\nStopped.")


# ─────────────────────────────────────────────────────────────
#  MENU
# ─────────────────────────────────────────────────────────────

def main():
    print("========================================")
    print("    Fishing Minigame Macro v2.0         ")
    print("========================================")

    config = load_config()

    if config:
        print(f"\n  Found saved calibration")
        print(f"  Center: ({config['center_x']}, {config['center_y']})")
    else:
        print("\n  No calibration found. Please run option 1 first.")

    print("\n  1)  Calibrate  (do this first, or if you moved the game window)")
    print("  2)  Run the macro")
    print("  3)  Exit")

    choice = input("\nEnter 1, 2, or 3: ").strip()

    if choice == "1":
        config = calibrate()
        again = input("\nRun the macro now? (y/n): ").strip().lower()
        if again == "y":
            run_macro(config)

    elif choice == "2":
        if not config:
            print("\n  No calibration found. Please run option 1 first.")
        else:
            run_macro(config)

    elif choice == "3":
        print("Bye!")

    else:
        print("Please enter 1, 2, or 3.")
        main()


if __name__ == "__main__":
    main()