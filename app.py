"""
app.py — Local Food Wastage Management System
=============================================
A Streamlit interface over the SQLite database (food.db) that provides:

  • Dashboard      – key metrics at a glance
  • Browse Data    – view the four raw tables
  • Filter & Contact – filter listings by city / provider / food type / meal
                       type and pull provider & receiver contact details
  • CRUD           – add, update, delete food listings
  • SQL Queries    – all 15 analysis queries with their outputs
  • EDA & Insights – charts on wastage / claim / provider trends

Run:
    streamlit run app.py
(make sure database_setup.py has been run first so food.db exists)
"""

import os
import sqlite3
from datetime import date, datetime

import pandas as pd
import streamlit as st

from queries import QUERIES

try:
    import charts
    HAS_PLOTLY = charts.HAS_PLOTLY
except Exception:
    HAS_PLOTLY = False

DB_PATH = os.path.join(os.path.dirname(__file__), "food.db")

st.set_page_config(
    page_title="Local Food Wastage Management System",
    page_icon="🍲",
    layout="wide",
)

# --------------------------------------------------------------- global styling
st.markdown(
    """
    <style>
      .block-container { padding-top: 2.2rem; padding-bottom: 3rem; }
      h1, h2, h3 { color: #0F172A; font-weight: 700; }

      /* hero header */
      .hero {
        background: linear-gradient(110deg, #065F46 0%, #10B981 55%, #34D399 100%);
        border-radius: 18px; padding: 26px 30px; margin-bottom: 22px;
        color: #ECFDF5; box-shadow: 0 10px 30px rgba(16,185,129,0.25);
      }
      .hero h1 { color: #FFFFFF; margin: 0; font-size: 1.9rem; }
      .hero p  { color: #D1FAE5; margin: 6px 0 0; font-size: 0.98rem; }

      /* KPI cards */
      .kpi {
        background: #FFFFFF; border: 1px solid #E5E9F0; border-radius: 16px;
        padding: 18px 18px 16px; box-shadow: 0 4px 14px rgba(15,23,42,0.05);
        height: 100%;
      }
      .kpi .lab { color: #64748B; font-size: 0.82rem; font-weight: 600;
                  text-transform: uppercase; letter-spacing: .04em; }
      .kpi .val { color: #0F172A; font-size: 1.7rem; font-weight: 800; margin-top: 4px; }
      .kpi .ico { width: 40px; height: 40px; border-radius: 11px; display: flex;
                  align-items: center; justify-content: center; font-size: 20px;
                  margin-bottom: 10px; }

      /* section divider tweak */
      hr { margin: 1.4rem 0; }

      /* dataframe corners */
      [data-testid="stDataFrame"] { border-radius: 12px; overflow: hidden; }

      /* sidebar */
      section[data-testid="stSidebar"] { background: #0F172A; }
      section[data-testid="stSidebar"] * { color: #E2E8F0 !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


def kpi_card(col, label, value, icon, color):
    col.markdown(
        f"""
        <div class="kpi" style="border-top:4px solid {color}">
          <div class="ico" style="background:{color}1A;color:{color}">{icon}</div>
          <div class="lab">{label}</div>
          <div class="val">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ---- safe chart wrappers (fall back to native charts if Plotly unavailable) ----
_PCFG = {"displayModeBar": False}


def viz_bar(series, title, **kw):
    if HAS_PLOTLY:
        try:
            st.plotly_chart(charts.bar(series, title, **kw), width="stretch", config=_PCFG)
            return
        except Exception:
            pass
    st.caption(title)
    st.bar_chart(series)


def viz_donut(series, title, color_map=None, height=360):
    if HAS_PLOTLY:
        try:
            st.plotly_chart(charts.donut(series, title, color_map=color_map, height=height),
                            width="stretch", config=_PCFG)
            return
        except Exception:
            pass
    st.caption(title)
    st.bar_chart(series)


def viz_grouped(pivot, title, **kw):
    if HAS_PLOTLY:
        try:
            st.plotly_chart(charts.grouped_bar(pivot, title, **kw), width="stretch", config=_PCFG)
            return
        except Exception:
            pass
    st.caption(title)
    st.bar_chart(pivot)


def viz_area(series, title, color="#3B82F6", height=340):
    if HAS_PLOTLY:
        try:
            st.plotly_chart(charts.area(series, title, color=color, height=height),
                            width="stretch", config=_PCFG)
            return
        except Exception:
            pass
    st.caption(title)
    st.line_chart(series)


# --------------------------------------------------------------------------- db
def get_conn():
    """One connection per session, reused across reruns."""
    if "conn" not in st.session_state:
        if not os.path.exists(DB_PATH):
            # On a fresh deploy (e.g. Streamlit Cloud) food.db won't exist yet,
            # so build it from the CSVs in ./data automatically.
            try:
                import database_setup
                with st.spinner("Setting up the database for the first time..."):
                    database_setup.build()
            except Exception as e:
                st.error(
                    "Could not build the database. Make sure the four CSV files "
                    f"are in the ./data folder. Details: {e}"
                )
                st.stop()
        st.session_state.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return st.session_state.conn


def run_query(sql, params=None):
    return pd.read_sql_query(sql, get_conn(), params=params or {})


def execute(sql, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params or {})
    conn.commit()
    return cur


def table(name):
    return run_query(f"SELECT * FROM {name}")


def distinct(col, tbl):
    df = run_query(f"SELECT DISTINCT {col} AS v FROM {tbl} WHERE {col} IS NOT NULL ORDER BY {col}")
    return df["v"].tolist()


# ------------------------------------------------------------------------ pages
def page_dashboard():
    st.markdown(
        """
        <div class="hero">
          <h1>🍲 Local Food Wastage Management System</h1>
          <p>Connecting surplus food providers with the people and organisations who need it.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    providers = table("providers")
    receivers = table("receivers")
    food = table("food_listings")
    claims = table("claims")

    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card(c1, "Providers", f"{len(providers):,}", "🏪", "#10B981")
    kpi_card(c2, "Receivers", f"{len(receivers):,}", "🤝", "#3B82F6")
    kpi_card(c3, "Food Listings", f"{len(food):,}", "🍱", "#F59E0B")
    kpi_card(c4, "Total Quantity", f"{int(food['Quantity'].sum()) if len(food) else 0:,}", "📦", "#8B5CF6")
    kpi_card(c5, "Claims", f"{len(claims):,}", "📋", "#EC4899")

    st.write("")
    st.divider()
    left, right = st.columns(2)
    with left:
        viz_donut(claims["Status"].value_counts(), "Claims by Status",
                  color_map=charts.STATUS_COLORS if HAS_PLOTLY else None)
    with right:
        viz_donut(food["Food_Type"].value_counts(), "Listings by Food Type",
                  color_map=charts.FOOD_COLORS if HAS_PLOTLY else None)

    viz_bar(food["Location"].value_counts().head(10), "Top 10 Cities by Food Listings",
            y_title="Listings")


def page_browse():
    st.title("Browse Data")
    name = st.selectbox(
        "Table",
        ["providers", "receivers", "food_listings", "claims"],
    )
    df = table(name)
    st.write(f"{len(df)} rows")
    st.dataframe(df, width="stretch", hide_index=True)
    st.download_button(
        "Download as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=f"{name}.csv",
        mime="text/csv",
    )


def page_filter():
    st.title("Filter Listings & Find Contacts")

    cities = ["(All)"] + distinct("Location", "food_listings")
    providers = ["(All)"] + distinct("Name", "providers")
    food_types = ["(All)"] + distinct("Food_Type", "food_listings")
    meal_types = ["(All)"] + distinct("Meal_Type", "food_listings")

    c1, c2, c3, c4 = st.columns(4)
    city = c1.selectbox("City", cities)
    provider = c2.selectbox("Provider", providers)
    food_type = c3.selectbox("Food Type", food_types)
    meal_type = c4.selectbox("Meal Type", meal_types)

    sql = """
        SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date,
               p.Name AS Provider, f.Provider_Type, f.Location,
               f.Food_Type, f.Meal_Type, p.Contact AS Provider_Contact
        FROM food_listings f
        JOIN providers p ON p.Provider_ID = f.Provider_ID
        WHERE 1 = 1
    """
    params = {}
    if city != "(All)":
        sql += " AND f.Location = :city";          params["city"] = city
    if provider != "(All)":
        sql += " AND p.Name = :provider";          params["provider"] = provider
    if food_type != "(All)":
        sql += " AND f.Food_Type = :food_type";    params["food_type"] = food_type
    if meal_type != "(All)":
        sql += " AND f.Meal_Type = :meal_type";    params["meal_type"] = meal_type
    sql += " ORDER BY f.Expiry_Date"

    df = run_query(sql, params)
    st.write(f"{len(df)} matching listings")
    st.dataframe(df, width="stretch", hide_index=True)

    st.divider()
    st.subheader("📞 Contact directory")
    tab1, tab2 = st.tabs(["Providers", "Receivers"])
    with tab1:
        pc = st.selectbox("Provider city", ["(All)"] + distinct("City", "providers"), key="pc")
        q = "SELECT Name, Type, Address, City, Contact FROM providers"
        prm = {}
        if pc := (pc if pc != "(All)" else None):
            q += " WHERE City = :c"; prm["c"] = pc
        st.dataframe(run_query(q + " ORDER BY Name", prm), width="stretch", hide_index=True)
    with tab2:
        rc = st.selectbox("Receiver city", ["(All)"] + distinct("City", "receivers"), key="rc")
        q = "SELECT Name, Type, City, Contact FROM receivers"
        prm = {}
        if rc != "(All)":
            q += " WHERE City = :c"; prm["c"] = rc
        st.dataframe(run_query(q + " ORDER BY Name", prm), width="stretch", hide_index=True)


def page_crud():
    st.title("Manage Food Listings (CRUD)")
    st.caption("Add, update, or remove food listing records.")

    action = st.radio("Action", ["Add", "Update", "Delete"], horizontal=True)
    provider_ids = run_query("SELECT Provider_ID, Name FROM providers ORDER BY Provider_ID")
    pid_options = provider_ids["Provider_ID"].tolist()
    food_types = distinct("Food_Type", "food_listings") or ["Vegetarian", "Non-Vegetarian", "Vegan"]
    meal_types = distinct("Meal_Type", "food_listings") or ["Breakfast", "Lunch", "Dinner", "Snacks"]

    # ----------------------------------------------------------------- CREATE
    if action == "Add":
        with st.form("add_form"):
            name = st.text_input("Food Name")
            qty = st.number_input("Quantity", min_value=1, value=1, step=1)
            expiry = st.date_input("Expiry Date", value=date.today())
            pid = st.selectbox("Provider", pid_options,
                               format_func=lambda i: f"{i} – {provider_ids.set_index('Provider_ID').loc[i,'Name']}")
            ftype = st.selectbox("Food Type", food_types)
            mtype = st.selectbox("Meal Type", meal_types)
            submitted = st.form_submit_button("Add listing")
        if submitted:
            prov = run_query("SELECT Type, City FROM providers WHERE Provider_ID = :p", {"p": int(pid)}).iloc[0]
            new_id = (run_query("SELECT COALESCE(MAX(Food_ID),0)+1 AS n FROM food_listings")["n"][0])
            execute(
                """INSERT INTO food_listings
                   (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID,
                    Provider_Type, Location, Food_Type, Meal_Type)
                   VALUES (:id,:name,:qty,:exp,:pid,:ptype,:loc,:ftype,:mtype)""",
                {"id": int(new_id), "name": name, "qty": int(qty),
                 "exp": expiry.isoformat(), "pid": int(pid),
                 "ptype": prov["Type"], "loc": prov["City"],
                 "ftype": ftype, "mtype": mtype},
            )
            st.success(f"Added listing #{int(new_id)} – {name}")

    # ----------------------------------------------------------------- UPDATE
    elif action == "Update":
        ids = run_query("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID")
        if ids.empty:
            st.info("No listings to update.")
            return
        fid = st.selectbox("Listing to edit", ids["Food_ID"].tolist(),
                           format_func=lambda i: f"{i} – {ids.set_index('Food_ID').loc[i,'Food_Name']}")
        row = run_query("SELECT * FROM food_listings WHERE Food_ID = :f", {"f": int(fid)}).iloc[0]
        with st.form("edit_form"):
            name = st.text_input("Food Name", row["Food_Name"])
            qty = st.number_input("Quantity", min_value=0, value=int(row["Quantity"]), step=1)
            try:
                cur_exp = datetime.fromisoformat(str(row["Expiry_Date"])).date()
            except ValueError:
                cur_exp = date.today()
            expiry = st.date_input("Expiry Date", value=cur_exp)
            ftype = st.selectbox("Food Type", food_types,
                                 index=food_types.index(row["Food_Type"]) if row["Food_Type"] in food_types else 0)
            mtype = st.selectbox("Meal Type", meal_types,
                                 index=meal_types.index(row["Meal_Type"]) if row["Meal_Type"] in meal_types else 0)
            submitted = st.form_submit_button("Save changes")
        if submitted:
            execute(
                """UPDATE food_listings
                   SET Food_Name=:name, Quantity=:qty, Expiry_Date=:exp,
                       Food_Type=:ftype, Meal_Type=:mtype
                   WHERE Food_ID=:f""",
                {"name": name, "qty": int(qty), "exp": expiry.isoformat(),
                 "ftype": ftype, "mtype": mtype, "f": int(fid)},
            )
            st.success(f"Updated listing #{int(fid)}")

    # ----------------------------------------------------------------- DELETE
    else:
        ids = run_query("SELECT Food_ID, Food_Name FROM food_listings ORDER BY Food_ID")
        if ids.empty:
            st.info("No listings to delete.")
            return
        fid = st.selectbox("Listing to delete", ids["Food_ID"].tolist(),
                           format_func=lambda i: f"{i} – {ids.set_index('Food_ID').loc[i,'Food_Name']}")
        st.warning("This also removes any claims that reference the listing.")
        if st.button("Delete listing", type="primary"):
            execute("DELETE FROM claims WHERE Food_ID = :f", {"f": int(fid)})
            execute("DELETE FROM food_listings WHERE Food_ID = :f", {"f": int(fid)})
            st.success(f"Deleted listing #{int(fid)}")


def page_queries():
    st.title("SQL Queries & Analysis")
    st.caption("All 15 analysis questions from the project brief, answered live from the database.")

    names = list(QUERIES.keys())
    choice = st.selectbox("Choose a query", ["(Run all)"] + names)

    def render(name):
        sql = QUERIES[name]
        st.markdown(f"#### {name}")
        params = {}
        if ":city" in sql:
            city = st.selectbox("City", distinct("City", "providers"), key=f"city_{name}")
            params["city"] = city
        df = run_query(sql, params)
        st.dataframe(df, width="stretch", hide_index=True)
        # auto-chart when it makes sense
        if df.shape[1] == 2 and pd.api.types.is_numeric_dtype(df.iloc[:, 1]):
            s = df.set_index(df.columns[0]).iloc[:, 0]
            viz_bar(s.head(15), "", y_title=str(df.columns[1]))
        with st.expander("Show SQL"):
            st.code(sql.strip(), language="sql")
        st.divider()

    if choice == "(Run all)":
        for n in names:
            render(n)
    else:
        render(choice)


def page_nulls():
    st.title("Null Value Analysis")
    st.caption("Missing values per table, with likely reasons (per the project brief).")

    reasons = {
        ("providers", "Contact"): "Provider forgot to enter contact details.",
        ("providers", "Address"): "Provider forgot to enter the address.",
        ("receivers", "Contact"): "Receiver may not want to share contact.",
        ("food_listings", "Expiry_Date"): "Food information not entered properly.",
        ("food_listings", "Quantity"): "Food information not entered properly.",
        ("claims", "Status"): "Claim process incomplete.",
        ("claims", "Timestamp"): "Claim process incomplete.",
    }

    for tname in ["providers", "receivers", "food_listings", "claims"]:
        df = table(tname)
        # treat empty strings / 'nan' / 'None' as missing too
        norm = df.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "NaN": pd.NA})
        nulls = norm.isna().sum()
        report = pd.DataFrame({
            "Column": nulls.index,
            "Missing": nulls.values,
            "Missing %": (nulls.values / max(len(df), 1) * 100).round(2),
        })
        report["Likely Reason"] = report["Column"].apply(
            lambda c: reasons.get((tname, c), "—")
        )
        st.subheader(f"{tname}  ({len(df)} rows)")
        if report["Missing"].sum() == 0:
            st.success("No missing values in this table.")
        st.dataframe(report, width="stretch", hide_index=True)
        st.divider()


def page_eda():
    st.title("EDA — Exploratory Data Analysis")
    st.caption("15 visualizations grouped as univariate, bivariate, multivariate, and claim analysis.")

    providers = table("providers")
    receivers = table("receivers")
    food = table("food_listings")
    claims = table("claims")

    # listing + provider + receiver context for the multivariate / claim charts
    cf = claims.merge(food, on="Food_ID", how="left")
    cf = cf.merge(providers[["Provider_ID", "Name"]], on="Provider_ID", how="left")
    cf = cf.merge(
        receivers[["Receiver_ID", "Name"]].rename(columns={"Name": "Receiver_Name"}),
        on="Receiver_ID", how="left",
    )

    # ---------------------------------------------------------- Univariate (1-4)
    st.header("Univariate")
    c1, c2 = st.columns(2)
    with c1:
        viz_donut(providers["Type"].value_counts(), "1. Provider Type Distribution")
    with c2:
        viz_donut(receivers["Type"].value_counts(), "2. Receiver Type Distribution")
    c3, c4 = st.columns(2)
    with c3:
        viz_donut(food["Food_Type"].value_counts(), "3. Food Type Distribution",
                  color_map=charts.FOOD_COLORS if HAS_PLOTLY else None)
    with c4:
        viz_donut(food["Meal_Type"].value_counts(), "4. Meal Type Distribution",
                  color_map=charts.MEAL_COLORS if HAS_PLOTLY else None)

    # ---------------------------------------------------------- Bivariate (5-8)
    st.header("Bivariate")
    viz_bar(food["Location"].value_counts().head(15), "5. City vs Food Listings (Top 15)",
            y_title="Listings")
    viz_bar(food.groupby("Provider_Type")["Quantity"].sum(), "6. Provider Type vs Quantity",
            y_title="Quantity")
    c5, c6 = st.columns(2)
    with c5:
        viz_bar(food.groupby("Food_Type")["Quantity"].sum(), "7. Food Type vs Quantity",
                color_map=charts.FOOD_COLORS if HAS_PLOTLY else None, y_title="Quantity")
    with c6:
        viz_bar(food.groupby("Meal_Type")["Quantity"].sum(), "8. Meal Type vs Quantity",
                color_map=charts.MEAL_COLORS if HAS_PLOTLY else None, y_title="Quantity")

    # -------------------------------------------------------- Multivariate (9-12)
    st.header("Multivariate")
    top_cities = food["Location"].value_counts().head(10).index
    pivot = (food[food["Location"].isin(top_cities)]
             .pivot_table(index="Location", columns="Provider_Type",
                          values="Quantity", aggfunc="sum", fill_value=0))
    viz_grouped(pivot, "9. City + Provider Type + Quantity (Top 10 Cities)", y_title="Quantity")

    pivot2 = food.pivot_table(index="Meal_Type", columns="Food_Type",
                              values="Quantity", aggfunc="sum", fill_value=0)
    viz_grouped(pivot2, "10. Food Type + Meal Type + Quantity", y_title="Quantity")

    prov_claims = (cf.groupby("Name")
                   .agg(Claims=("Claim_ID", "count"), Quantity=("Quantity", "sum"))
                   .sort_values("Claims", ascending=False).head(10))
    viz_grouped(prov_claims, "11. Provider + Claims + Quantity (Top 10 Providers)")

    rec_claims = (cf.groupby("Receiver_Name")
                  .agg(Claims=("Claim_ID", "count"), Quantity=("Quantity", "sum"))
                  .sort_values("Claims", ascending=False).head(10))
    viz_grouped(rec_claims, "12. Receiver + Claims + Quantity (Top 10 Receivers)")

    # ------------------------------------------------------ Claim Analysis (13-15)
    st.header("Claim Analysis")
    viz_donut(claims["Status"].value_counts(), "13. Claim Status Distribution",
              color_map=charts.STATUS_COLORS if HAS_PLOTLY else None)
    c7, c8 = st.columns(2)
    with c7:
        viz_bar(cf["Receiver_Name"].value_counts().head(10), "14. Top 10 Receivers",
                horizontal=True, height=420)
    with c8:
        viz_bar(cf["Name"].value_counts().head(10), "15. Top 10 Providers",
                horizontal=True, height=420)


def page_insights():
    st.title("Business Insights & Recommendations")

    food = table("food_listings")
    claims = table("claims")
    providers = table("providers")
    receivers = table("receivers")
    cf = claims.merge(food, on="Food_ID", how="left")

    st.header("Key Insights")

    # Food availability
    top_city_food = food["Location"].value_counts().idxmax()
    top_city_food_n = int(food["Location"].value_counts().max())
    # Food waste (most wasted meal = most cancelled claims by meal)
    cancelled = cf[cf["Status"] == "Cancelled"]
    most_wasted_meal = (cancelled["Meal_Type"].value_counts().idxmax()
                        if not cancelled.empty else "N/A")
    # Top provider by donated quantity
    prov_donation = (food.merge(providers[["Provider_ID", "Name"]], on="Provider_ID", how="left")
                     .groupby("Name")["Quantity"].sum().sort_values(ascending=False))
    top_provider = prov_donation.idxmax()
    # Top receiver by claims
    rec_claims = (claims.merge(receivers[["Receiver_ID", "Name"]], on="Receiver_ID", how="left")
                  ["Name"].value_counts())
    top_receiver = rec_claims.idxmax()
    # Claim completion %
    completed_pct = round(100 * (claims["Status"] == "Completed").mean(), 1)
    # Highest demand city (most claims)
    demand_city = cf["Location"].value_counts().idxmax()

    rows = [
        ("🏙️ Food Availability", f"**{top_city_food}** has the most food listings ({top_city_food_n})."),
        ("🗑️ Food Waste", f"**{most_wasted_meal}** is the most cancelled (wasted) meal type."),
        ("🏪 Provider Analysis", f"**{top_provider}** contributes the most food overall."),
        ("🤝 Receiver Analysis", f"**{top_receiver}** claims the most food."),
        ("✅ Claims Analysis", f"**{completed_pct}%** of all claims are completed."),
        ("📈 Demand Analysis", f"**{demand_city}** has the highest food demand (most claims)."),
    ]
    cols = st.columns(2)
    accent = ["#10B981", "#EF4444", "#3B82F6", "#8B5CF6", "#F59E0B", "#EC4899"]
    for i, (label, text) in enumerate(rows):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="kpi" style="border-left:5px solid {accent[i]};
                     border-top:none; margin-bottom:14px">
                  <div class="lab" style="color:{accent[i]}">{label}</div>
                  <div style="color:#0F172A;font-size:0.98rem;margin-top:6px">{text}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("Supporting charts")
    cc1, cc2 = st.columns(2)
    with cc1:
        viz_donut(claims["Status"].value_counts(), "Claim Status Split",
                  color_map=charts.STATUS_COLORS if HAS_PLOTLY else None)
    with cc2:
        viz_bar(cf["Location"].value_counts().head(10), "Top 10 Cities by Demand (Claims)",
                horizontal=True, height=400)

    st.divider()
    st.header("Recommendations")
    st.markdown(
        f"""
1. **More NGO partnerships in high-wastage cities** — cities with high cancellation/expiry
   (such as **{demand_city}**) should be prioritised for new NGO tie-ups.
2. **Recognise top providers** — reward providers like **{top_provider}** to encourage
   continued and increased donations.
3. **Automated expiry notifications** — alert providers and nearby receivers before food
   expires, so the **{most_wasted_meal}** wastage seen above is reduced.
4. **Boost collection in high-demand cities** — increase pickup/logistics capacity in
   **{demand_city}** to meet the highest demand.
"""
    )


# ------------------------------------------------------------------------- main
PAGES = {
    "Dashboard": page_dashboard,
    "Browse Data": page_browse,
    "Null Value Analysis": page_nulls,
    "Filter & Contact": page_filter,
    "Manage Listings (CRUD)": page_crud,
    "SQL Queries": page_queries,
    "EDA": page_eda,
    "Insights & Recommendations": page_insights,
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
st.sidebar.divider()
st.sidebar.caption("Local Food Wastage Management System\nPython · SQL · Streamlit")

PAGES[selection]()
