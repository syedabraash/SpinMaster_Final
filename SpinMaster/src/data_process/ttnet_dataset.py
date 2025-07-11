from turbojpeg import TurboJPEG
jpeg_reader = None

import sys
import os
import numpy as np
import time

from torch.utils.data import Dataset
from turbojpeg import TurboJPEG
import cv2

sys.path.append('../')

from data_process.ttnet_data_utils import load_raw_img


class TTNet_Dataset(Dataset):
    def __init__(self, events_infor, org_size, input_size, transform=None, num_samples=None):
        
        self.events_infor = events_infor
        self.w_org = org_size[0]
        self.h_org = org_size[1]
        self.w_input = input_size[0]
        self.h_input = input_size[1]
        self.w_resize_ratio = self.w_org / self.w_input
        self.h_resize_ratio = self.h_org / self.h_input
        self.transform = transform
        if num_samples is not None:
            self.events_infor = self.events_infor[:num_samples]

    def __len__(self):
        return len(self.events_infor)

    def __resize_ball_pos__(self, ball_pos_xy, w_ratio, h_ratio):
        return np.array([ball_pos_xy[0] / w_ratio, ball_pos_xy[1] / h_ratio])

    def __check_ball_pos__(self, ball_pos_xy, w, h):
        if not ((0 < ball_pos_xy[0] < w) and (0 < ball_pos_xy[1] < h)):
            ball_pos_xy[0] = -1.
            ball_pos_xy[1] = -1.

    def __getitem__(self, index):
        global jpeg_reader
        if jpeg_reader is None:
            jpeg_reader = TurboJPEG(r'C:\libjpeg-turbo64\bin\turbojpeg.dll')  # initialize once

        img_path_list, org_ball_pos_xy, target_events, seg_path = self.events_infor[index]
        seg_img = load_raw_img(seg_path)

        resized_imgs = []

        for img_path in img_path_list:
            if not os.path.exists(img_path):
                continue  # skip missing image silently

            try:
                with open(img_path, 'rb') as in_file:
                    img = jpeg_reader.decode(in_file.read(), 0)
                    resized_imgs.append(cv2.resize(img, (self.w_input, self.h_input)))
            except Exception:
                continue  # skip unreadable images

        if not resized_imgs:
            dummy_img = np.zeros((self.h_input, self.w_input, 3), dtype=np.uint8)
            resized_imgs = [dummy_img] * 9  # fill with blank frames
            resized_imgs = np.dstack(resized_imgs)
        else:
            resized_imgs = np.dstack(resized_imgs)

        global_ball_pos_xy = self.__resize_ball_pos__(org_ball_pos_xy, self.w_resize_ratio, self.h_resize_ratio)

        if self.transform:
            resized_imgs, global_ball_pos_xy, seg_img = self.transform(resized_imgs, global_ball_pos_xy, seg_img)

        org_ball_pos_xy = self.__resize_ball_pos__(global_ball_pos_xy, 1. / self.w_resize_ratio, 1. / self.h_resize_ratio)

        self.__check_ball_pos__(org_ball_pos_xy, self.w_org, self.h_org)
        self.__check_ball_pos__(global_ball_pos_xy, self.w_input, self.h_input)

        resized_imgs = resized_imgs.transpose(2, 0, 1)
        target_seg = seg_img.transpose(2, 0, 1).astype(np.float32)
        target_seg[target_seg < 75] = 0.
        target_seg[target_seg >= 75] = 1.

        return (
            resized_imgs,
            org_ball_pos_xy.astype(np.int32),
            global_ball_pos_xy.astype(np.int32),
            target_events,
            target_seg
        )
    
