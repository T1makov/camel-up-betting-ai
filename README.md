# Camel Up Betting AI

A Python simulator and betting advisor for **Camel Up**, focused on modeling randomized camel movement, leg betting, and expected-value-based decision making.

This project simulates the core mechanics of a Camel Up leg and includes an AI advisor that estimates each camel’s probability of finishing first or second. The advisor then uses those probabilities to evaluate available betting tickets and recommend statistically strong choices.

## Overview

Camel Up is a stochastic board game where camels move according to randomized dice rolls. Because camels can stack on top of each other and move together, each roll can significantly change the race state.

This project models those mechanics and uses probability simulation to answer questions like:

* Which camel is most likely to finish first this leg?
* Which camel is most likely to finish second?
* Which available betting ticket has the highest expected value?
* How do exhaustive enumeration and Monte Carlo simulation compare?

## Features

* Simulates camel movement, stacking, dice rolls, and track position updates
* Models leg betting tickets and payout logic
* Supports multiple players
* Includes an AI betting advisor
* Computes first-place and second-place probabilities
* Uses exhaustive enumeration of remaining dice outcomes
* Includes Monte Carlo simulation for experimental probability estimates
* Calculates expected value for available bets
* Includes unit tests for board logic, dice behavior, payouts, and AI analysis

## Project Structure

```text
camel-up-betting-ai/
├── AI.py              # AI probability analysis and betting recommendations
├── Board.py           # Board state, camel movement, rankings, and tickets
├── CamelUp.py         # Main game loop and player actions
├── Player.py          # Player money and betting tickets
├── Pyramid.py         # Dice rolling logic
├── requirements.txt   # Python dependencies
├── README.md          # Project documentation
└── tests/             # Unit tests
```

## How the AI Works

The AI advisor analyzes the current board state and estimates how likely each camel is to finish the leg in first or second place.

For the remaining dice in the leg, each possible future roll has:

* a camel color
* a movement value of 1, 2, or 3

The AI uses two approaches:

### 1. Exhaustive Enumeration

The AI generates every possible sequence of remaining dice rolls, simulates each sequence, and counts how often each camel finishes first or second.

This gives an exact probability estimate for the current leg state.

### 2. Monte Carlo Simulation

The AI also supports repeated random simulations. Instead of checking every possible future sequence, it samples many possible outcomes and estimates probabilities experimentally.

This is useful for comparing exact and sampled probability estimates.

## Expected Value Calculation

For each available betting ticket, the AI calculates expected value using the probability that the selected camel finishes first, second, or outside the top two.

The formula is:

```text
EV = ticket_value × P(first) + 1 × P(second) - 1 × P(other)
```

Where:

```text
P(other) = 1 - P(first) - P(second)
```

The AI can then recommend the bet with the highest expected value.

## Installation

Clone the repository:

```bash
git clone https://github.com/YOUR-USERNAME/camel-up-betting-ai.git
cd camel-up-betting-ai
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Game

Run:

```bash
python3 CamelUp.py
```

During a turn, players can choose actions such as:

```text
r = roll a die
b = take a betting ticket
a = ask the AI advisor for analysis
```

The game simulates a leg, processes payouts, and displays player results.

## Running Tests

Run the test suite with:

```bash
python3 -m pytest
```

## Current Scope

This project focuses on simulating leg-level Camel Up betting decisions rather than implementing every rule from the full board game. The main goal is to model probabilistic race outcomes and use those probabilities to make better betting decisions.

## Future Improvements

Potential extensions include:

* Full-race simulation across multiple legs
* Support for overall winner and loser bets
* More polished command-line interface
* Strategy comparison between human players and AI agents
* Visualization of probability changes after each roll
* Stronger Monte Carlo benchmarking for larger game variants

## Disclaimer

This is an educational programming project inspired by the board game Camel Up. It is not affiliated with the official game or publisher.
