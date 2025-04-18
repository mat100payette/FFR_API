import numpy as np
from PIL import Image
from PySide6.QtGui import QImage


def qimage_to_pil_image(qimage: QImage) -> Image.Image:
    """
    Convert a `PySide6.QtGui.QImage` to a `PIL.Image.Image`.
    """
    # Ensure the QImage format is RGBA8888
    if qimage.format() != QImage.Format.Format_RGBA8888:
        qimage = qimage.convertToFormat(QImage.Format.Format_RGBA8888)

    width = qimage.width()
    height = qimage.height()

    # Get the memoryview of the image bits and cast it to a buffer
    buffer = qimage.bits().tobytes()

    # Convert the buffer into a NumPy array
    arr = np.frombuffer(buffer, dtype=np.uint8).reshape((height, qimage.bytesPerLine() // 4, 4))

    # Slice the array to remove any padding
    arr = arr[:, :width, :]

    # Create a PIL Image from the NumPy array
    pil_image = Image.fromarray(arr, "RGBA")

    return pil_image


def stitch_images_vertically(images: list[Image.Image], image_width: int, image_height: int) -> Image.Image:
    """
    Stitches images vertically.
    """
    num_images = len(images)
    total_width = image_width
    total_height = image_height * num_images

    # Reverse the list of images to fix the vertical order
    images = images[::-1]

    # Create an empty canvas with a transparent background
    stitched_image = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 0))

    # Iterate through the images and place them in the final stitched image
    for i in range(num_images):
        chunk_pil = images[i]

        # Calculate where to place the current chunk in the final image
        left = 0
        upper = i * image_height

        # Paste the chunk into the correct location
        stitched_image.paste(chunk_pil, (left, upper))

    return stitched_image
