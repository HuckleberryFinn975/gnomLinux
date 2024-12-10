import cv2
import numpy as np
import os

def recognize(input_file):
    image = cv2.imread(input_file, cv2.IMREAD_GRAYSCALE)
    image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY_INV)[1]

    digit_templates = {}
    template_folder = "samples"
    for digit in range(10):
        template_path = os.path.join(template_folder, f"sample{digit}.png")
        template_image = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        template_image = cv2.threshold(template_image, 128, 255, cv2.THRESH_BINARY_INV)[1]
        digit_templates[digit] = template_image

    detected_digits = []
    for digit, template in digit_templates.items():
        w, h = template.shape[::-1]
        res = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8 
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            detected_digits.append((pt[0], digit))

    detected_digits = sorted(detected_digits, key=lambda x: x[0])
    recognized_number = ''.join(str(digit) for _, digit in detected_digits)
    return recognized_number
