# Invoice Image Process

**Introduction:** The `invoiceImageProcess.py` script preprocesses invoice images by masking irrelevant regions and correcting their orientation.

## 📖 Usage

### 1. Import the script and Instantiate the 'ImgProcess' class

```python
from core.image_pipeline import ImgProcess

process = ImgProcess()
```

You can provide your own YOLO model file by passing it as an argument to the script.

```python
from core.image_pipeline import ImgProcess

seg_invoice_model_pt= "your own YOLO model file path"
cls_angle_model_pt= "your own YOLO model file path"

process = ImgProcess(
    seg_invoice_model_pt, cls_angle_model_pt
)
```

To enable information output, set the `msg` parameter to `True`.

```python
from core.image_pipeline import ImgProcess

process = ImgProcess(msg=True)
``` 

### 2. Run Image Processing

Use the `process()` method to perform masking and rotation on the input image.

```python
# The source of the image(s) to be processed. 
# Accepts various types, including file paths, URLs, PIL images, NumPy arrays, and Torch tensors.
src = "(str | Path | int | Image.Image | list | tuple | np.ndarray | torch.Tensor)"
result = process(src)
```