from image_pipeline import ImgProcess
from pathlib import Path
import cv2
import os

# 可以在此測試Poetry 正常的話會看到圖片

path = Path(__file__).parts
index = path.index("src")
path = (
    Path("\\".join(path[: index + 1]))
    / "core"
    / "image_pipeline"
    / "raw_images"
    / "20250630_100847.jpg"
)
print(path.exists())
process = ImgProcess()
result = process(path)
cv2.imshow("result", result[0].image)
cv2.waitKey(0)
print(os.getcwd())
