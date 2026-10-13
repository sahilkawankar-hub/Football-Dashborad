# ⚽ Football Player Performance Analytics Dashboard

An interactive, portfolio-quality football (soccer) analytics dashboard built with **Python**, **Streamlit**, and **Plotly**.

> ⚠️ **SYNTHETIC DATA DISCLAIMER**
> All player statistics in this project are **artificially generated** using NumPy with a fixed random seed (42). They do **not** represent any real players, real clubs, or real-world match results. The data is clearly labelled as synthetic throughout the application.

---

## Features

| Page | What you'll find |
|---|---|
| **Overview** | 5 KPI cards, top-10 scorers bar chart, goals & assists by team |
| **Player Analysis** | Goals vs assists scatter, shots vs goals with trendline, single-player radar profile, 2-player head-to-head comparison |
| **Team Analysis** | Goals & assists grouped bar, avg rating bar, squad size pie, top performer per team |
| **Position Analysis** | Avg stats per position, multi-metric comparison, squad composition donut, top-rated player per position |
| **Data Explorer** | Searchable, sortable full stats table, column selector, CSV download |

**Sidebar filters** (cascading): Season → Team → Position → Player

---

## Project Structure

```
football-analysis-dashboard/
├── app.py                        # Home / Overview page (Streamlit entry point)
├── pages/
│   ├── 1_Player_Analysis.py      # Player Analysis page
│   ├── 2_Team_Analysis.py        # Team Analysis page
│   ├── 3_Position_Analysis.py    # Position Analysis page
│   └── 4_Data_Explorer.py        # Data Explorer + CSV download
├── utils.py                      # Shared: load_data, render_sidebar, apply_theme
├── generate_data.py              # One-time synthetic data generator (already run)
├── football_players.csv          # Synthetic dataset — 300 rows, 19 columns
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

---

## Dataset Schema

300 rows — 100 synthetic players × 3 seasons (2021/22, 2022/23, 2023/24).

| Column | Type | Notes |
|---|---|---|
| player_id | int | Unique player identifier |
| player_name | str | Synthetic name |
| season | str | 2021/22, 2022/23, 2023/24 |
| team | str | One of 10 synthetic clubs |
| position | str | GK / DEF / MID / FWD |
| age | int | 18–35 |
| matches_played | int | 15–38 |
| minutes_played | int | Derived from matches × ~75 min |
| goals | int | Position-weighted |
| assists | int | Position-weighted |
| shots | int | ≥ goals, position-weighted |
| shots_on_target | int | ≤ shots, ≥ goals |
| passes | int | Position-weighted |
| pass_accuracy | float | 0.62–0.94 |
| dribbles | int | Position-weighted |
| tackles | int | Position-weighted |
| yellow_cards | int | 0–6 |
| red_cards | int | 0–1 |
| rating | float | 5.0–9.5 composite score |

---

## Local Setup

### Prerequisites

- Python 3.10 or later
- pip

### Steps

```bash
# 1. Clone or download the project
git clone https://github.com/your-username/football-analytics-dashboard.git
cd football-analytics-dashboard

# 2. Create and activate a virtual environment (recommended)
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Re-generate the synthetic dataset
#    The CSV is already committed — only needed if you want to regenerate it.
python generate_data.py

# 5. Run the app
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**.

---

## Deploying to Streamlit Cloud

1. Push this project to a public GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app** → select your repo → set **Main file path** to `app.py`.
4. Click **Deploy**. Streamlit Cloud installs `requirements.txt` automatically.

> **Note:** `football_players.csv` must be committed to the repo so the deployed app can read it. No external data source or API key is required.

---

## Screenshots

*(Add screenshots here after running the app locally)*

| Overview page | Player Analysis |
|---|---|
| ![Overview](screenshots/overview.png) | ![Player Analysis](screenshots/player_analysis.png) |

---

## Contributing

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/my-improvement`.
3. Commit your changes and open a pull request.

Please keep the **synthetic data disclaimer** visible in any derived work.

---

## License

MIT — free to use and modify. Attribution appreciated.
