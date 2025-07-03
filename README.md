# 🏓 SpinMaster - Intelligent Table Tennis Analyzer

This project uses the **TTNet deep learning architecture** to analyze table tennis gameplays in real time. It detects the ball, identifies forehand and backhand shots, and provides players with actionable feedback on their performance — including **suggested training modules** for improvement.

---

## 🚀 Features

- 🎯 **Ball Tracking**: Detects and tracks the table tennis ball in real-time video footage.
- 🧠 **Shot Classification**: Classifies player shots as either **forehand** or **backhand**.
- 📈 **Performance Feedback**: Analyzes shot data to highlight the player’s strengths and weaknesses.
- 🏋️‍♂️ **Training Suggestions**: Recommends specific training videos or modules hosted on our website to help players improve.

---

## 📂 Project Structure

```

├── src/
│   ├── config/                   # Training configurations (e.g., train\_1st\_phase.yaml)
│   ├── data\_process/            # Dataset loading, transformations, and processing
│   ├── models/                  # TTNet model and its components
│   ├── utils/                   # Helper functions (e.g., logger, metrics)
│   ├── main.py                  # Entry point for training/inference
│
├── dataset/                     # Training/validation/test datasets
├── checkpoints/                 # Model checkpoints after training
├── runs/                        # TensorBoard logs
├── requirements.txt             # Python dependencies
├── train\_1st\_phase.sh           # First-phase training script (global + segmentation)
└── README.md                    # Project documentation

````

---

## 🧪 How It Works

1. **Input**: The player uploads a gameplay video.
2. **Detection & Analysis**:
   - Ball is tracked using global and local detection modules.
   - Each shot is classified as forehand or backhand.
   - Shot accuracy and distribution are computed.
3. **Feedback Output**:
   - A report is generated highlighting areas for improvement (e.g., "Improve backhand accuracy").
   - Relevant training modules are suggested.

---

## ⚙️ Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/TTNet-TableTennis-Analyzer.git
cd TTNet-TableTennis-Analyzer
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare Dataset

Organize your dataset as follows:

```
dataset/
├── training/
│   ├── images/
│   ├── labels/
│   └── segmentation_masks/
├── validation/
│   └── ...
```

### 4. Train the Model

**Phase 1 (global + segmentation):**

```bash
python src/main.py --config src/config/train_1st_phase.yaml
```

**Phase 2 (full TTNet):**

```bash
python src/main.py --config src/config/train.yaml
```

---

## 📊 Inference and Feedback Generation

To run inference on new gameplay footage:

```bash
python src/inference.py --video_path path/to/your/gameplay.mp4
```

The system will:

* Process the video
* Generate a performance report
* Output suggested training modules

---

## 💡 Example Use Case

> *"After uploading his match footage, Ali received a report stating his forehand was 80% accurate while his backhand dropped to 42%. The system suggested two drills focused on backhand consistency, linking directly to videos on our website."*

---

## 🧠 Model Architecture

* **TTNet** is a multi-branch model with the following components:

  * Global Ball Detection
  * Local Ball Refinement
  * Shot Event Classification (Forehand/Backhand)
  * Segmentation (for context)

---

## 📌 Future Work

* Add real-time analysis mode (live camera input)
* Expand shot classification (smash, loop, push)
* Player detection and movement tracking

---

## 🤝 Contributing

Pull requests and issues are welcome! Feel free to fork the repo, suggest features, or report bugs.

---

## 📜 License

This project is licensed under the MIT License.
```
