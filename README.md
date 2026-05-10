# Fishing Minigame Macro — Setup Guide

Choose whichever method you prefer:

- **Method 1 — Command Prompt:** Simpler, no extra software needed
- **Method 2 — VS Code:** Better if you want to view or edit the script yourself

---

# METHOD 1 — Command Prompt

## What You Need Before Starting

- A Windows computer
- The `fishing_macro.py` file (put it on your Desktop)

---

## Step 1 — Install Python

1. Open your web browser and go to: **python.org/downloads**
2. Click the big yellow button that says **"Download Python 3.x.x"**
3. Once it finishes downloading, open the file
4. ⚠️ **IMPORTANT** — before clicking anything, look at the bottom of the installer and tick the box that says **"Add python.exe to PATH"**
5. Click **"Install Now"**
6. Wait for it to finish, then click **Close**

---

## Step 2 — Open Command Prompt

1. Press the **Windows key** on your keyboard (the key with the Windows logo on it)
2. Type **cmd**
3. Press **Enter**
4. A black window will open — this is Command Prompt, this is where you will type commands

---

## Step 3 — Install the Required Libraries

1. Click inside the black Command Prompt window
2. Type the following exactly and press **Enter:**

```
pip install mss opencv-python pyautogui numpy
```

3. A bunch of text will scroll by — just wait until it stops and you can type again. This may take a minute or two.

---

## Step 4 — Navigate to the Script

1. In the Command Prompt window, type the following and press **Enter:**

```
cd Desktop
```

This tells the computer to look at your Desktop where the script is saved.

---

## Step 5 — Run the Script

1. Type the following and press **Enter:**

```
python fishing_macro.py
```

2. A menu will appear with 3 options

---

## Step 6 — Calibrate First (Do This Every Time You Move the Game Window)

1. Make sure your game is open and visible on your screen
2. Type **1** and press **Enter**
3. A screenshot of your screen will open in a new window
4. **Click 1:** Click the very **center** of the spinning circle, then press any key on your keyboard
5. **Click 2:** Click the **outer edge** of the ring, then press any key
6. **Click 3:** Click the **inner edge** of the ring, then press any key
7. The window will close and you will see **"Calibration saved!"** in the Command Prompt

---

## Step 7 — Run the Macro

1. It will ask **"Run the macro now? (y/n)"** — type **y** and press **Enter**
2. You have **4 seconds** to click on your game window before it starts watching
3. A small debug window will pop up showing what the macro is detecting in real time
4. The macro will now automatically click for you when the red bar reaches the white zone!

---

## How to Stop the Macro

You have two options:

- Press **Q** while the debug window is selected
- Move your mouse to the **very top-left corner** of your screen (emergency stop)

---

## Running It Again Later

Every time you want to use the macro again:

1. Open Command Prompt (Windows key → type cmd → Enter)
2. Type `cd Desktop` and press **Enter**
3. Type `python fishing_macro.py` and press **Enter**
4. Choose option **2** to run (you only need to calibrate again if you moved the game window)

---

## Troubleshooting (Command Prompt)

- **"python is not recognized"** — Python was not installed correctly. Go back to Step 1 and make sure you ticked the **"Add python.exe to PATH"** box before installing.
- **"No module named mss"** — The libraries were not installed. Go back to Step 3 and run the pip install command again.
- **The macro is clicking at the wrong time** — Run calibration again (option 1) and make sure you click the center and edges of the circle as precisely as possible.
- **It took a screenshot of the wrong monitor** — Let whoever set this up for you know and they can adjust the monitor setting in the script.

---
---

# METHOD 2 — VS Code

## What You Need Before Starting

- A Windows computer
- The `fishing_macro.py` file (put it on your Desktop)

---

## Step 1 — Install Python

1. Open your web browser and go to: **python.org/downloads**
2. Click the big yellow button that says **"Download Python 3.x.x"**
3. Once it finishes downloading, open the file
4. ⚠️ **IMPORTANT** — before clicking anything, look at the bottom of the installer and tick the box that says **"Add python.exe to PATH"**
5. Click **"Install Now"**
6. Wait for it to finish, then click **Close**

---

## Step 2 — Install VS Code

1. Open your web browser and go to: **code.visualstudio.com**
2. Click the big blue **"Download for Windows"** button
3. Once it finishes downloading, open the file and follow the installer
4. When asked, tick the box that says **"Add to PATH"** if it appears
5. Click through until it says **Finish**

---

## Step 3 — Install the Python Extension in VS Code

1. Open VS Code
2. On the left side there is a column of icons — click the one that looks like 4 squares (it is called Extensions)
3. In the search bar that appears, type **Python**
4. Click the one made by **Microsoft** (it should be the first result)
5. Click the blue **Install** button
6. Wait for it to finish

---

## Step 4 — Open the Script in VS Code

1. In VS Code, click **File** at the top left
2. Click **Open File**
3. Find `fishing_macro.py` on your Desktop and click it
4. Click **Open**
5. The code will appear in the editor

---

## Step 5 — Open the Terminal in VS Code

1. At the top of VS Code, click **Terminal**
2. Click **New Terminal**
3. A panel will appear at the bottom of the screen — this is where you type commands

---

## Step 6 — Install the Required Libraries

1. Click inside the terminal panel at the bottom
2. Type the following exactly and press **Enter:**

```
pip install mss opencv-python pyautogui numpy
```

3. A bunch of text will scroll by — just wait until it stops and you can type again. This may take a minute or two.

---

## Step 7 — Run the Script

1. In the terminal at the bottom, type the following and press **Enter:**

```
python fishing_macro.py
```

2. A menu will appear with 3 options

---

## Step 8 — Calibrate First (Do This Every Time You Move the Game Window)

1. Make sure your game is open and visible on your screen
2. Type **1** and press **Enter**
3. A screenshot of your screen will open in a new window
4. **Click 1:** Click the very **center** of the spinning circle, then press any key on your keyboard
5. **Click 2:** Click the **outer edge** of the ring, then press any key
6. **Click 3:** Click the **inner edge** of the ring, then press any key
7. The window will close and you will see **"Calibration saved!"** in the terminal

---

## Step 9 — Run the Macro

1. It will ask **"Run the macro now? (y/n)"** — type **y** and press **Enter**
2. You have **4 seconds** to click on your game window before it starts watching
3. A small debug window will pop up showing what the macro is detecting in real time
4. The macro will now automatically click for you when the red bar reaches the white zone!

---

## How to Stop the Macro

You have two options:

- Press **Q** while the debug window is selected
- Move your mouse to the **very top-left corner** of your screen (emergency stop)

---

## Running It Again Later

Every time you want to use the macro again:

1. Open VS Code
2. Click **Terminal → New Terminal**
3. Type `python fishing_macro.py` and press **Enter**
4. Choose option **2** to run (you only need to calibrate again if you moved the game window)

---

## Troubleshooting (VS Code)

- **"python is not recognized"** — Python was not installed correctly. Go back to Step 1 and make sure you ticked the **"Add python.exe to PATH"** box before installing. Then restart VS Code.
- **"No module named mss"** — The libraries were not installed. Go back to Step 6 and run the pip install command again.
- **The macro is clicking at the wrong time** — Run calibration again (option 1) and make sure you click the center and edges of the circle as precisely as possible.
- **It took a screenshot of the wrong monitor** — Let whoever set this up for you know and they can adjust the monitor setting in the script.

---

*If anything else goes wrong, screenshot the terminal window and send it to whoever gave you this script!*
