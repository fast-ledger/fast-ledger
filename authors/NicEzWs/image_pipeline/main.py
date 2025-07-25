from scanner.image_pipeline import ImgProcess, P_Result
from pathlib import Path
import cv2

base_dir = Path(__file__).parent

process = ImgProcess(
    seg_invoice_model_pt="src/core/scanner/image_pipeline/models/seg_invoice3.pt"
)

img: str | Path = "picture5.jpg"
step_list: list[str] = ["1first", "2second", "3third", "4fourth", "5final", "9mask"]
step_result: list[P_Result] = []


final_list = process(base_dir / "0raw_imgs" / img, scale_ratio=1)


def get_result(result_list: list, step_list: list):
    for list in step_list:
        result_list.append(process.get_step_result(list[1:])[0])


get_result(step_result, step_list)


for i, step in enumerate(step_list):
    path = base_dir / step
    path.mkdir(parents=True, exist_ok=True)
    path = path / img
    cv2.imwrite(path.as_posix(), step_result[i].image)
