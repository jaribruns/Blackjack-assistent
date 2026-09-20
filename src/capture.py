"""
Schermopname via mss (snel, werkt op Windows/macOS/Linux).
"""
import numpy as np
import mss


def grab_region(region):
    """
    region: [x, y, w, h] in absolute schermpixels.
    Retourneert een BGR numpy array (OpenCV-formaat).
    """
    x, y, w, h = region
    monitor = {"left": int(x), "top": int(y), "width": int(w), "height": int(h)}
    with mss.mss() as sct:
        shot = sct.grab(monitor)
        img = np.array(shot)  # BGRA
        return img[:, :, :3]  # drop alpha -> BGR


def grab_full_screen():
    with mss.mss() as sct:
        monitor = sct.monitors[1]  # primair scherm; pas aan voor multi-monitor setups
        shot = sct.grab(monitor)
        img = np.array(shot)
        return img[:, :, :3], monitor
