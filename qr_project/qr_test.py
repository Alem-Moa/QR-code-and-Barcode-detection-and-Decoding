import cv2
from pyzbar import pyzbar
import os
import winsound

# ---------------- CONFIG ----------------
IMAGE_FILES = ["images/test_qr.png", "images/barcode1.jpg"]
FRAME_WIDTH = 640
FRAME_HEIGHT = 480
# ----------------------------------------

# Store already scanned codes (avoid duplicates)
scanned_codes = set()

def detect_and_draw(frame, source="Camera"):
    """
    Detect QR codes and barcodes, draw bounding boxes,
    beep only once per unique code, print data to terminal,
    and position text safely inside the image.
    """
    codes = pyzbar.decode(frame)

    for code in codes:
        code_data = code.data.decode("utf-8")
        code_type = code.type

        # ---------- DRAW QR / BARCODE BOX ----------
        x, y, w, h = code.rect
        cv2.rectangle(
            frame, (x, y), (x + w, y + h),
            (0, 255, 0), 2
        )

        # ---------- TEXT POSITION FIX ----------
        text = f"{code_data} ({code_type})"

        (text_width, text_height), baseline = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
        )

        # Default position: above box
        text_x = x
        text_y = y - 10

        # Move text below if above image boundary
        if text_y - text_height < 0:
            text_y = y + h + text_height + 10

        # Shift left if text goes out of right boundary
        if text_x + text_width > frame.shape[1]:
            text_x = frame.shape[1] - text_width - 10

        # ---------- TEXT BACKGROUND ----------
        cv2.rectangle(
            frame,
            (text_x - 5, text_y - text_height - 5),
            (text_x + text_width + 5, text_y + 5),
            (0, 0, 0),
            -1
        )

        # ---------- DRAW TEXT ----------
        cv2.putText(
            frame,
            text,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 255),
            2
        )

        # ---------- BEEP & TERMINAL OUTPUT ----------
        if code_data not in scanned_codes:
            scanned_codes.add(code_data)

            winsound.Beep(1000, 150)

            print(f"[NEW SCAN] Source: {source}")
            print(f"  Type : {code_type}")
            print(f"  Data : {code_data}")
            print("-" * 45)

    return frame


# ================= IMAGE FILE SCAN =================
for file_path in IMAGE_FILES:
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found!")
        continue

    image = cv2.imread(file_path)
    image = detect_and_draw(image, source=file_path)

    cv2.imshow(f"QR & Barcode Detection - {file_path}", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ================= LIVE CAMERA SCAN =================
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Error: Cannot open camera")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

print("Press 'q' to quit the live camera.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = detect_and_draw(frame, source="Live Camera")
    cv2.imshow("QR & Barcode Detection (Live Camera)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
