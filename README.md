# Peyers Patch
## Discription
This repository contains helper classes to generate segmentation binary maps and filter the predictions. In order to use this package, the raw predictions from mmv_im2im package are needed. These raw predictions are saved in your local machine. This corresponding folder that contains the raw predictions is the input directory for this package. The output directory is the folder in your local machine to save your binary maps. In order to use this package use as below

`python main.py --input_dir /mnt/eternus/users/Sai/paired_data/segmentation_final_predictions/PP/raw_predictions/B_cells --output_dir /mnt/eternus/users/Sai/paired_data/segmentation_final_predictions/PP/binary_predictions/B_cells --binary_threshold 1.0 --size_threshold 10000 --num_classes 2 --smoothen_threshold 3 --boundry_buffer_distance 20`

### Description of input arguments:

- `input_dir` is the directory of the input raw predictions after using mmv_im2im package
- `output_dir` is the directory to save your binary predictions
- `binary_threshold` it is the threshold limit to convert raw predictions to binary images. For peyers patch project the optimal values are 1.0 for channel 1 (B cells) and 0.001 for channel 2 (T cells).
- `size_threshold` it is the threshold limit to remove unecessary objects of smaller sizes.
- `num_classes` contains the number of classes that needs to be segmented. For binary segmentation it is 2, for multi class segmentation it depends on the number of classes that need to be segmented
- `smoothen_threshold` this argument is used to smoothen the edges present in the segmented regions.
- `boundry_buffer_distance` argument is used to removed objects that touches the boundries. The filter size is given as input argument to remove objects with the vicinity of these pixels region in all the four regions.

### Discription of the folder structure:
- The peyers patch folder is organized in to following structure:
- `checkpoints` folder contains the best models for channel 1 and channel 2 segmentations respectively.
- `configs` folder contains the YAML files to use for the mmv_im2im package to generate raw predictions
- `src` contains all the necessary pyhton files to generate, postprocess and evaluate the tumor sizes from the binary maps. 
#### Description of the python files in src folder:
- The src folder contains three files viz. postprocessing.py, evaluation_metrics.py, __init__.py and main.py. The postprocessing.py file contains class named `BinaryMap` which contains all the helper functions to convert raw iamges to binary maps. This file is used in general to convert any raw prediction into the binary map based on the input arguments. The evaluation_metrics.py is a file that is specifically used to reproduce the results of the peyers patch project. In order for this file to use, it is important to have appropriate file suffixes in both the raw predictions and binary predictions directory.

### Example usecase for peyers patch:

- With the help of the instructions, use the config files and necessary checkpoints which are available in the config and checkpoints folder of peyers patch. 
  For example, to generate raw predictions for B cells use the checkpoint "unet_model_B_cell_segmentation.ckpt" and "inference_segmentation_B_cells_unet.yaml" as
  below:
  `run_im2im --config ./mmv_im2im/example_configs/inference_segmentation_B_cells_unet.yaml  --mode inference --debug`
  
  and similarly for T cells use the mmv_im2im as below after installation:
  
  `run_im2im --config ./mmv_im2im/example_configs/inference_segmentation_T_cells_unet.yaml  --mode inference --debug`
  
  Also ensure that checkpoints are used in appropriate locations in the config files. For example one can use it as follows:
  
  `ckpt:`
  
         checkpoint_path: ../mmv_im2im_original/unet_model_B_cell_segmentation.ckpt
         hparams_file:../mmv_im2im_original/lightning_logs/version_XX/hparams.yaml`
 - Once we have the raw predictions, ensure that each file have a name ending as "_IM_" along with necessary suffix ending mentioned in the config file.
 - After generating the raw predictions for B cells and T cells seperately, store these raw predictions in your local machine.
 - Use the peyers patch repository to generate raw predictions as below:

  For B cells, to convert raw predictions to binary maps:
  
  `python main.py --input_dir ../Peyerspatch/raw_predictions/B_cells --output_dir ../Peyerspatch/PP/binary_predictions/B_cells --binary_threshold 1.0 --size_threshold 10000 --num_classes 2 --smoothen_threshold 3 --boundry_buffer_distance 20`
  
  For T cells, to convert raw predictions to binary maps:
  
  `python main.py --input_dir ../Peyerspatch/raw_predictions/T_cells --output_dir ../Peyerspatch/PP/binary_predictions/T_cells --binary_threshold 0.001 --size_threshold 2000 --num_classes 2 --smoothen_threshold 3 --boundry_buffer_distance 20`
  
  After generating the binary predictions, the postprocessing will be completed and the binary predictions in their corresponding folders are generated. Additionally, the evaluation metrics are also estimated and these files are stored in individual folder seperately. A user input is taken weather he/she wants to visualize the metrics together in one excel file or not. If he chooses not to visualize them together, the program is ended and the user can have access to these files.
