```
├── dataset/
    ├── test/
        ├── annotations/
        ├── images/
        ├── videos/
    ├── training
        ├── annotations/
            ├── game_1/
                ├── segmentation_masks/
                ├── ball_markup.json
                ├── events_markup.json
        ├── images/
            ├── game_1/
                ├── img_000001.jpg
                ├── img_000002.jpg
                ...
        ├── videos/
            ├── game_1.mp4
            ├── game_2.mp4
            ...
├── prepare_dataset/
        ├── download_dataset.py
        ├── extract_all_images.py
        ├── extract_selected_images.py
        ├── extract_smooth_labellings.py
        ├── unzip.py
        ├── README.md
├── src/
    ├── config
    │   ├── config.py
    │   ├── __init__.py
    ├── data_process
    │   ├── __init__.py
    │   ├── transformation.py
    │   ├── ttnet_dataloader.py
    │   ├── ttnet_dataset.py
    │   ├── ttnet_data_utils.py
    │   └── ttnet_video_loader.py
    ├── losses
    │   ├── __init__.py
    │   ├── losses.py
    ├── models
    │   ├── __init__.py
    │   ├── model_utils.py
    │   ├── multi_task_learning_model.py
    │   ├── TTNet.py
    │   └── unbalanced_loss_model.py
    └── utils
    │   ├── init_paths.py
    │   ├── __init__.py
    │   ├── logger.py
    │   ├── metrics.py
    │   ├── misc.py
    │   ├── post_processing.py
    │   └── train_utils.py
    ├── demo.py
    ├── demo.sh
    ├── main.py
    ├── test_3rd_phase.sh
    ├── test.py
    ├── train_1st_phase.sh
    ├── train_2nd_phase.sh
    ├── train_3rd_phase.sh
    ├── train.sh
├──

```
