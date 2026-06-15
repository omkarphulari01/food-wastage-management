"""
queries.py
----------
The 15 analysis queries from the project document, organised by section.
Each entry has a human-readable title and the SQL string. The Streamlit
app imports QUERIES and runs them; you can also run any of them directly
in a SQL client against food.db.
"""

QUERIES = {
    # ---------------------------------------------- Food Providers & Receivers
    "Q1. Providers & receivers per city": """
        SELECT city,
               provider_count,
               receiver_count
        FROM (
            SELECT City AS city, COUNT(*) AS provider_count FROM providers GROUP BY City
        ) p
        FULL OUTER JOIN (
            SELECT City AS city, COUNT(*) AS receiver_count FROM receivers GROUP BY City
        ) r USING (city)
        ORDER BY city;
    """,

    "Q2. Provider type contributing the most food": """
        SELECT Provider_Type,
               SUM(Quantity) AS total_quantity,
               COUNT(*)      AS listings
        FROM food_listings
        GROUP BY Provider_Type
        ORDER BY total_quantity DESC;
    """,

    "Q3. Contact info of providers in a specific city": """
        SELECT Name, Type, Address, Contact
        FROM providers
        WHERE City = :city
        ORDER BY Name;
    """,

    "Q4. Receivers who have claimed the most food": """
        SELECT r.Receiver_ID,
               r.Name,
               r.Type,
               r.City,
               COUNT(c.Claim_ID)                                  AS total_claims,
               SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS completed_claims
        FROM receivers r
        JOIN claims c ON c.Receiver_ID = r.Receiver_ID
        GROUP BY r.Receiver_ID, r.Name, r.Type, r.City
        ORDER BY total_claims DESC
        LIMIT 15;
    """,

    # ------------------------------------------------ Food Listings & Availability
    "Q5. Total quantity of food available": """
        SELECT SUM(Quantity) AS total_food_quantity_available
        FROM food_listings;
    """,

    "Q6. City with the highest number of food listings": """
        SELECT Location AS city,
               COUNT(*) AS listing_count
        FROM food_listings
        GROUP BY Location
        ORDER BY listing_count DESC;
    """,

    "Q7. Most commonly available food types": """
        SELECT Food_Type,
               COUNT(*)      AS listings,
               SUM(Quantity) AS total_quantity
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY listings DESC;
    """,

    # ----------------------------------------------------- Claims & Distribution
    "Q8. Claims made for each food item": """
        SELECT f.Food_ID,
               f.Food_Name,
               COUNT(c.Claim_ID) AS claim_count
        FROM food_listings f
        LEFT JOIN claims c ON c.Food_ID = f.Food_ID
        GROUP BY f.Food_ID, f.Food_Name
        ORDER BY claim_count DESC;
    """,

    "Q9. Provider with the most successful (completed) claims": """
        SELECT p.Provider_ID,
               p.Name,
               p.City,
               COUNT(*) AS completed_claims
        FROM claims c
        JOIN food_listings f ON f.Food_ID = c.Food_ID
        JOIN providers p     ON p.Provider_ID = f.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Provider_ID, p.Name, p.City
        ORDER BY completed_claims DESC
        LIMIT 15;
    """,

    "Q10. Claim status breakdown (completed / pending / cancelled)": """
        SELECT Status,
               COUNT(*) AS claim_count,
               ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM claims), 2) AS percentage
        FROM claims
        GROUP BY Status
        ORDER BY claim_count DESC;
    """,

    # ----------------------------------------------------- Analysis & Insights
    "Q11. Average quantity of food claimed per receiver": """
        SELECT ROUND(AVG(claimed_qty), 2) AS avg_quantity_per_receiver
        FROM (
            SELECT c.Receiver_ID,
                   SUM(f.Quantity) AS claimed_qty
            FROM claims c
            JOIN food_listings f ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY c.Receiver_ID
        );
    """,

    "Q12. Most claimed meal type": """
        SELECT f.Meal_Type,
               COUNT(c.Claim_ID) AS claim_count
        FROM claims c
        JOIN food_listings f ON f.Food_ID = c.Food_ID
        GROUP BY f.Meal_Type
        ORDER BY claim_count DESC;
    """,

    "Q13. Total quantity of food donated by each provider": """
        SELECT p.Provider_ID,
               p.Name,
               p.City,
               SUM(f.Quantity) AS total_donated
        FROM providers p
        JOIN food_listings f ON f.Provider_ID = p.Provider_ID
        GROUP BY p.Provider_ID, p.Name, p.City
        ORDER BY total_donated DESC
        LIMIT 15;
    """,

    # -------------------------------------------- Two extra queries (15+ total)
    "Q14. Listings expiring soon vs already expired": """
        SELECT CASE
                   WHEN DATE(Expiry_Date) <  DATE('now') THEN 'Expired'
                   WHEN DATE(Expiry_Date) <= DATE('now', '+3 day') THEN 'Expiring in 3 days'
                   ELSE 'Fresh'
               END AS expiry_status,
               COUNT(*)      AS listings,
               SUM(Quantity) AS total_quantity
        FROM food_listings
        GROUP BY expiry_status
        ORDER BY listings DESC;
    """,

    "Q15. Claim completion rate by city": """
        SELECT f.Location AS city,
               COUNT(*)                                                AS total_claims,
               SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END) AS completed,
               ROUND(100.0 * SUM(CASE WHEN c.Status = 'Completed' THEN 1 ELSE 0 END)
                     / COUNT(*), 2)                                     AS completion_rate_pct
        FROM claims c
        JOIN food_listings f ON f.Food_ID = c.Food_ID
        GROUP BY f.Location
        ORDER BY completion_rate_pct DESC;
    """,
}

# SQLite (used by the Streamlit app) does not support FULL OUTER JOIN in older
# versions. Q1 below is a SQLite-safe rewrite that the app uses instead.
QUERIES["Q1. Providers & receivers per city"] = """
    WITH cities AS (
        SELECT City FROM providers
        UNION
        SELECT City FROM receivers
    )
    SELECT ci.City AS city,
           COALESCE(p.provider_count, 0) AS provider_count,
           COALESCE(r.receiver_count, 0) AS receiver_count
    FROM cities ci
    LEFT JOIN (SELECT City, COUNT(*) AS provider_count FROM providers GROUP BY City) p
           ON p.City = ci.City
    LEFT JOIN (SELECT City, COUNT(*) AS receiver_count FROM receivers GROUP BY City) r
           ON r.City = ci.City
    ORDER BY ci.City;
"""
