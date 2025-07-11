import torch
import torch.nn as nn
import torch.nn.functional as F


class ConvBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ConvBlock, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.batchnorm = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU()
        self.maxpool = nn.MaxPool2d(kernel_size=2, stride=2, padding=0)

    def forward(self, x):
        x = self.maxpool(self.relu(self.batchnorm(self.conv(x))))
        return x


class ConvBlock_without_Pooling(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(ConvBlock_without_Pooling, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, kernel_size=3, stride=1, padding=1)
        self.batchnorm = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU()

    def forward(self, x):
        x = self.relu(self.batchnorm(self.conv(x)))
        return x


class DeconvBlock(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DeconvBlock, self).__init__()
        middle_channels = int(in_channels / 4)
        self.conv1 = nn.Conv2d(in_channels, middle_channels, kernel_size=1, stride=1, padding=0)
        self.batchnorm1 = nn.BatchNorm2d(middle_channels)
        self.relu = nn.ReLU()
        self.batchnorm_tconv = nn.BatchNorm2d(middle_channels)
        self.tconv = nn.ConvTranspose2d(middle_channels, middle_channels, kernel_size=3, stride=2, padding=1,
                                        output_padding=1)
        self.conv2 = nn.Conv2d(middle_channels, out_channels, kernel_size=1, stride=1, padding=0)
        self.batchnorm2 = nn.BatchNorm2d(out_channels)

    def forward(self, x):
        x = self.relu(self.batchnorm1(self.conv1(x)))
        x = self.relu(self.batchnorm_tconv(self.tconv(x)))
        x = self.relu(self.batchnorm2(self.conv2(x)))

        return x


class BallDetection(nn.Module):
    def __init__(self, num_frames_sequence, dropout_p):
        super(BallDetection, self).__init__()
        self.conv1 = nn.Conv2d(num_frames_sequence * 3, 64, kernel_size=1, stride=1, padding=0)
        self.batchnorm = nn.BatchNorm2d(64)
        self.relu = nn.ReLU()
        self.convblock1 = ConvBlock(in_channels=64, out_channels=64)
        self.convblock2 = ConvBlock(in_channels=64, out_channels=64)
        self.dropout2d = nn.Dropout2d(p=dropout_p)
        self.convblock3 = ConvBlock(in_channels=64, out_channels=128)
        self.convblock4 = ConvBlock(in_channels=128, out_channels=128)
        self.convblock5 = ConvBlock(in_channels=128, out_channels=256)
        self.convblock6 = ConvBlock(in_channels=256, out_channels=256)
        self.fc1 = nn.Linear(in_features=2560, out_features=1792)
        self.fc2 = nn.Linear(in_features=1792, out_features=896)
        self.fc3 = nn.Linear(in_features=896, out_features=448)
        self.dropout1d = nn.Dropout(p=dropout_p)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.batchnorm(self.conv1(x)))
        out_block2 = self.convblock2(self.convblock1(x))
        x = self.dropout2d(out_block2)
        out_block3 = self.convblock3(x)
        out_block4 = self.convblock4(out_block3)
        x = self.dropout2d(out_block4)
        out_block5 = self.convblock5(out_block4)
        features = self.convblock6(out_block5)

        x = self.dropout2d(features)
        x = x.contiguous().view(x.size(0), -1)

        x = self.dropout1d(self.relu(self.fc1(x)))
        x = self.dropout1d(self.relu(self.fc2(x)))
        out = self.sigmoid(self.fc3(x))

        return out, features, out_block2, out_block3, out_block4, out_block5


class EventsSpotting(nn.Module):
    def __init__(self, dropout_p):
        super(EventsSpotting, self).__init__()
        self.conv1 = nn.Conv2d(512, 64, kernel_size=1, stride=1, padding=0)
        self.batchnorm = nn.BatchNorm2d(64)
        self.relu = nn.ReLU()
        self.dropout2d = nn.Dropout2d(p=dropout_p)
        self.convblock = ConvBlock_without_Pooling(in_channels=64, out_channels=64)
        self.fc1 = nn.Linear(in_features=640, out_features=512)
        self.fc2 = nn.Linear(in_features=512, out_features=2)
        self.sigmoid = nn.Sigmoid()

    def forward(self, global_features, local_features):
        input_eventspotting = torch.cat((global_features, local_features), dim=1)
        x = self.relu(self.batchnorm(self.conv1(input_eventspotting)))
        x = self.dropout2d(x)
        x = self.convblock(x)
        x = self.dropout2d(x)
        x = self.convblock(x)
        x = self.dropout2d(x)

        x = x.contiguous().view(x.size(0), -1)
        x = self.relu(self.fc1(x))
        out = self.sigmoid(self.fc2(x))

        return out


