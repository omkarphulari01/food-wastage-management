"""
generate_sample_data.py
------------------------
Creates realistic sample CSVs that match the schemas described in the
project document. Run this only if you do NOT have the real CSVs yet.

When you get the real datasets from Google Drive, just place these files
in the ./data folder with the SAME column names and skip this script:
    data/providers_data.csv
    data/receivers_data.csv
    data/food_listings_data.csv
    data/claims_data.csv
"""

import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------------- reference pools
CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
    "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
]

PROVIDER_TYPES = ["Restaurant", "Grocery Store", "Supermarket", "Bakery", "Catering Service"]
RECEIVER_TYPES = ["NGO", "Community Center", "Individual", "Shelter", "Charity"]
FOOD_TYPES = ["Vegetarian", "Non-Vegetarian", "Vegan"]
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snacks"]
CLAIM_STATUS = ["Completed", "Pending", "Cancelled"]

FOOD_NAMES = [
    "Rice", "Bread", "Curry", "Pasta", "Salad", "Soup", "Pizza", "Sandwich",
    "Biryani", "Dal", "Roti", "Noodles", "Fruit Box", "Vegetable Mix",
    "Chicken Wrap", "Paneer Tikka", "Idli", "Dosa", "Samosa", "Cake",
]

PROVIDER_NAME_PARTS_A = ["Green", "Royal", "Fresh", "Golden", "City", "Sunrise",
                         "Spice", "Garden", "Daily", "Urban"]
PROVIDER_NAME_PARTS_B = ["Kitchen", "Foods", "Mart", "Bakery", "Bistro",
                         "Grocers", "Caterers", "Diner", "Pantry", "Deli"]

RECEIVER_NAME_PARTS_A = ["Helping", "Hope", "Care", "Unity", "Seva", "Annapurna",
                         "Smile", "Bright", "Shelter", "Open"]
RECEIVER_NAME_PARTS_B = ["Hands", "Foundation", "Trust", "Center", "Mission",
                         "Home", "Society", "Network", "Welfare", "Kitchen"]

STREETS = ["MG Road", "Station Road", "Park Street", "Market Lane", "Gandhi Nagar",
           "Lake View", "Hill Road", "Church Street", "Civil Lines", "Mall Road"]


def phone():
    return f"+91-{random.randint(70000, 99999)}{random.randint(10000, 99999)}"


# ---------------------------------------------------------------- providers
N_PROVIDERS = 120
providers = []
for pid in range(1, N_PROVIDERS + 1):
    name = f"{random.choice(PROVIDER_NAME_PARTS_A)} {random.choice(PROVIDER_NAME_PARTS_B)}"
    providers.append({
        "Provider_ID": pid,
        "Name": name,
        "Type": random.choice(PROVIDER_TYPES),
        "Address": f"{random.randint(1, 250)}, {random.choice(STREETS)}",
        "City": random.choice(CITIES),
        "Contact": phone(),
    })
providers_df = pd.DataFrame(providers)

# ---------------------------------------------------------------- receivers
N_RECEIVERS = 90
receivers = []
for rid in range(1, N_RECEIVERS + 1):
    name = f"{random.choice(RECEIVER_NAME_PARTS_A)} {random.choice(RECEIVER_NAME_PARTS_B)}"
    receivers.append({
        "Receiver_ID": rid,
        "Name": name,
        "Type": random.choice(RECEIVER_TYPES),
        "City": random.choice(CITIES),
        "Contact": phone(),
    })
receivers_df = pd.DataFrame(receivers)

# ---------------------------------------------------------------- food listings
N_LISTINGS = 400
listings = []
today = datetime.now().date()
for fid in range(1, N_LISTINGS + 1):
    prov = providers_df.sample(1).iloc[0]
    expiry = today + timedelta(days=random.randint(-5, 20))  # some already expired
    listings.append({
        "Food_ID": fid,
        "Food_Name": random.choice(FOOD_NAMES),
        "Quantity": random.randint(1, 50),
        "Expiry_Date": expiry.isoformat(),
        "Provider_ID": int(prov["Provider_ID"]),
        "Provider_Type": prov["Type"],
        "Location": prov["City"],  # food is where the provider is
        "Food_Type": random.choice(FOOD_TYPES),
        "Meal_Type": random.choice(MEAL_TYPES),
    })
food_df = pd.DataFrame(listings)

# ---------------------------------------------------------------- claims
N_CLAIMS = 500
claims = []
for cid in range(1, N_CLAIMS + 1):
    food = food_df.sample(1).iloc[0]
    rec = receivers_df.sample(1).iloc[0]
    ts = datetime.now() - timedelta(
        days=random.randint(0, 60),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )
    claims.append({
        "Claim_ID": cid,
        "Food_ID": int(food["Food_ID"]),
        "Receiver_ID": int(rec["Receiver_ID"]),
        "Status": random.choices(CLAIM_STATUS, weights=[0.55, 0.30, 0.15])[0],
        "Timestamp": ts.strftime("%Y-%m-%d %H:%M:%S"),
    })
claims_df = pd.DataFrame(claims)

# ---------------------------------------------------------------- save
providers_df.to_csv(os.path.join(DATA_DIR, "providers_data.csv"), index=False)
receivers_df.to_csv(os.path.join(DATA_DIR, "receivers_data.csv"), index=False)
food_df.to_csv(os.path.join(DATA_DIR, "food_listings_data.csv"), index=False)
claims_df.to_csv(os.path.join(DATA_DIR, "claims_data.csv"), index=False)

print("Sample data written to:", DATA_DIR)
print(f"  providers_data.csv      {len(providers_df):>4} rows")
print(f"  receivers_data.csv      {len(receivers_df):>4} rows")
print(f"  food_listings_data.csv  {len(food_df):>4} rows")
print(f"  claims_data.csv         {len(claims_df):>4} rows")
