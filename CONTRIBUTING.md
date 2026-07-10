# Contributing to Simulyn AI

First off, thank you for considering contributing to Simulyn! We welcome contributions from the community to help us build the next generation of PyTorch-accelerated Decision Intelligence.

## 🚀 How to Contribute

1. **Fork the repository** on GitHub.
2. **Clone your fork** locally.
3. **Create a new branch** for your feature or bug fix (`git checkout -b feature/your-feature-name`).
4. **Make your changes** and ensure they are tested (especially any PyTorch/ROCm tensor logic).
5. **Commit your changes** with descriptive commit messages.
6. **Push your branch** to your fork.
7. **Open a Pull Request** against our `main` branch.

## 💻 Development Setup

Please refer to the `README.md` for the Quickstart guide on setting up the FastAPI backend and D3.js frontend locally. 

If you are modifying the PyTorch backend, please ensure you have an environment capable of running AMD ROCm for hardware acceleration, although CPU fallback is supported for local development.

## 🐛 Bug Reports & Feature Requests

Please use the GitHub Issues tab to report bugs or suggest features. Provide as much detail as possible, including system specs (especially GPU architecture) if reporting a PyTorch engine issue.
