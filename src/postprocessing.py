from scipy.ndimage import label, sum, median_filter
import numpy as np
import torch
from aicsimageio import AICSImage
from aicsimageio.writers import OmeTiffWriter
import os


class BinaryMap:
    def __init__(self, num_classes, binary_threshold=0.1, filter_size=3):
        self.num_classes = num_classes
        self.binary_threshold = binary_threshold
        self.filter_size = filter_size

    def _read_tiff_file(self, in_dir, file_name):
        image = AICSImage(os.path.join(in_dir, file_name))
        image_data = image.get_image_dask_data("CZYX", T=0)
        image_array = image_data.compute()
        return image_array

    def _get_softmax_prediction(self, image_array):
        image_tensor = torch.tensor(image_array)
        log_softmax_layer = torch.nn.LogSoftmax(dim=0)
        prediction = log_softmax_layer(image_tensor)
        prediction = prediction[(self.num_classes - 1), :, :, :]
        return prediction

    def _get_binary_maps(self, prediction):
        prediction[prediction >= -self.binary_threshold] = 1.0
        prediction[prediction < -self.binary_threshold] = 0.0
        prediction = median_filter(prediction, size=self.filter_size)
        prediction = prediction.astype(float)
        return prediction


class Post_Processing:
    def __init__(self, object_threshold=10000, boundary_threshold=20):
        self.object_threshold = object_threshold
        self.boundary_threshold = boundary_threshold

    def _remove_objects(self, prediction):
        label_img, cc_num = label(prediction)
        cc_areas = sum(prediction, label_img, range(cc_num + 1))
        area_mask = cc_areas < self.object_threshold
        prediction = prediction.astype(int)
        prediction[area_mask[label_img]] = 0
        prediction = prediction.astype(float)
        return prediction

    def _remove_boundry_objects(self, prediction):
        label_img, _ = label(prediction > 0)
        boundary_mask = np.zeros_like(prediction)
        boundary_mask[:, : self.boundary_threshold, :] = 1
        boundary_mask[:, -self.boundary_threshold :, :] = 1
        boundary_mask[:, :, : self.boundary_threshold] = 1
        boundary_mask[:, :, -self.boundary_threshold :] = 1
        bd_objects_on_hold = prediction.copy()
        bd_idx = list(np.unique(label_img[boundary_mask > 0]))
        for cid in bd_idx:
            if cid > 0:
                bd_objects_on_hold[label_img == cid] = 0
        return bd_objects_on_hold

    def _save_tiff_file(self, prediction, file_name, out_dir):
        prediction = prediction.astype(np.uint8)
        prediction[prediction > 0] = 255
        OmeTiffWriter.save(
            prediction, os.path.join(out_dir, file_name), dim_order="ZYX"
        )
