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
results = process(src)
```

You can also pass additional arguments such as:

- **`scale_ratio`** *(`float` | `int`)*:
The scaling ratio applied to the image.
- **`save_result`** *(`bool`)*:
Toggle saving of the result.
- **`step_info`** *(`bool`)*:
Toggle step informational message display.
- **`contour_info`** *(`bool`)*:
Toggle showing the contour informational messages
- **`model_info`** *(`bool`)*:
Toggle whether to display informational messages about the model's prediction.

```python
results = process(
    src,
    scale_ratio=0.3,
    save_result=True,
    step_info=True,
    contour_info=False,
    model_info=False,
)
```

### 3. What It Returns

Returns a list of results of P_Result objects, e.g., `[result1, result2, ...]`, 
you can use 

**`result1.image`** to get the `image (as a numpy.ndarray)` from *`result1`*, 

**`result2.id`** to get the `ID (as a str)` from *`result2`*, and 

**`result3.label_name`** to get the `label_name (as a str)` from *`result3`*

- **Displaying output**
```python
import cv2

for result in results:
    print(result.label_name)
    cv2.imshow(result.id, result.image)
    key = cv2.waitkey(1500)
    if key == 27 or key == ord("q"):
        break

while not (key == 27 or key == ord("q")):
    key = cv2.waitKey(0)
cv2.destroyAllWindows()
```
- **Displaying output on colab**
```python
from google.colab.patches import cv2_imshow

for result in results:
    print(result.id, result.label_name)
    cv2_imshow(result.image)
```

## ⚙️ Model and Output Configuration

The `ImgProcess` object allows you to configure the model and output behavior before processing:

### `set_model(seg_model=None, cls_model=None)`

Sets a custom model object for processing.

*You can provide either `seg_model` or `cls_model`, or both - it's recommended to provide at least one.*

```python
process.set_model(
    seg_invoice_model=your_seg_model,
    cls_angle_model=your_cls_model
)
```

### `set_model_pt(seg_model_pt=None, cls_model_pt=None, msg=False)`

Specify a custom file path for the YOLO model input.

*You can provide either `seg_model_pt` or `cls_model_pt`, or both - it's recommended to provide at least one.*

```python
process.set_model(
    seg_invoice_model_pt=your_seg_model_pt,
    cls_angle_model_pt=your_cls_model_pt
)
```

### `set_saving_directory(path: str | Path)`

Sets the folder where results will be saved.

```python
process.set_saving_directory(your_saving_path)
```

## 📋 Retrieving Information and Processed Results

The `ImgProcess` object provides several `get_` methods for accessing internal information and step-by-step results.

### `get_src()`

```python
src = process.get_src()
print(src)
```

### `get_image_list(sr=0.3)`
- **`sr`** *(`float*` | `int`)*: The scaling ratio applied to the image.

```python
import cv2

scale_ratio = 0.3
image_list = process.get_image_list(scale_ratio)

for i, image in enumerate(image_list):
    cv2.imshow(str(i), image)
```