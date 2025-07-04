![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web_App-000000?logo=flask)
![License](https://img.shields.io/github/license/syedabraash/spinmaster_final)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Made With ❤️](https://img.shields.io/badge/Made%20with-%E2%9D%A4-red)

# 🚀 SpinMaster | AI-Powered Table Tennis Coach

SpinMaster is your ultimate virtual table tennis analyst — a full-stack AI application that breaks down match footage, identifies gameplay weaknesses, and recommends personalized training modules to help players level up their performance like the pros.

---

## 🌟 Features

- 🎥 **Video Upload Interface** — Upload match videos directly through a sleek web interface.
- 🤖 **Automated Pose Detection** — Detects elbow angles and arm orientation to classify forehand and backhand shots.
- 📊 **Match Analysis Engine** — Calculates shot success rates and determines weak areas.
- 🧠 **TTNet Integration (Modular)** — Built to support advanced table tennis models like [TTNet](https://github.com/OSAI-ai/TTNet) for precise shot classification.
- 📈 **Dynamic Leaderboards** — Rank top players using comic-inspired UI.
- 🎓 **Smart Training Suggestions** — Recommends YouTube tutorials based on your weaknesses.
- 🔐 **User Authentication** — Register and log in to track your progress (with session support).
- 🌐 **Flask-based Local Server** — Lightweight, local-first deployment with modern UI/UX.

---

## 🧩 Architecture Breakdown

### 1. `pose_to_csv.py`  
Utilizes [MediaPipe](https://github.com/google/mediapipe) pose landmarks to:
- Extract joint positions (specifically elbow angles)
- Identify the shot type (forehand/backhand) using angle deltas
- Timestamp each frame
- Track shot success based on rally outcome
- Export structured `.csv` data for analysis

### 2. `csv_analyzer.py`  
Reads the generated CSV and:
- Computes per-player statistics
- Calculates shot-wise success ratios
- Determines point and match winners
- Feeds performance summary to front-end (forehand/backhand strengths)

### 3. `analyze_match.py`  
A simple entry point that merges the above scripts for batch processing or CLI testing.

### 4. `app.py`  
Your all-in-one Flask server:
- Manages video uploads
- Runs the full analysis pipeline
- Displays real-time feedback
- Handles user login/registration
- Renders leaderboard and training module pages

---

## 🧠 TTNet Model (Optional Extension)

SpinMaster is built with modularity in mind. While it runs a lightweight elbow-angle classification model by default, it also supports powerful integrations like:
> A dedicated table tennis recognition model trained on extensive datasets to detect:
- Forehand / Backhand
- Serve / Smash / Topspin
- Ball location & player segmentation

🧪 We're currently integrating TTNet as an alternate backend for precision-grade analysis using deep learning.

---

## 🎨 UI & UX Highlights

- **Pastel & Neon Dark Mode** 🎨
- Glassmorphism cards and overlays
- Background video or image with motivational quotes
- Embedded YouTube training cards
- Responsive layout (desktop-first)

---

## 🚀 Getting Started

1. Clone the repository  
```bash
   git clone https://github.com/yourusername/spinmaster.git
   cd spinmaster
````

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Launch the Flask app

   ```bash
   python app.py
   ```

4. Open in browser: `http://127.0.0.1:5000/`

---

## 📁 Folder Structure

```
SpinMaster/
├── app.py
├── pose_to_csv.py
├── csv_analyzer.py
├── analyze_match.py
├── users.json
├── uploads/
├── static/
│   ├── styles.css
│   ├── login-icon.png
│   └── tt.jpg / tt.mp4
└── templates/
    ├── index.html
    ├── login.html
    ├── leaderboard.html
    └── training.html
```

---

## 👤 Author

**Abraash Syed**
Futurist | AI Developer | Table Tennis Enthusiast 🏓
[GitHub](https://github.com/syedabraash) • [LinkedIn](https://www.linkedin.com/in/syedabraash/)

---

## Acknowledgments
Special thanks to the incredible individuals and organizations whose work and contributions made SpinMaster possible:

Lab OSAI — For providing the table tennis datasets used to train and test TTNet
Nguyen Mau Dzung — For detailed guidance and model structure of the TTNet architecture
MediaPipe — For enabling seamless pose tracking and landmark detection
Nicholas Renotte — For insightful tutorials and guidance on object recognition using the Roboflow platform
WTT (World Table Tennis) — For global player rankings and match insights
And all other open-source contributors, documentation authors, and creators whose tools and knowledge supported the development of this project.

Without this collective foundation, SpinMaster would not exist.

---

## 📄 License

MIT License © 2025 Abraash Syed
Feel free to use, contribute, and help SpinMaster grow!

> “Master the spin, master the game.”
