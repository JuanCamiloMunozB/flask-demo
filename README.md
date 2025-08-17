[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/irotxg5d)
## [Problem Statement](https://docs.google.com/document/d/1oo1zXgb5mTcACx2uTkhLDLrZ3LaPFtP1GkHRZvba9hU/edit?usp=sharing)
# 🧠 Sports Betting Expert System

An expert system for football and basketball betting recommendations using a hybrid AI approach that combines symbolic reasoning with probabilistic inference.

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-Web_Framework-black?logo=flask)](https://flask.palletsprojects.com/)
[![Experta](https://img.shields.io/badge/Experta-Rule_Engine-lightgrey)](https://github.com/nilp0inter/experta)
[![pgmpy](https://img.shields.io/badge/pgmpy-Bayesian_Inference-orange)](https://pgmpy.org/)

## 👨‍💻 Team Members

- José Manuel Cardona
- Martín Gómez
- Juan Camilo Muñoz

## 🎯 Project Overview

This project is an AI-driven betting advisor that interacts with users through a conversational interface. It helps users evaluate the safety of sports bets based on current match conditions, player status, and historical performance.

The system supports two sports:

- ⚽ **Football (Soccer)**
- 🏀 **Basketball**

It asks dynamic questions, processes user responses as facts, and delivers recommendations categorized as “safe” or “risky” bets.

## 🚀 Deployment

The system is deployed as a Telegram chat-bot. You can access the live version [here](https://t.me/BetGuide_Bot).

## 🧠 Core Concepts

- **Rule-based reasoning** using Experta: Encodes expert heuristics for evaluating match context.
- **Bayesian networks** using pgmpy: Models uncertainty and probabilistic relationships between match variables.
- **Flask web interface**: Interactive chatbot UI for user input and real-time responses.

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/AyP3/ti2-2025-1-bueno.git
cd ti2-2025-1-bueno
````

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Linux/macOS
venv\Scripts\activate     # On Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
pip install --upgrade frozendict
```

### 4. Run the app

```bash
flask run
```

Visit `http://127.0.0.1:5000/` to start using the system prototype.
