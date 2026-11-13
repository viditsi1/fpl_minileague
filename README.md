# FPL Mini-League Differential Tracker

A Python script that interacts with the official **Fantasy Premier League (FPL)** API to generate a real-time **Differential Leaderboard** for your specific mini-league. It automatically detects and supports both **FPL Classic** and **FPL Draft** leagues!

---

## Table of Contents
- [Features](#features)
- [How It Works](#how-it-works)
- [Python Installation Guide](#python-installation-guide)
  - [macOS (Recommended via Homebrew)](#macos-recommended-via-homebrew)
  - [macOS Troubleshooting](#macos-troubleshooting)
  - [Windows](#windows)
  - [Linux (Ubuntu / Debian / Fedora)](#linux-ubuntu--debian--fedora)
- [Project Setup](#project-setup)
- [Finding Your League ID & Gameweek](#finding-your-league-id--gameweek)
- [Running the Script](#running-the-script)
- [Sample Output](#sample-output)
- [Configuration Options](#configuration-options)

---

## Features
- **Dynamic Input**: Interactively prompts for **League ID** and **Gameweek ID**.
- **Dual Support**: Automatically handles both **Classic Mini-Leagues** and **Draft Leagues**.
- **Mini-League Ownership Calculation**: Computes ownership percentage *specifically within your mini-league*, rather than global ownership.
- **Starters vs. Bench**: Option to count the full 15-man squad or only active starting XI players in ownership calculations.
- **Differential Ranking**: Sorts candidate players by **lowest mini-league ownership first**, followed by **highest gameweek points**, surfacing the true differential heroes who won you the gameweek.

---

## How It Works
1. Connects to the FPL `bootstrap-static` endpoint to map player IDs to web names.
2. Pulls live match data and gameweek points for every player via `event/{gameweek}/live`.
3. Queries your mini-league standings (trying Classic first, then falling back to Draft).
4. Loops through every manager's team picks for the specified gameweek and calculates mini-league ownership.
5. Filters out players with zero or negative points, ranks the top differentials, and prints a formatted leaderboard.

---

## Python Installation Guide

### macOS (Recommended via Homebrew)

macOS comes with an older system Python that is restricted and lacks modern package management. The cleanest way to manage Python on a Mac is via [Homebrew](https://brew.sh/).

#### 1. Install Homebrew (if not already installed)
Open your **Terminal** (`Command + Space`, type `Terminal`, and press Enter) and run:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Ensure Xcode Command Line Tools are Installed
Homebrew and Python build tools require the Xcode CLI developer tools:
```bash
xcode-select --install
```
*(If a prompt appears, click **Install** and wait for it to complete.)*

#### 3. Install Python 3
```bash
brew install python
```

#### 4. Add Homebrew to your PATH (Apple Silicon Macs: M1/M2/M3/M4)
Ensure your terminal uses Homebrew's Python:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

#### 5. Verify Installation
```bash
python3 --version
pip3 --version
```
You should see `Python 3.12+` or `Python 3.13+`.

---

### macOS Troubleshooting

If you encountered errors while setting up Python or Homebrew on Mac:

#### Problem 1: `macos_version.rb` or outdated Homebrew error
**Error:** `undefined method ... in macos_version.rb` or Homebrew complains about unsupported macOS versions.  
**Fix:** Update and reset your Homebrew installation:
```bash
cd $(brew --repository)
git fetch
git reset --hard origin/master
brew update
brew install python
```

#### Problem 2: `pip: command not found`
**Fix:** On macOS, the package manager is installed as `pip3` to prevent conflicts with legacy macOS components. Always use:
```bash
pip3 install <package>
# or inside a virtual environment:
pip install <package>
```

#### Problem 3: `NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+`
**Cause:** Older system Python (e.g. macOS default Python 3.9) uses LibreSSL instead of OpenSSL.  
**Fix:** Pin `urllib3` to version 1.x:
```bash
pip3 install "urllib3<2"
```
*(Or switch to modern Homebrew Python as described above, which uses OpenSSL).*

---

### Windows

1. Open **PowerShell** or **Command Prompt** and run:
   ```cmd
   winget install Python.Python.3
   ```
2. Alternatively, download the official installer from [python.org](https://www.python.org/downloads/).
   > **Important:** During installation, check the box that says **"Add Python to PATH"** before clicking Install.
3. Verify in a new Command Prompt:
   ```cmd
   python --version
   pip --version
   ```

---

### Linux (Ubuntu / Debian / Fedora)

- **Ubuntu / Debian**:
  ```bash
  sudo apt update
  sudo apt install python3 python3-pip python3-venv -y
  ```
- **Fedora**:
  ```bash
  sudo dnf install python3 python3-pip -y
  ```

---

## Project Setup

### 1. Clone the Repository
```bash
git clone https://github.com/viditsi1/fpl_minileague.git
cd fpl_minileague
```

### 2. Set Up a Virtual Environment (Recommended)
Using a virtual environment isolates project dependencies and prevents PEP 668 ("externally-managed-environment") warnings:

```bash
# Create a virtual environment named 'venv'
python3 -m venv venv

# Activate the virtual environment
# On macOS / Linux:
source venv/bin/activate

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.\venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

## Finding Your League ID & Gameweek

### FPL Classic League ID
1. Log into [fantasy.premierleague.com](https://fantasy.premierleague.com/).
2. Navigate to the **Leagues & Cups** tab.
3. Click on your Mini-League name to view the standings.
4. Check the browser URL bar:
   ```
   https://fantasy.premierleague.com/leagues-classic/19308/standings/c
                                                     ^^^^^
                                                This is your League ID
   ```

### FPL Draft League ID
1. Log into [draft.premierleague.com](https://draft.premierleague.com/).
2. Click on your League.
3. Check the browser URL bar:
   ```
   https://draft.premierleague.com/league/12345
                                          ^^^^^
                                     This is your League ID
   ```

### Gameweek ID
- Enter the integer for the gameweek you wish to analyze (e.g. `10` for Gameweek 10).

---

## Running the Script

Ensure your virtual environment is activated, then run:

```bash
python3 fpl.py
```

You will be prompted:
```text
Enter League ID: 19308
Enter Gameweek ID: 10

Fetching data, please wait...
```

---

## Sample Output

```text
=== Warrior's Punt (Classic | 50 Teams) | GW10 Mini-League Differentials ===

 1. Ødegaard        | 11 pts | Owned by 1/50 (  2.0%) | OG 11 (Akshay Sathyanarayanan)
 2. B.Fernandes     | 10 pts | Owned by 1/50 (  2.0%) | Rebel Devils (Prasad P)
 3. Barcola         |  5 pts | Owned by 1/50 (  2.0%) | OCD XV (Mithil Chavan)
 4. Cunha           |  5 pts | Owned by 1/50 (  2.0%) | TrueBlueBhat (parikshit bhat)
 5. A.Becker        |  4 pts | Owned by 1/50 (  2.0%) | Cunha Matata (sanjay balrajani)
 6. Tzolis          |  3 pts | Owned by 1/50 (  2.0%) | Immortals (Sid Nambiar)
 7. Pickford        |  3 pts | Owned by 1/50 (  2.0%) | Snaydoooo (Snehanshu Gupta)
 8. Rayan           |  2 pts | Owned by 1/50 (  2.0%) | Wirtz Case Scenario (Falak Shah)
 9. Truffert        |  2 pts | Owned by 1/50 (  2.0%) | OG 11 (Akshay Sathyanarayanan)
10. Robertson       |  2 pts | Owned by 1/50 (  2.0%) | OCD XV (Mithil Chavan)
11. Doku            |  2 pts | Owned by 1/50 (  2.0%) | VishalBull (Vishal Bulchandani)
12. N.Williams      |  2 pts | Owned by 1/50 (  2.0%) | Snaydoooo (Snehanshu Gupta)
13. Robinson        |  2 pts | Owned by 1/50 (  2.0%) | SafedNeela11 (Rajit Rajan)
14. Kamada          |  2 pts | Owned by 1/50 (  2.0%) | SafedNeela11 (Rajit Rajan)
15. Havertz         |  2 pts | Owned by 1/50 (  2.0%) | ThinkOut (suraj khandelwal)
```

---

## Configuration Options

Open [fpl.py](file:///Users/vidit/fpl/fpl/fpl_minileague/fpl.py) to customize tracking behavior:

| Variable | Default | Description |
| :--- | :--- | :--- |
| `COUNT_BENCH_IN_OWNERSHIP` | `True` | Set to `True` to count all 15 squad spots toward mini-league ownership. Set to `False` to only count active starters. |
| `MAX_LEAGUE_OWNERSHIP_COUNT` | `None` | Set to `1` to filter strictly for unique 1-of-1 differential picks, or `None` to display all low-ownership picks sorted ascending. |

---

## License
MIT License. Feel free to use, modify, and share!
