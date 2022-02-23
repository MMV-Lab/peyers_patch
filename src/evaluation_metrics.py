import pandas as pd
import glob
from aicsimageio import AICSImage
import numpy as np
import os
import yaml
from munch import Munch


class EvaluationMetrics:
    def __init__(self, in_dir, out_dir):
        self.in_dir = in_dir
        self.out_dir = out_dir

    def _read_yaml_file(self, yaml_path):
        with open(yaml_path, "r") as stream:
            opt_dict = yaml.safe_load(stream)
            opt = Munch(opt_dict)
            return opt

    def _load_file_suffix(self, cfg):
        self.suffix = cfg["data"]["output"]["suffix"]

    def _get_tumor_size(self, prediction):
        n_white_pix = np.sum(prediction == 255)
        return n_white_pix

    def _evaluate_tumor_sizes(self):
        file_list = glob.glob(self.in_dir + "/" + "*_IM_" + self.suffix + ".tiff")
        df = []
        for file in file_list:
            word_list = os.path.basename(file).split("_")
            channel_id = word_list[-4]
            if channel_id == "ch01" or channel_id == "ch1":
                self.channel_name = "Bcell tumor size"
            elif channel_id == "ch02" or channel_id == "ch2":
                self.channel_name = "Tcell tumor size"
            else:
                self.channel_name = "other tumor size"
            ch_pred = self.out_dir + os.sep + os.path.basename(file)
            if not os.path.exists(ch_pred):
                print("Missing file name")
                ch_tumor_size = np.nan
                file_name = "_".join(os.path.basename(file).split("_")[:-4])
                df.append({"Filename": file_name, self.channel_name: ch_tumor_size})
                continue
            ch_image = AICSImage(ch_pred)
            ch_image_data = ch_image.get_image_dask_data("ZYX", T=0, C=0)
            ch_image_array = ch_image_data.compute()
            ch_tumor_size = self._get_tumor_size(ch_image_array)
            file_name = "_".join(os.path.basename(file).split("_")[:-4])
            df.append({"Filename": file_name, self.channel_name: ch_tumor_size})
        return df

    def _get_data_frame(self, df):
        dataframe = pd.DataFrame(df)
        dataframe.to_excel
        return dataframe

    def _save_data(self, dataframe):
        dataframe.to_excel(
            os.path.join(self.out_dir, "_".join(self.channel_name.split()) + ".xlsx")
        )
