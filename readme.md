# Oakhill Engine & Game Project

**A data-driven 2D Game Engine and RPG implementation built from scratch in Python.**

## Project Overview

Oakhill is more than just a game; it is a custom-built 2D game engine designed to demonstrate advanced software engineering concepts. The project prioritizes modular architecture, separation of concerns, and tool development.

Unlike standard projects that rely heavily on pre-made engines (like Unity or Godot), Oakhill implements core systems natively, including a **custom programming language interpreter**, a **level editor**, and a **resource management system**.

## Technical Highlights

This project demonstrates proficiency in the following areas:

* **Computer Science Fundamentals:** Implementation of a custom recursive descent parser, lexer, and Abstract Syntax Tree (AST) for game scripting.
* **Object-Oriented Programming (OOP):** Heavy utilization of inheritance, polymorphism, and encapsulation across the Entity framework.
* **Design Patterns:** Implementation of **Singleton** (Managers), **Factory** (Entity creation), **Observer** (Event handling), and **State** (Game state machine) patterns.
* **Tooling & DevOps:** Creation of internal tools (`level_editor.py`, `linter.py`) to streamline the development pipeline.
* **Data-Driven Design:** All game assets, maps, and entity configurations are loaded dynamically via JSON, allowing for rapid iteration without code changes.

## System Architecture

The codebase is organized into distinct modules to ensure maintainability and scalability:

```text
Oakhill/
├── src/
│   ├── core/           # Main Game Loop, State Machine, and Result handling
│   ├── entities/       # Polymorphic Game Objects (Player, Enemies, Interactables)
│   ├── components/     # Reusable logic (Animations, Behaviours)
│   ├── managers/       # Centralized subsystems (Resources, Audio, UI, Events)
│   ├── scripting/      # Custom Interpreter Implementation (Lexer, Parser, AST)
│   └── editor_systems/ # GUI components for the custom Level/UI Editor
├── tools/              # Dev tools (Linter, Script Runner)
├── data/               # JSON configuration files (Assets, Maps, Templates)
└── main.py             # Application Entry Point

```

### 1. Custom Scripting Language (`src/scripting`)

To allow for complex narrative events without hardcoding logic, I implemented a domain-specific language (DSL) interpreter.

* **Lexer.py:** Tokenizes raw text input.
* **Parser.py & AST.py:** Constructs an Abstract Syntax Tree to represent logical structures.
* **Interpreter.py:** Executes the tree, handling variables, control flow, and game state manipulation.
* **NativeProxy.py:** Bridges the custom language with the Python game engine.

### 2. Entity Management (`src/entities` & `src/components`)

Game objects utilize a hybrid inheritance/component model. Base classes define core properties, while specialized components (like `Animations.py` and `Behaviour.py`) handle logic, decoupling behavior from data.

### 3. Manager Pattern (`src/managers`)

The engine utilizes centralized managers to handle global state:

* **ResourceManager:** Asynchronous loading and caching of assets (images, sounds).
* **EventManager:** Handles the pub/sub event system to decouple game systems.
* **TweenManager:** Handles interpolation for smooth animations and transitions.
* **UIManager:** Manages the GUI stack and user interaction.

## Internal Tools

To facilitate development, I built custom tooling alongside the engine:

* **Level Editor (`level_editor.py`):** A graphical interface for placing tiles, defining collision zones, and setting up entity triggers.
* **UI Editor (`ui_editor.py`):** A tool to visually design user interfaces and generate the corresponding JSON layouts.
* **Linter (`tools/linter.py`):** A custom static analysis script to ensure code quality and consistency across the project.

## Getting Started

### Prerequisites

* Python 3.10 or higher
* pygame, and PySide6

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/oakhill.git

```


2. Navigate to the project directory:
```bash
cd oakhill

```


3. Run the game:
```bash
python main.py

```



### Running the Tools

To launch the level editor:

```bash
python level_editor.py

```