class Segmentation(nn.Module):
    def __init__(self):
        super(Segmentation, self).__init__()
        self.deconvblock5 = DeconvBlock(in_channels=256, out_channels=128)
        self.deconvblock4 = DeconvBlock(in_channels=128, out_channels=128)
        self.deconvblock3 = DeconvBlock(in_channels=128, out_channels=64)
        self.deconvblock2 = DeconvBlock(in_channels=64, out_channels=64)
        self.tconv = nn.ConvTranspose2d(in_channels=64, out_channels=32, kernel_size=3, stride=2, padding=0,
                                        output_padding=0)
        self.relu = nn.ReLU()
        self.conv1 = nn.Conv2d(32, 32, kernel_size=3, stride=1, padding=0)
        self.conv2 = nn.Conv2d(32, 3, kernel_size=2, stride=1, padding=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, out_block2, out_block3, out_block4, out_block5):
        x = self.deconvblock5(out_block5)
        x = x + out_block4
        x = self.deconvblock4(x)
        x = x + out_block3
        x = self.deconvblock3(x)

        x = x + out_block2
        x = self.deconvblock2(x)

        x = self.relu(self.tconv(x))

        x = self.relu(self.conv1(x))

        out = self.sigmoid(self.conv2(x))

        return out


class TTNet(nn.Module):
    def __init__(self, dropout_p, tasks, input_size, thresh_ball_pos_mask, num_frames_sequence,
                 mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225)):
        super(TTNet, self).__init__()
        self.tasks = tasks
        self.ball_local_stage, self.events_spotting, self.segmentation = None, None, None
        self.ball_global_stage = BallDetection(num_frames_sequence=num_frames_sequence, dropout_p=dropout_p)
        if 'local' in tasks:
            self.ball_local_stage = BallDetection(num_frames_sequence=num_frames_sequence, dropout_p=dropout_p)
        if 'event' in tasks:
            self.events_spotting = EventsSpotting(dropout_p=dropout_p)
        if 'seg' in tasks:
            self.segmentation = Segmentation()
        self.w_resize = input_size[0]
        self.h_resize = input_size[1]
        self.thresh_ball_pos_mask = thresh_ball_pos_mask
        self.mean = torch.repeat_interleave(torch.tensor(mean).view(1, 3, 1, 1), repeats=9, dim=1)
        self.std = torch.repeat_interleave(torch.tensor(std).view(1, 3, 1, 1), repeats=9, dim=1)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    def forward(self, resize_batch_input, org_ball_pos_xy):
        pred_ball_local, pred_events, pred_seg, local_ball_pos_xy = None, None, None, None

        pred_ball_global, global_features, out_block2, out_block3, out_block4, out_block5 = self.ball_global_stage(
            self.__normalize__(resize_batch_input))
        if self.ball_local_stage is not None:
            input_ball_local, cropped_params = self.__crop_original_batch__(resize_batch_input, pred_ball_global)
            local_ball_pos_xy = self.__get_groundtruth_local_ball_pos__(org_ball_pos_xy, cropped_params)
            pred_ball_local, local_features, *_ = self.ball_local_stage(self.__normalize__(input_ball_local))
            if self.events_spotting is not None:
                pred_events = self.events_spotting(global_features, local_features)
        if self.segmentation is not None:
            pred_seg = self.segmentation(out_block2, out_block3, out_block4, out_block5)

        return pred_ball_global, pred_ball_local, pred_events, pred_seg, local_ball_pos_xy

    def run_demo(self, resize_batch_input):
        pred_ball_global, global_features, out_block2, out_block3, out_block4, out_block5 = self.ball_global_stage(
            self.__normalize__(resize_batch_input))
        input_ball_local, cropped_params = self.__crop_original_batch__(resize_batch_input, pred_ball_global)
        pred_ball_local, local_features, *_ = self.ball_local_stage(self.__normalize__(input_ball_local))
        pred_events = self.events_spotting(global_features, local_features)
        pred_seg = self.segmentation(out_block2, out_block3, out_block4, out_block5)

        return pred_ball_global, pred_ball_local, pred_events, pred_seg

    def __normalize__(self, x):
        if not self.mean.is_cuda:
            self.mean = self.mean.to(self.device)
            self.std = self.std.to(self.device)

        return (x / 255. - self.mean) / self.std

    def __get_groundtruth_local_ball_pos__(self, org_ball_pos_xy, cropped_params):
        local_ball_pos_xy = torch.zeros_like(org_ball_pos_xy)
        for idx, params in enumerate(cropped_params):
            is_ball_detected, x_min, x_max, y_min, y_max, x_pad, y_pad = params

            if is_ball_detected:
                local_ball_pos_xy[idx, 0] = max(org_ball_pos_xy[idx, 0] - x_min + x_pad, -1)
                local_ball_pos_xy[idx, 1] = max(org_ball_pos_xy[idx, 1] - y_min + y_pad, -1)
                if (local_ball_pos_xy[idx, 0] >= self.w_resize) or (local_ball_pos_xy[idx, 1] >= self.h_resize) or (
                        local_ball_pos_xy[idx, 0] < 0) or (local_ball_pos_xy[idx, 1] < 0):
                    local_ball_pos_xy[idx, 0] = -1
                    local_ball_pos_xy[idx, 1] = -1
            else:
                local_ball_pos_xy[idx, 0] = -1
                local_ball_pos_xy[idx, 1] = -1
        return local_ball_pos_xy

    def __crop_original_batch__(self, resize_batch_input, pred_ball_global):
        batch_size = resize_batch_input.size(0)
        h_original, w_original = 1080, 1920
        h_ratio = h_original / self.h_resize
        w_ratio = w_original / self.w_resize
        pred_ball_global_mask = pred_ball_global.clone().detach()
        pred_ball_global_mask[pred_ball_global_mask < self.thresh_ball_pos_mask] = 0.
        input_ball_local = torch.zeros_like(resize_batch_input)
        original_batch_input = F.interpolate(resize_batch_input, (h_original, w_original))
        cropped_params = []
        for idx in range(batch_size):
            pred_ball_pos_x = pred_ball_global_mask[idx, :self.w_resize]
            pred_ball_pos_y = pred_ball_global_mask[idx, self.w_resize:]
            if (torch.sum(pred_ball_pos_x) == 0.) or (torch.sum(pred_ball_pos_y) == 0.):
                x_center = int(self.w_resize / 2)
                y_center = int(self.h_resize / 2)
                is_ball_detected = False
            else:
                x_center = torch.argmax(pred_ball_pos_x)
                y_center = torch.argmax(pred_ball_pos_y)
                is_ball_detected = True

            x_center = int(x_center * w_ratio)
            y_center = int(y_center * h_ratio)

            x_min, x_max, y_min, y_max = self.__get_crop_params__(x_center, y_center, self.w_resize, self.h_resize,
                                                                  w_original, h_original)
            h_crop = y_max - y_min
            w_crop = x_max - x_min
            x_pad = 0
            y_pad = 0
            if (h_crop != self.h_resize) or (w_crop != self.w_resize):
                x_pad = int((self.w_resize - w_crop) / 2)
                y_pad = int((self.h_resize - h_crop) / 2)
                input_ball_local[idx, :, y_pad:(y_pad + h_crop), x_pad:(x_pad + w_crop)] = original_batch_input[idx, :,
                                                                                           y_min:y_max, x_min: x_max]
            else:
                input_ball_local[idx, :, :, :] = original_batch_input[idx, :, y_min:y_max, x_min: x_max]
            cropped_params.append([is_ball_detected, x_min, x_max, y_min, y_max, x_pad, y_pad])

        return input_ball_local, cropped_params

    def __get_crop_params__(self, x_center, y_center, w_resize, h_resize, w_original, h_original):
        x_min = max(0, x_center - int(w_resize / 2))
        y_min = max(0, y_center - int(h_resize / 2))

        x_max = min(w_original, x_min + w_resize)
        y_max = min(h_original, y_min + h_resize)

        return x_min, x_max, y_min, y_max


if __name__ == '__main__':
    tasks = ['global', 'local', 'event', 'seg']
    ttnet = TTNet(dropout_p=0.5, tasks=tasks, input_size=(320, 128), thresh_ball_pos_mask=0.01,
                  num_frames_sequence=9).to(self.device)
    resize_batch_input = torch.rand((10, 27, 128, 320)).to(self.device)
    org_ball_pos_xy = torch.rand((10, 2)).to(self.device)
    pred_ball_global, pred_ball_local, pred_events, pred_seg, local_ball_pos_xy = ttnet(resize_batch_input,
                                                                                        org_ball_pos_xy)
    if pred_ball_global is not None:
        print('pred_ball_global: {}'.format(pred_ball_global.size()))
    if pred_ball_local is not None:
        print('pred_ball_local: {}'.format(pred_ball_local.size()))
    if pred_events is not None:
        print('pred_events: {}'.format(pred_events.size()))
    if pred_seg is not None:
        print('pred_segmentation: {}'.format(pred_seg.size()))
