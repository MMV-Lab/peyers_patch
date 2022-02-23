from postprocessing import Post_Processing, BinaryMap
from evaluation_metrics import EvaluationMetrics
import argparse
import os
import sys
from pathlib import Path
import pandas as pd


class Args(argparse.Namespace):
    def __init__(self):
        self._args_parse()

    def _args_parse(self):
        p = argparse.ArgumentParser(description="Post processing predictions")

        p.add_argument(
            "--input_dir",
            required=True,
            action="store",
            help="Input directory to load predictions",
        )

        p.add_argument(
            "--output_dir",
            required=True,
            action="store",
            help="Output directory to load predictions",
        )

        p.add_argument(
            "--num_classes",
            default=2,
            type=int,
            help="Number of classes present in the image",
        )

        p.add_argument(
            "--binary_threshold",
            default=0.001,
            required=True,
            type=float,
            help="Threshold value to convert predictions to binary maps",
        )

        p.add_argument(
            "--smoothen_threshold",
            default=3,
            type=int,
            help="Threshold value to apply smoothen filter",
        )

        p.add_argument(
            "--size_threshold",
            default=1000,
            required=True,
            type=int,
            help="Threshold size to remove objects",
        )

        p.add_argument(
            "--boundry_buffer_distance",
            default=20,
            type=int,
            help="Threshold size to remove objects at boundries",
        )
        p.parse_args(namespace=self)


CH_YAML = "../configs/inference_segmentation_B_cells_unet.yaml"
EXCEL_FILE = "tumor_sizes.xlsx"


def _get_binary_maps(args):
    input_dir = args.input_dir
    output_dir = args.output_dir
    num_classes = args.num_classes
    binary_threshold = args.binary_threshold
    smoothen_theshold = args.smoothen_threshold
    size_threshold = args.size_threshold
    boundry_buffer_distance = args.boundry_buffer_distance
    binary_map = BinaryMap(num_classes, binary_threshold, smoothen_theshold)
    post_processor = Post_Processing(size_threshold, boundry_buffer_distance)
    file_list = sorted(os.listdir(input_dir))
    for file in file_list:
        image_array = binary_map._read_tiff_file(input_dir, file)
        prediction = binary_map._get_softmax_prediction(image_array)
        prediction = binary_map._get_binary_maps(prediction)
        prediction = post_processor._remove_objects(prediction)
        prediction = post_processor._remove_boundry_objects(prediction)
        post_processor._save_tiff_file(prediction, file, output_dir)


def _evaluate_metrics_ch(args, yaml_file):
    input_dir = args.input_dir
    output_dir = args.output_dir
    evaluator = EvaluationMetrics(input_dir, output_dir)
    ch_cfg = evaluator._read_yaml_file(yaml_file)
    evaluator._load_file_suffix(ch_cfg)
    ch_df = evaluator._evaluate_tumor_sizes()
    ch_dataframe = evaluator._get_data_frame(ch_df)
    return ch_dataframe


def _merge_dataframes(dataframe1, dataframe2):
    final_dataframe = dataframe1.merge(dataframe2, on="Filename", how="inner")
    return final_dataframe


def _save_data(args, dataframe):
    dataframe.to_excel(os.path.join(args.output_dir, EXCEL_FILE), index=False)


def main():
    args = Args()
    print("Generating binary maps for raw predictions")
    _get_binary_maps(args)
    print("Post processing complete")
    ch_dataframe = _evaluate_metrics_ch(args, CH_YAML)
    _save_data(args, ch_dataframe)
    print("Saved channel metrics as excel")
    print("Do you want to merge the excel files? \n")
    merge_file = input("yes/no \n")
    if merge_file == "yes":
        ch1_out_dir = input("Enter the output directory of channel 1: ")
        ch2_out_dir = input("Enter the output directory of channel 2: ")
        ch1_dataframe = pd.read_excel(os.path.join(ch1_out_dir, EXCEL_FILE))
        ch2_dataframe = pd.read_excel(os.path.join(ch2_out_dir, EXCEL_FILE))
        final_dataframe = _merge_dataframes(ch1_dataframe, ch2_dataframe)
        final_dataframe.to_excel(
            os.path.join(os.path.commonpath([ch1_out_dir, ch2_out_dir]), EXCEL_FILE)
        )
    elif merge_file == "no":
        sys.exit(0)


if __name__ == "__main__":
    main()
