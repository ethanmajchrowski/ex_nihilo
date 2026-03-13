# Ex Nihilo

A modular 2D factory‑building and automation game written in Python
using Pygame.

The goal of this project is to explore logistics‑driven gameplay inspired
by automation games while keeping the implementation simple, scalable,
and data‑driven. Machines, resources, and recipes are designed to grow
in complexity through infrastructure and processing chains rather than
traditional research trees.

The project is currently an experimental prototype focused on building
the core simulation systems.

------------------------------------------------------------------------

## Features

-   Freeform building placement (with optional grid snapping)
-   Machines with configurable recipes
-   Resource nodes and extraction systems
-   Conveyor logistics and item transport
-   Camera‑based world navigation
-   Modular data‑driven machine/item registry
-   Scalable architecture for expanding production chains

------------------------------------------------------------------------

## Project Goals

This project focuses on experimenting with several design ideas:

-   **Infrastructure‑gated progression** rather than tech trees\
-   **Multi‑stage resource processing pipelines**\
-   **Physical logistics** as the main gameplay challenge\
-   **Simple but extensible architecture**

The codebase is structured so new machines, items, and recipes can be
added without modifying core systems.

------------------------------------------------------------------------

## Requirements

-   Python 3.x\
-   pygame-ce
-   colorlog


Install dependencies:

    pip install pygame-ce colorlog

------------------------------------------------------------------------

## Running the Game

Clone the repository:

    git clone https://github.com/ethanmajchrowski/ex_nihilo.git
    cd ex_nihilo

Run the main file:

    python main.py

------------------------------------------------------------------------

## Project Structure

    ex_nihilo/
    │
    ├─ main.py            # Game entry point
    ├─ systems/           # Core simulation systems
    ├─ machines/          # Machine definitions and logic
    ├─ items/             # Item and resource definitions
    ├─ rendering/         # Rendering and camera systems
    ├─ ui/                # Interface tools and panels
    └─ data_registry.py   # Data-driven machine/item registry

------------------------------------------------------------------------

## Current Status

This is an **early prototype**. This was worked on as a summer project and development is not active right now.

Future focus areas include:

-   machine placement logic
-   item transport systems
-   scalable machine / recipe architecture

------------------------------------------------------------------------

## Inspiration

Automation and factory‑building games such as:

-   Factorio
-   modded Minecraft automation systems
-   industrial simulation games

The design emphasizes **emergent complexity from simple systems** rather
than large handcrafted progression trees.
