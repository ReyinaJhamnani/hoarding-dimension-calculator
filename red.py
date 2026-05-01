import cv2 as cv
import numpy as np


def detect_red_square(image_path, name):
    box_detected = False
    w, h = 0, 0

    image = cv.imread(image_path)

    if image is None:
        print(f"Error: Could not read image at {image_path}")
        blank = np.zeros((100, 100, 3), dtype=np.uint8)
        return 0, 0, blank

    max_width = 800
    max_height = 650

    orig_height, orig_width = image.shape[:2]
    aspect_ratio = orig_width / orig_height

    # Resize image while maintaining aspect ratio
    if orig_width > max_width or orig_height > max_height:
        if aspect_ratio > 1:
            new_width = max_width
            new_height = int(max_width / aspect_ratio)
        else:
            new_height = max_height
            new_width = int(max_height * aspect_ratio)
        resized_image = cv.resize(image, (new_width, new_height))
    else:
        resized_image = image.copy()

    # BGR color range for red
    lower_red = np.array([0, 0, 115])
    upper_red = np.array([81, 100, 255])

    mask = cv.inRange(resized_image, lowerb=lower_red, upperb=upper_red)

    # Morphological opening to remove small noise
    kernel = np.ones((3, 3), np.uint8)
    mask = cv.morphologyEx(mask, cv.MORPH_OPEN, kernel)

    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        approx = cv.approxPolyDP(contour, 0.02 * cv.arcLength(contour, True), True)

        if 3 < len(approx) <= 5 and cv.isContourConvex(approx):
            x, y, w, h = cv.boundingRect(approx)
            contour_aspect_ratio = float(w) / h
            print(f"Candidate box: w={w}, h={h}, ar={contour_aspect_ratio:.2f}")

            if (0.6 <= contour_aspect_ratio <= 1.4) and (cv.contourArea(contour) > 20):
                box_detected = True
                cv.rectangle(resized_image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv.putText(resized_image, "Red Box Detected",
                           (x + w // 2 - 50, y - 10),
                           cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                break

    # moved outside loop — only reset if nothing was ever detected
    if not box_detected:
        w, h = 0, 0
        print("No red square detected")


    return w, h, resized_image
