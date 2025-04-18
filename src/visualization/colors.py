from PySide6.QtGui import QColor


def manip_score_to_color(score: int) -> str:
    """
    Map a manip score to distinct color bands with smooth transitions:
    - 0-25   : White
    - 26-50  : Green
    - 51-75  : Yellow
    - 76-100 : Red
    - 100    : Purple
    """

    if score <= 25:
        # White (255, 255, 255) to Green (0, 255, 0)
        normalized_score = score / 25  # Normalize between 0 and 25
        r = int(255 * (1 - normalized_score))  # Red decreases from 255 to 0
        g = 255  # Green stays at 255
        b = int(255 * (1 - normalized_score))  # Blue decreases from 255 to 0
    elif 26 <= score <= 50:
        # Green (0, 255, 0) to Yellow (255, 255, 0)
        normalized_score = (score - 25) / 25  # Normalize between 25 and 50
        r = int(255 * normalized_score)  # Red increases from 0 to 255
        g = 255  # Green stays at 255
        b = 0  # Blue stays at 0
    elif 51 <= score <= 75:
        # Yellow (255, 255, 0) to Red (255, 0, 0)
        normalized_score = (score - 50) / 25  # Normalize between 50 and 75
        r = 255  # Red stays at 255
        g = int(255 * (1 - normalized_score))  # Green decreases from 255 to 0
        b = 0  # Blue stays at 0
    else:
        # Red (255, 0, 0) to Purple-Red (128, 0, 128)
        normalized_score = (score - 75) / 25  # Normalize between 75 and 100
        r = int(255 * (1 - (0.5 * normalized_score)))  # Red decreases slightly from 255 to 128
        g = 0  # Green stays at 0
        b = int(255 * normalized_score)  # Blue increases from 0 to 128

    return QColor(r, g, b).name()
