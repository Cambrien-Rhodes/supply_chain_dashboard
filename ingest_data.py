import sqlite3
import csv

connection = sqlite3.connect('supply_chain.db')
cursor = connection.cursor()



cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        sku TEXT PRIMARY KEY,
        description TEXT,
        category TEXT,
        unit_price REAL
    );

""")

cursor.execute(""" 
    CREATE TABLE IF NOT EXISTS inventory_status(
      sku TEXT PRIMARY KEY,
      quantity_on_hand INTEGER,
      reorder_point INTEGER);
""")

with open('data/erp_export.csv', mode='r', encoding ='utf-8-sig') as file:

    reader = csv.DictReader(file, delimiter ="\t")


    print('Processing into relational tables.....')



    for row in reader:
     



        clean_row = {key.strip(): value.strip() for key, value in row.items() if key}


        if not clean_row.get("sku"):
       
            continue

        sku = clean_row["sku"]
        description = clean_row["description"]
        category = clean_row["category"]
        unit_price = clean_row["unit_price"]
        quantity_on_hand = clean_row["quantity_on_hand"]
        reorder_point = clean_row["reorder_point"]

        cursor.execute("""
            INSERT OR IGNORE INTO products 
            (sku, description, category, unit_price)
            VALUES (?, ?, ?, ?);""", 
            (sku, description, category, unit_price))
        
        cursor.execute("""
            INSERT OR IGNORE INTO inventory_status 
            (sku, quantity_on_hand, reorder_point)
            VALUES (?, ?, ?); """, 
            (sku, quantity_on_hand, reorder_point))



connection.commit()

print('Data ingestion complete')

connection.close()