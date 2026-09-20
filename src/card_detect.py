"""
Zoekt losse kaart-rechthoeken binnen een geknipte regio (bv. "speler" of "dealer" vak).
Werkt op basis van contourdetectie: kaarten zijn lichte rechthoeken op een
(meestal donkerdere) tafelachtergrond. Dit is een redelijk generieke aanpak,
maar geen garantie voor elke site-skin - zie README voor tuning-tips.
"""
import cv2
import numpy as np

MIN_CARD_AREA = 1500          # pas aan naar gelang schermresolutie / zoom
CARD_ASPECT_RATIO = 1.4       # hoogte/breedte van een standaard speelkaart
ASPECT_TOLERANCE = 0.35


def find_card_boxes(region_img):
    """
    Retourneert een lijst van (x, y, w, h) boxes voor vermoedelijke kaarten,
    gesorteerd van links naar rechts.
    """
    gray = cv2.cvtColor(region_img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Kaarten zijn doorgaans (bijna-)wit -> harde threshold werkt vaak goed.
    _, thresh = cv2.threshold(blurred, 150, 255, cv2.THRESH_BINARY)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    boxes = []
    for c in contours:
        area = cv2.contourArea(c)
        if area < MIN_CARD_AREA:
            continue
        x, y, w, h = cv2.boundingRect(c)
        if w == 0:
            continue
        ratio = h / w
        # accepteer zowel rechtopstaande als (bijna) horizontale kaarten
        if abs(ratio - CARD_ASPECT_RATIO) < ASPECT_TOLERANCE or abs((1 / ratio) - CARD_ASPECT_RATIO) < ASPECT_TOLERANCE:
            boxes.append((x, y, w, h))

    boxes.sort(key=lambda b: b[0])  # links -> rechts
    return boxes


def crop_boxes(region_img, boxes):
    crops = []
    for (x, y, w, h) in boxes:
        crops.append(region_img[y:y + h, x:x + w])
    return crops
