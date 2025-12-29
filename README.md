📷 QR & Barcode Detection Project

This project is a Python-based QR code and barcode detection and decoding system using OpenCV and Pyzbar, enhanced with a GUI, database storage, and CSV logging.
It can scan codes from image files or a live camera feed, display results in a user-friendly interface, and store scan history for reporting and analysis.

✨ Features

✅ Detects QR codes and 1D barcodes

🖼️ Scan from image files (.png, .jpg)

🎥 Live camera scanning

🔊 Beep sound for each new unique code

📝 Displays scanned data in GUI table instead of terminal

🟩 Draws bounding boxes and text labels around detected codes

📍 Automatically adjusts text position inside the image

💾 Stores scan history in an SQLite database

🗂️ Exports scan history to CSV for reporting or analysis

🔄 Switch between image and live camera scanning easily via GUI

🛠️ Requirements

Python 3.10+

Install required libraries:

pip install opencv-python pyzbar
pip install pillow


Windows users: winsound is built-in (no installation needed)

▶️ How to Run the Project

1️⃣ Open terminal in the project folder:

cd qr_project


2️⃣ Run the program:

python qr_gui.py


3️⃣ Use the GUI buttons to switch between image file scanning and live camera scanning.
4️⃣ Scanned codes will appear in the table, and a beep sound will play for new codes.
5️⃣ Scan history is automatically saved to SQLite database (scan_history.db) and CSV (scan_history.csv).

🚀 Technologies Used

Python

OpenCV – image and video processing

Pyzbar – QR & barcode detection

Tkinter – graphical user interface

SQLite3 – database storage

CSV – scan history export
