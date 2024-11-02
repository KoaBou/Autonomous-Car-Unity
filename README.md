# Autonomous Car Unity

Using simple CV algorithms to develop an autonomous system, Unity used for simulation.

## Table of Contents

- [Introduction](#introduction)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [Demo](#demo)
- [License](#license)

## Introduction

This project aims to develop an autonomous car system using simple computer vision (CV) algorithms. The simulation environment is built in Unity.

## Project Structure

- `models/`: Contains traffic sign detection model.
- `utils/`: Contains computer vision algorithms and control logic.

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/KoaBou/Autonomous-Car-Unity.git
    cd Autonomous-Car-Unity
    ```

2. Install the necessary Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Open the Unity project located in the `Assets/` directory with Unity Hub.

## Usage

1. Open the simulation on web browser: https://via-sim.makerviet.org/
2. Run the controller:
   ```bash
   python web_drive.py
   ```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -am 'Add new feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a pull request.

## Demo Video

Watch the demo video below:

[![Autonomous Car Unity Demo](https://img.youtube.com/vi/EO4QMFLjuzk/0.jpg)](https://youtu.be/EO4QMFLjuzk)



## License

This project is licensed under the MIT License.
