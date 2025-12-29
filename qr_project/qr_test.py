import cv2
from pyzbar import pyzbar
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog
import os
import sqlite3
import csv
from datetime import datetime
import winsound

# ================= CONFIG =================
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
DB_NAME = "scan_history.db"
CSV_FILE = "scan_history.csv"
# ==========================================

# Store scanned codes (avoid duplicates)
scanned_codes = set()

# ================= DATABASE SETUP =================
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS scans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code_data TEXT,
    code_type TEXT,
    source TEXT,
    scan_time TEXT
)
""")
conn.commit()

# ================= CSV SETUP =================
with open(CSV_FILE, "a", newline="") as file:
    writer = csv.writer(file)
    if file.tell() == 0:
        writer.writerow(["Code Data", "Code Type", "Source", "Scan Time"])

# ================= GUI SETUP =================
root = tk.Tk()
root.title("QR & Barcode Scanner")
root.geometry("700x400")

title = tk.Label(root, text="QR & Barcode Scanner", font=("Arial", 16, "bold"))
title.pack(pady=10)

table = ttk.Treeview(
    root,
    columns=("Type", "Data", "Source", "Time"),
    show="headings",
    height=10
)

table.heading("Type", text="Type")
table.heading("Data", text="Data")
table.heading("Source", text="Source")
table.heading("Time", text="Time")

table.column("Type", width=80)
table.column("Data", width=250)
table.column("Source", width=120)
table.column("Time", width=150)

table.pack(pady=10)

status_label = tk.Label(root, text="Status: Idle", fg="blue")
status_label.pack()

# ================= DETECTION FUNCTION =================
def detect_and_draw(frame, source="Live Camera"):
    codes = pyzbar.decode(frame)

    for code in codes:
        code_data = code.data.decode("utf-8")
        code_type = code.type

        x, y, w, h = code.rect
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        text = f"{code_data} ({code_type})"
        cv2.putText(
            frame,
            text,
            (x, y - 10 if y > 20 else y + h + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        if code_data not in scanned_codes:
            scanned_codes.add(code_data)
            scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Beep
            winsound.Beep(1000, 150)

            # Insert into GUI table
            table.insert("", "end", values=(code_type, code_data, source, scan_time))

            # Save to database
            cursor.execute("""
                INSERT INTO scans (code_data, code_type, source, scan_time)
                VALUES (?, ?, ?, ?)
            """, (code_data, code_type, source, scan_time))
            conn.commit()

            # Save to CSV
            with open(CSV_FILE, "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([code_data, code_type, source, scan_time])

    return frame

def scan_image_file():
    stop_camera()  # stop live camera if running

    file_path = filedialog.askopenfilename(
        title="Select Image",
        filetypes=[
            ("Image Files", "*.png *.jpg *.jpeg *.bmp"),
            ("All Files", "*.*")
        ]
    )

    if not file_path or not os.path.exists(file_path):
        return

    image = cv2.imread(file_path)
    if image is None:
        messagebox.showerror("Error", "Could not read image file")
        return

    result = detect_and_draw(image, source=os.path.basename(file_path))

    cv2.imshow("Image Scan Result", result)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# ================= CAMERA CONTROL =================
cap = None
running = False

def start_camera():
    global cap, running
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if not cap.isOpened():
        messagebox.showerror("Error", "Cannot open camera")
        return

    running = True
    status_label.config(text="Status: Scanning...", fg="green")
    update_frame()

def update_frame():
    if not running:
        return

    ret, frame = cap.read()
    if ret:
        frame = detect_and_draw(frame)
        cv2.imshow("Live Camera - QR & Barcode Scanner", frame)
        cv2.waitKey(1)

    root.after(10, update_frame)

def stop_camera():
    global running
    running = False
    status_label.config(text="Status: Stopped", fg="red")
    if cap:
        cap.release()
    cv2.destroyAllWindows()

# ================= BUTTONS =================
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)

start_btn = tk.Button(btn_frame, text="Start Scan", width=15, command=start_camera)
start_btn.grid(row=0, column=0, padx=10)

stop_btn = tk.Button(btn_frame, text="Stop Scan", width=15, command=stop_camera)
stop_btn.grid(row=0, column=1, padx=10)

image_btn = tk.Button(
    btn_frame,
    text="Scan Image File",
    width=15,
    command=scan_image_file
)
image_btn.grid(row=0, column=2, padx=10)

# ================= EXIT HANDLING =================
def on_close():
    stop_camera()
    conn.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
