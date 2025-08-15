# Perceptron Visualizer

An interactive **Pygame** application to visualize the **Perceptron learning algorithm** in real time.  
Click to add labeled points, train the perceptron step-by-step watching the decision boundary evolve over iterations or instantly. Perfect for teaching and exploring the geometric intuition behind linear classification.

Inspired by my interest in machine learning and interactive visualizations, the perceptron is implemented from scratch using numpy.

---

## 📸 Some drafts of the development progress
![WhatsApp Görsel 2025-08-15 saat 16 01 55_ba597d35](https://github.com/user-attachments/assets/7827e921-58a9-4f11-9f36-8f85175c58d1)

---

## 🧠 Features
- 🖱️ Interactive point placement – right-click to add labeled points for two classes.
- ⚡ Batch training – instantly finds a separating hyperplane if one exists.
- 🎞️ Animated training – step-by-step perceptron updates over time.
- 🎨 Dynamic decision boundary visualization – shows last few iterations in different colors.
- 🔍 Zoom and pan controls – navigate the coordinate space freely.
- 📏 Real-time coordinate display – always see your cursor position in world coordinates.
- 🗑️ Reset functionality – clear points and start fresh with a single key press.

---

## 🧰 Installation
Recommended: use poetry.

# Clone the repo
git clone https://github.com/yourusername/perceptron-visualizer.git
cd perceptron-visualizer

# Create Virtual Environment and Install dependencies
poetry install

---

## ▶️ Running the App
# Using poetry
poetry run python src/main.py

# Or plain Python
python src/main.py

---

## 🧪 Requirements
- Python 3.10+
- pygame
- pygame_gui
- numpy

If not using poetry, install with:
pip install pygame pygame_gui numpy

---

## ✍️ Usage
- **Add Points** – right-click while a class button is selected in the UI.
- **Train** – click **Train Perceptron** for batch mode or **Animated Train** for stepwise learning.
- **Pan** – hold left mouse button and drag.
- **Zoom** – scroll wheel in/out.
- **Reset** – press **R** to clear all points and boundaries.

---

## 🧹 To Do
- Save/load point sets
- Adjustable training speed
- Perceptron with margin
- Display misclassified points count in real time
- Support more than two classes (multiclass perceptron)
- Export visualization as image/GIF

---

## 🧑‍💻 Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss your ideas.

---

## 📄 License
MIT License. See LICENSE for details.
