import psycopg2

# Replace with your database connection details
DATABASE_URL = "postgresql://odds_db_p_pu99_user:hSooNc8dpZ3IeK97dBmRdeXj9zgK3lQI@dpg-cvor0bh5pdvs73a3p240-a.oregon-postgres.render.com/odds_db_p_pu99"

try:
    # Establish the connection
    conn = psycopg2.connect(DATABASE_URL)
    
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    
    # Query the count of rows in the odds table
    cursor.execute("SELECT COUNT(*) FROM odds;")
    
    # Fetch and print the result
    result = cursor.fetchone()
    print(f"Number of rows in the 'odds' table: {result[0]}")
    
except Exception as e:
    print("An error occurred:", e)
finally:
    # Close the cursor and connection
    cursor.close()
    conn.close()

