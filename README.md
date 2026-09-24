# Computer Graphics with Python & OpenGL

A comprehensive collection of interactive 2D and 3D computer graphics projects and games built using Python and PyOpenGL. This repository demonstrates key computer graphics concepts, including real-time rendering, collision detection, and 3D environment simulation.

---

## 🕹️ Featured Projects

### 3D Games
*   **Highway Escape**: A high-speed 3D racer with fuel management, boosters, and multiple vehicle types.
*   **Bullet Frenzy**: An intense 3D action/shooter game.

### 2D Games & Scenes
*   **Tic-Tac-Toe**: Classic 2D strategy game.
*   **Rock-Paper-Scissors (RPS)**: Interactive hand-game with custom OpenGL UI.
*   **Catch the Diamonds!**: A fast-paced reflex game.
*   **House in Rainfall**: A serene 2D environmental scene demonstrating particle effects.

---

## 📸 Screenshots

### Highway Escape (3D Racing Game)

| DX Box | Gameplay - Car View | Gameplay - Bus View |
|:-----------:|:-------------------:|:-------------------:|
| ![Menu](screenshots/Screenshot%202026-09-24%20232900.png) | ![Car Gameplay](screenshots/Screenshot%202026-09-24%20232925.png) | ![Bus Gameplay](screenshots/Screenshot%202026-09-24%20232950.png) |

| Gameplay - Truck View | Boost Active | Game Over Screen |
|:---------------------:|:------------:|:----------------:|
| ![Truck Gameplay](screenshots/Screenshot%202026-09-24%20233008.png) | ![Boost](screenshots/Screenshot%202026-09-24%20233144.png) | ![Game Over](screenshots/Screenshot%202026-09-24%20233203.png) |

---

## 🎮 Highway Escape - Game Features

| Feature | Description |
|---------|-------------|
| **3 Vehicle Types** | Car, Bus, Truck - each with unique physics & visuals |
| **Fuel System** | Collect green pickups to refuel; empty fuel = game over |
| **Speed Boost** | Yellow pickups activate 5s speed boost with exhaust flames |
| **Ghost Mode** | Cyan pickups grant 5s invincibility (pass through enemies) |
| **3-Lane Highway** | Smooth lane switching with tyre mark effects on braking |
| **Enemy Traffic** | Dynamic spawning with varying speeds |
| **Zebra Crossings** | Pedestrians crossing - fatal if hit! |
| **Autoplay/AI** | Press `A` to watch AI play |
| **Chase Camera** | Dynamic 3rd-person camera following player |

---

## 🎮 Controls

### Highway Escape
| Key | Action |
|-----|--------|
| `←` `→` | Switch lanes (Left/Right) |
| `↑` `↓` | Accelerate / Brake |
| `A` | Toggle Autoplay (AI) |
| `R` | Restart / Return to Menu |
| `Mouse Click` | Menu navigation |

---

## 🛠️ Requirements

*   **Python 3.x** (3.11+ recommended for pygame projects)
*   **PyOpenGL** - `pip install PyOpenGL PyOpenGL_accelerate`
*   **Pygame** - `pip install pygame` (for 2D games: Tic-Tac-Toe, RPS, Catch the Diamonds, House in Rainfall)
*   **FreeGLUT** - Required for GLUT-based projects (usually bundled with PyOpenGL on Windows)

---

## 🚀 Getting Started

```bash
# Clone the repository
git clone https://github.com/yourusername/Computer-Graphics-with-Python-Open-GL.git
cd Computer-Graphics-with-Python-Open-GL

# Install dependencies
pip install PyOpenGL PyOpenGL_accelerate pygame

# Run a game
python "3D Game Highway Escape.py"
# or
python "2D Game Tic Tac Toe.py"
```

---

## 📁 Project Structure

```
Computer-Graphics-with-Python-Open-GL/
├── screenshots/                    # Game screenshots
├── 3D Game Highway Escape.py       # 3D racing game (main project)
├── 3D Game Bullet Frenzy.py        # 3D shooter game
├── 2D Game Tic Tac Toe.py          # Classic Tic-Tac-Toe
├── 2D Game RPS.py                  # Rock-Paper-Scissors
├── 2D Game Catch the Diamonds!.py  # Reflex game
├── 2D Game Amazing DX_box.py       # 3D box demo
├── 2D Scene House in Rainfall.py   # Particle rain scene
└── README.md                       # This file
```

---

## 📜 License

This project is for educational purposes. Feel free to explore, learn, and modify!

---

## 🙏 Acknowledgments

- Built with **PyOpenGL** and **Pygame**
- Inspired by classic arcade racing games
- Great for learning 3D graphics, game loops, and real-time simulation in Python