if __name__ == '__main__':
    import cv2
    import matplotlib.pyplot as plt
    import torch.nn.functional as F
    import torch
    from config.config import parse_configs
    from data_process.ttnet_data_utils import train_val_data_separation
    from data_process.transformation import Compose, Random_Crop, Resize, Random_HFlip, Random_Rotate

    configs = parse_configs()
    game_list = ['game_1']
    dataset_type = 'training'
    train_events_infor, val_events_infor, *_ = train_val_data_separation(configs)
    print('len(train_events_infor): {}'.format(len(train_events_infor)))
    transform = Compose([
        Random_Crop(max_reduction_percent=0.15, p=1.),
        Random_HFlip(p=1.),
        Random_Rotate(rotation_angle_limit=15, p=1.)
    ], p=1.)

    ttnet_dataset = TTNet_Dataset(train_events_infor, configs.org_size, configs.input_size, transform=transform)

    print('len(ttnet_dataset): {}'.format(len(ttnet_dataset)))
    example_index = 100
    resized_imgs, org_ball_pos_xy, global_ball_pos_xy, target_event, target_seg = ttnet_dataset.__getitem__(
        example_index)
    if 1:
        origin_imgs = F.interpolate(torch.from_numpy(resized_imgs).unsqueeze(0).float(), (1080, 1920))
        origin_imgs = origin_imgs.squeeze().numpy().transpose(1, 2, 0).astype(np.uint8)
        print('F.interpolate - origin_imgs shape: {}'.format(origin_imgs.shape))
        resized_imgs = resized_imgs.transpose(1, 2, 0)
        print('resized_imgs shape: {}'.format(resized_imgs.shape))
    else:
        # Test cv2.resize
        resized_imgs = resized_imgs.transpose(1, 2, 0)
        print('resized_imgs shape: {}'.format(resized_imgs.shape))
        origin_imgs = cv2.resize(resized_imgs, (1920, 1080))
        print('cv2.resize - origin_imgs shape: {}'.format(origin_imgs.shape))

    out_images_dir = os.path.join(configs.results_dir, 'debug', 'ttnet_dataset')
    if not os.path.isdir(out_images_dir):
        os.makedirs(out_images_dir)

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(20, 20))
    axes = axes.ravel()

    for i in range(configs.num_frames_sequence):
        img = origin_imgs[:, :, (i * 3): (i + 1) * 3]
        axes[i].imshow(img)
        axes[i].set_title('image {}'.format(i))
    fig.suptitle(
        'Event: is bounce {}, is net: {}, ball_position_xy: (x= {}, y= {})'.format(target_event[0], target_event[1],
                                                                                   org_ball_pos_xy[0],
                                                                                   org_ball_pos_xy[1]),
        fontsize=16)
    plt.savefig(os.path.join(out_images_dir, 'org_all_imgs_{}.jpg'.format(example_index)))
    target_seg = target_seg.transpose(1, 2, 0)
    print('target_seg shape: {}'.format(target_seg.shape))

    plt.imsave(os.path.join(out_images_dir, 'augment_seg_img_{}.jpg'.format(example_index)), target_seg)
    for i in range(configs.num_frames_sequence):
        img = resized_imgs[:, :, (i * 3): (i + 1) * 3]
        if (i == (configs.num_frames_sequence - 1)):
            img = cv2.resize(img, (img.shape[1], img.shape[0]))
            ball_img = cv2.circle(img, tuple(global_ball_pos_xy), radius=5, color=(255, 0, 0), thickness=2)
            ball_img = cv2.cvtColor(ball_img, cv2.COLOR_RGB2BGR)
            cv2.imwrite(os.path.join(out_images_dir, 'augment_img_{}.jpg'.format(example_index)),
                        ball_img)

        axes[i].imshow(img)
        axes[i].set_title('image {}'.format(i))
    fig.suptitle(
        'Event: is bounce {}, is net: {}, ball_position_xy: (x= {}, y= {})'.format(target_event[0], target_event[1],
                                                                                   global_ball_pos_xy[0],
                                                                                   global_ball_pos_xy[1]),
        fontsize=16)
    plt.savefig(os.path.join(out_images_dir, 'augment_all_imgs_{}.jpg'.format(example_index)))
