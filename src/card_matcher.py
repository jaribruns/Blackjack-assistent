"""
Herkent welke kaart (rang + kleur) op een crop staat, door de crop te vergelijken
met de templates die de gebruiker via calibrate.py heeft ingesproken.

Gebruikt ORB-features (schaal/rotatie-tolerant genoeg voor kleine verschillen
in browserzoom) + een template-match als fallback/score-verfijning.
"""
import os
import cv2
import numpy as np
from paths import base_dir

TEMPLATE_DIR = os.path.join(base_dir(), "templates")

RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
SUITS = ["S", "H", "D", "C"]  # Spades, Hearts, Diamonds, Clubs


class CardMatcher:
    def __init__(self, threshold=0.72):
        self.threshold = threshold
        self.orb = cv2.ORB_create(nfeatures=500)
        self.bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.templates = {}  # label -> (gray_img, keypoints, descriptors)
        self._load_templates()

    def _load_templates(self):
        if not os.path.isdir(TEMPLATE_DIR):
            return
        for fname in os.listdir(TEMPLATE_DIR):
            if not fname.lower().endswith(".png"):
                continue
            label = fname[:-4]  # bv. "AS", "10H"
            path = os.path.join(TEMPLATE_DIR, fname)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            kp, des = self.orb.detectAndCompute(img, None)
            self.templates[label] = (img, kp, des)

    def reload(self):
        self.templates = {}
        self._load_templates()

    def identify(self, card_img):
        """
        card_img: BGR crop van 1 kaart.
        Retourneert (label, score) of (None, 0) als niets goed genoeg matcht.
        label formaat: "AS" = Aas Schoppen, "10H" = 10 Harten, etc.
        """
        if card_img is None or card_img.size == 0:
            return None, 0.0

        gray = cv2.cvtColor(card_img, cv2.COLOR_BGR2GRAY)
        kp, des = self.orb.detectAndCompute(gray, None)
        if des is None or len(kp) < 4:
            return self._template_match_fallback(gray)

        best_label, best_score = None, 0.0
        for label, (t_img, t_kp, t_des) in self.templates.items():
            if t_des is None or len(t_kp) < 4:
                continue
            matches = self.bf.match(des, t_des)
            if not matches:
                continue
            matches = sorted(matches, key=lambda m: m.distance)
            good = [m for m in matches if m.distance < 60]
            score = len(good) / max(len(t_kp), 1)
            if score > best_score:
                best_score, best_label = score, label

        if best_score >= self.threshold * 0.5:  # ORB-score schaal ligt lager dan 0-1 template match
            return best_label, best_score

        return self._template_match_fallback(gray)

    def _template_match_fallback(self, gray_card):
        """Als er te weinig features zijn (bv. effen kaartrug of kleine crop),
        val terug op klassieke genormaliseerde template matching."""
        best_label, best_score = None, 0.0
        for label, (t_img, _, _) in self.templates.items():
            if t_img is None:
                continue
            try:
                resized = cv2.resize(gray_card, (t_img.shape[1], t_img.shape[0]))
            except cv2.error:
                continue
            res = cv2.matchTemplate(resized, t_img, cv2.TM_CCOEFF_NORMED)
            score = float(res.max())
            if score > best_score:
                best_score, best_label = score, label

        if best_score >= self.threshold:
            return best_label, best_score
        return None, best_score


def label_to_rank(label):
    """'10H' -> '10', 'AS' -> 'A'"""
    for r in sorted(RANKS, key=len, reverse=True):
        if label.startswith(r):
            return r
    return None
