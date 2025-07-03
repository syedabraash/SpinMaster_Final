import os
import sys
from pose_to_csv import generate_csv_from_video
from csv_analyzer import analyze_match_csv

def analyze_single_video(video_path):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    csv_path = f"{video_name}.csv"

    print(f"\n📼 Processing: {video_name}")
    generate_csv_from_video(video_path, csv_path)

    print(f"\n📊 Analysis for: {video_name}")
    analyze_match_csv(csv_path)

def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_match.py path/to/video_or_folder")
        return

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        # Folder: process all .mp4 files
        video_files = [f for f in os.listdir(input_path) if f.endswith('.mp4')]
        for file in video_files:
            full_path = os.path.join(input_path, file)
            analyze_single_video(full_path)
    else:
        # Single video
        analyze_single_video(input_path)

if __name__ == "__main__":
    main()
