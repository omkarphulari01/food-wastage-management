# Local Food Wastage Management System

Python · SQL · Streamlit · Data Analysis

Connects surplus-food providers (restaurants, grocery stores, supermarkets)
with receivers (NGOs, community centers, individuals), stores everything in a
SQL database, and exposes a Streamlit app for filtering, CRUD operations,
15 analysis queries, and EDA.

## Project structure

```
food_project/
├── data/                     # the four CSV datasets
│   ├── providers_data.csv
│   ├── receivers_data.csv
│   ├── food_listings_data.csv
│   └── claims_data.csv
├── generate_sample_data.py   # creates sample CSVs (skip if you have real data)
├── database_setup.py         # loads CSVs -> SQLite (food.db)
├── queries.py                # the 15 SQL analysis queries
├── app.py                    # the Streamlit application
├── requirements.txt
└── README.md
```

## Setup

1. (Optional) Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Add the data:
   - **If you have the real CSVs** from the project's Google Drive links, put
     them in the `data/` folder using these exact filenames:
     `providers_data.csv`, `receivers_data.csv`, `food_listings_data.csv`,
     `claims_data.csv`.
   - **Otherwise**, generate realistic sample data (already included here):
     ```
     python generate_sample_data.py
     ```
     The sample CSVs use the **exact column names** from the project spec, so
     the rest of the pipeline works unchanged when you swap in the real files.

4. Build the database:
   ```
   python database_setup.py
   ```
   This creates `food.db` with four typed tables and primary/foreign keys.

5. Run the app:
   ```
   streamlit run app.py
   ```

## App pages

| Page | What it does |
|------|--------------|
| Dashboard | Headline metrics + quick charts |
| Browse Data | View / download each of the four tables |
| Null Value Analysis | Missing-value report per table with likely reasons |
| Filter & Contact | Filter listings by city, provider, food type, meal type; provider & receiver contact directory |
| Manage Listings (CRUD) | Add, update, delete food listings |
| SQL Queries | All 15 analysis queries with live outputs and auto-charts |
| EDA | 15 visualizations: univariate, bivariate, multivariate, claim analysis |
| Insights & Recommendations | 6 business insights + 4 recommendations, computed from the data |

## The 15 analysis queries

Food Providers & Receivers
1. Providers & receivers per city
2. Provider type contributing the most food
3. Contact info of providers in a specific city
4. Receivers who have claimed the most food

Food Listings & Availability
5. Total quantity of food available
6. City with the highest number of food listings
7. Most commonly available food types

Claims & Distribution
8. Claims made for each food item
9. Provider with the most successful (completed) claims
10. Claim status breakdown (completed / pending / cancelled %)

Analysis & Insights
11. Average quantity of food claimed per receiver
12. Most claimed meal type
13. Total quantity of food donated by each provider
14. Listings expiring soon vs already expired (extra)
15. Claim completion rate by city (extra)

## Using the real datasets

The data in `data/` are the project's real datasets. To use updated data,
replace the four files in `data/` (keep the filenames and column headers) and
re-run `python database_setup.py` — the app also rebuilds `food.db`
automatically on first run if it is missing.

## Deploying online (Streamlit Community Cloud)

This makes the app reachable from any device via a public link.

1. Put this whole folder in a **GitHub repository** (see steps below).
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click **New app**, choose your repository, set the main file to `app.py`,
   and click **Deploy**.
4. The app installs `requirements.txt`, builds the database from the CSVs in
   `data/` automatically, and gives you a public URL like
   `https://your-app.streamlit.app`.

`food.db` is intentionally **not** committed (it is in `.gitignore`); the app
rebuilds it from the CSVs on first run, both locally and on the cloud.

### Pushing to GitHub

```
git init
git add .
git commit -m "Local Food Wastage Management System"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

(Or use GitHub's website: create a new repository, then "Add file" →
"Upload files" and drag this folder's contents in.)

