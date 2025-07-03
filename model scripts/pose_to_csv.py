# pose_to_csv.py

import cv2
import csv
import mediapipe as mp
import time

def generate_csv_from_video(video_path, csv_output_path='match_data.csv'):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    cap = cv2.VideoCapture(video_path)
    frame_rate = 10
    frame_count = 0

    csv_data = []

    def get_timestamp(cap):
        return time.strftime('%H:%M:%S', time.gmtime(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000))

    def get_player_side(x_pos, width):
        return 'player1' if x_pos < width / 2 else 'player2'

    def infer_shot_type(landmarks):
        rw_y = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y
        re_y = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y
        return 'forehand' if rw_y < re_y else 'backhand'

    current_server = 'player1'
    current_hitter = current_server
    rally_shots = 0
    max_rally_length = 6
    next_shot_is_serve = True

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % frame_rate != 0:
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(frame_rgb)
        timestamp = get_timestamp(cap)

        if result.pose_landmarks:
            width = frame.shape[1]
            landmarks = result.pose_landmarks.landmark
            x_pos = landmarks[mp_pose.PoseLandmark.NOSE.value].x * width

            if next_shot_is_serve:
                shot_type = 'serve'
                success = 1
                point_winner = ''
                rally_shots = 0
                current_hitter = current_server
                next_shot_is_serve = False
            else:
                current_hitter = 'player2' if current_hitter == 'player1' else 'player1'
                shot_type = infer_shot_type(landmarks)
                point_winner = ''
                rally_shots += 1

                end_rally = rally_shots >= max_rally_length or frame_count % 35 == 0
                if end_rally:
                    success = 0
                    point_winner = 'player1' if current_hitter == 'player2' else 'player2'
                    current_server = point_winner
                    next_shot_is_serve = True
                else:
                    success = 1

            csv_data.append([timestamp, current_hitter, shot_type, success, point_winner])

    cap.release()
    pose.close()

    with open(csv_output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'player', 'shot_type', 'success', 'point_winner'])
        writer.writerows(csv_data)

    print(f"✅ CSV generated: {csv_output_path}")
