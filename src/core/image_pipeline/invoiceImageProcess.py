from ultralytics import YOLO
from pathlib import Path
import numpy as np
import ultralytics
import logging
import glob
import cv2


# fmt: off
class ImgProcess:
    __id_list = []
    __seg_model_label_name_list = []
    __base_dir = Path(__file__).resolve().parent
    __step_result_dict = {'first': [], 'second': [], 'third': [], 'fourth': [], 'final': []}

    _seg_invoice_model_pt = __base_dir/'model'/'best_seg.pt'
    _cls_angle_model_pt=__base_dir/'model'/'best_angle_cls.pt'
    _seg_invoice_model = YOLO(_seg_invoice_model_pt, 'segment')
    _cls_angle_model = YOLO(_cls_angle_model_pt, 'classify')

    saving_folder = __base_dir/'result'

    
    def __init__(self, seg_invoice_model_pt=None, cls_angle_model_pt=None, msg=True):
        '''
        seg_invoice_model: 
        Specify the path to the YOLO model file that can segment the image.
        This argument is optional; a dedault value is provided.

        cls_angle_model_pt:
        Specify the path to the YOLO model file used to classify image orientation.
        This argument is optional; a default path is provided.

        msg:
        Toggle display of informational messages.
        '''
        if seg_invoice_model_pt is None:
            seg_invoice_model_pt = self._seg_invoice_model_pt
        if cls_angle_model_pt is None:
            cls_angle_model_pt = self._cls_angle_model_pt

        self.show_msg = msg
        if msg:
            print()
            ultralytics.checks()

        self.set_model_pt(seg_invoice_model_pt, cls_angle_model_pt, msg)

        if self._seg_invoice_model is None and msg:
            print("Seg_invoice_model is None")

        if self._cls_angle_model is None and msg:
            print("Cls_angle_model is None")

    def __call__(self, src, scale_ratio=0.3, save_result=False, return_id=True, step_info=True, contour_info=False, model_info=False):
        """
        If the final result has only one item, return an image. 
        If return_id is True, return a tuple (image, ID) instead.

        If the final result has multiple items, return a list.
        If return_id is True, return a list of (image, ID) tuples instead.

        src:
        The source to be processed.

        scale_ratio:
        The scaling ratio applied to the image.

        save_result:
        Toggle saving of the result.

        return_id:
        Toggle whether to return ID.

        step_info:
        Toggle step informational message display.

        contour_info:
        Toggle showing the contour informational messages

        model_info:
        Toggle whether to display informational messages about the model's prediction.
        """
        if not model_info:
            logging.getLogger("ultralytics").setLevel(logging.CRITICAL)

        seg_model = self._seg_invoice_model

        self.__src = self.__locate_path(src, self.show_msg)
        if self.get_src() is None:
            raise ValueError(f'no {src} found')
        self.__src = self.__src.as_posix()
        
        image_list = self.get_image_list(scale_ratio)

        result_list = seg_model(self.__src, imgsz=1024)

        for index, result in enumerate(result_list):
            i = f"{index:03d}"
            
            masks = result.masks
            if masks is None:
                continue

            for j, mask_tansor in enumerate(masks.data):
                # Get label name               
                label_name = self.get_seg_model_label_name(seg_model, result, j)
                self.__seg_model_label_name_list.append(label_name)

                id = f'result_{i}_{j}'
                self.__id_list.append(id)
                if self.show_msg or contour_info or model_info or step_info:
                    print()
                    print('----------------------------------------------------------------')
                    print(f"{'picture id:':<13}{id:<13}")
                    print(f"{'label name:':<13}{label_name:<13}\n")

                # The First step is to merge mask
                image = image_list[index]
                image_shape = image.shape

                mask = mask_tansor.cpu().numpy().astype(np.uint8) * 255
                mask = cv2.resize(mask, (image_shape[1], image_shape[0]))

                image = self.merge_mask(image, mask)
                self.__step_result_dict['first'].append(image)

                if step_info:
                    print('First step finish')

                # The Second step is to rotate the image
                (x, y), (w, h), angle = self.get_max_contour_info(mask, contour_info)
                image, mask = self.rotate_image(image, angle, mask)
                self.__step_result_dict['second'].append(image)

                if step_info:
                    print('Second step finish')

                # The Third step is to crop the image
                image, mask = self.crop_image(image, mask)
                self.__step_result_dict['third'].append(image)

                if step_info:
                    print('Third step finish')

                # The fourth step is to rotate the image
                cls_model = self._cls_angle_model
                result_list = cls_model(image, imgsz=640)

                angle = int(cls_model.names[result_list[0].probs.top1])
                angle = 90 - angle

                image, mask = self.rotate_image(image, angle, mask)
                self.__step_result_dict['fourth'].append(image)

                if step_info:
                    print('Fourth step finish')

                # The final step is to crop the image
                image, mask = self.crop_image(image, mask)
                self.__step_result_dict['final'].append(image)

                if step_info:
                    print('Final step finish')

                if save_result:
                    folder = Path(self.saving_folder)
                    folder.mkdir(parents=True, exist_ok=True)
                    cv2.imwrite(folder/f'{id}.png', image)

                if self.show_msg or contour_info or model_info or step_info:
                    print('----------------------------------------------------------------')
                    print()

        return self.get_final_result('final', return_id)

    
    def merge_mask(self, image, mask):
        image = cv2.bitwise_and(image, image, mask=mask)
        b, g, r = cv2.split(image)
        return cv2.merge([b, g, r, mask])

    def rotate_image(self, image, angle, mask=None):
        [h_img, w_img, ch] = image.shape

        side_length = h_img if h_img > w_img else w_img
        rect_shape = (side_length, side_length)

        center = side_length // 2
        center = (center, center)

        M = cv2.getRotationMatrix2D(center, angle, 1.0)

        image = cv2.warpAffine(image, M, rect_shape, flags=cv2.INTER_LINEAR, borderValue=(0,0,0))
        if mask is not None:
            mask = cv2.warpAffine(mask, M, rect_shape, flags=cv2.INTER_NEAREST)
        return image, mask

    def crop_image(self, image, mask):
        ys, xs = np.where(mask == 255)

        if len(ys) > 0 and len(xs) > 0:
            y_min, y_max = ys.min(), ys.max()+1
            x_min, x_max = xs.min(), xs.max()+1

        image = image[y_min: y_max, x_min: x_max]
        mask = mask[y_min: y_max, x_min: x_max]

        return image, mask


    def set_model(self, seg_invoice_model=None, cls_angle_model=None):
        self._seg_invoice_model = seg_invoice_model if seg_invoice_model is not None else self._seg_invoice_model
        self._cls_angle_model = cls_angle_model if cls_angle_model is not None else self._cls_angle_model

    def set_model_pt(self, seg_invoice_model_pt=None, cls_angle_model_pt=None, show_msg=False):
        if show_msg:
            print()

        path = self.__locate_path(seg_invoice_model_pt, show_msg)
        self._seg_invoice_model = self.__setYOLO_model(self._seg_invoice_model, path, 'segment')

        path = self.__locate_path(cls_angle_model_pt, show_msg)
        self._cls_angle_model = self.__setYOLO_model(self._cls_angle_model, path, 'classify')

        if show_msg:
            print()

    def set_saving_directory(self, path):
        self.saving_folder = path


    def get_src(self):
        return self.__src
    
    def get_image_list(self, sr=0.3):
        image_path_list = sorted(glob.glob(self.__src))
        return [cv2.resize(cv2.imread(path), (0, 0), fx=sr, fy=sr) for path in image_path_list]
    
    def get_seg_model_label_name(self, seg_model, result, index=0):
        label_index = result.boxes.cls.cpu().numpy().astype(np.uint8)[index].item()
        return seg_model.names[label_index]

    def get_max_contour_info(self, mask, msg=False):
        '''return (x, y), (w, h), angle'''
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            raise ValueError('No contours found')
        
        max_contours = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > max_contours:
                max_contours = area
                contour = cnt

        (x, y), (w, h), angle = cv2.minAreaRect(contour)
        if msg:
            print()
            print(f"{'rotation angle:':<20}{angle:.3f}")
            print(f"{'center point:':<20}({x:7.2f}, {y:7.2f})")
            print(f"{'width & height:':<20}({w:7.2f}, {h:7.2f})")
            print()

        return (x, y), (w, h), angle

    def get_final_result(self, step, return_id=False):
        result_list = self.__step_result_dict[step]
        id_list = self.__id_list
        len_res = len(result_list)

        if len_res == 1:
            if return_id:
                return (result_list[0], id_list[0])
            return result_list[0]
        if len_res > 1:
            if return_id:
                return list(zip(result_list, id_list))
            return result_list
        else:
            return None


    def __setYOLO_model(self, model, path, task=None, verbose=False):
        return YOLO(path, task, verbose) if path is not None else model

    def __locate_path(self, path, show_msg=False):
        if path is None:
            if show_msg:
                print('Path is None')
            return None
        
        path = Path(path)

        if '*' in path.name:
            if Path(path.parent).exists():
                if show_msg:
                    print(f"Path '{path}', is exist")
                return path
            else:
                if show_msg:
                    print(f"No '{path}' found")
                return None
        
        if path.exists():
            if show_msg:
                print(f"Path: '{path}', is exist")
            return path
        else:
            if show_msg:
                print(f"No '{path}' found")
            return None
# fmt: on


if __name__ == "__main__":
    base_dir = Path(__file__).resolve().parent
    path = base_dir / "raw_images" / "*"
    process = ImgProcess()
    process.set_saving_directory(base_dir / "test_result")
    result_list = process(path.as_posix(), save_result=True, return_id=True)

    """all_path = "result/*"
    for path in glob.glob(all_path):
        img = cv2.imread(path)
        path = path.split("\\")[-1]
        cv2.imshow(path, img)
        key = cv2.waitKey(1500)
        if key == 27 or key == ord("q"):
            break"""

    for result, id in result_list:
        cv2.imshow(id, result)
        key = cv2.waitKey(1500)
        if key == 27 or key == ord("q"):
            break

    while True:
        if key == 27 or key == ord("q"):
            cv2.destroyAllWindows()
            break
        else:
            key = cv2.waitKey(0)
