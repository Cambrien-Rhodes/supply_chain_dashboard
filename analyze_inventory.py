import sqlite3
import pandas as pd

connection = sqlite3.connect('supply_chain.db')

query = """
    SELECT
        p.sku, 
        p.description,
        p.category,
        p.unit_price,
        i.quantity_on_hand,
        i.reorder_point
    FROM products p
    INNER JOIN inventory_status i ON p.sku = i.sku;

"""



df = pd.read_sql_query(query, connection)

df['total_capital'] = df['quantity_on_hand'] * df['unit_price']

df['stock_deficit'] = df['reorder_point'] - df['quantity_on_hand']

df['reorder_cost'] = df['stock_deficit'].apply(lambda x: x if x > 0 else 0) * df['unit_price']

total_inventory_value = df['total_capital'].sum()

critical_items_df = df[df['quantity_on_hand']< df['reorder_point']]
total_critical_items = len(critical_items_df)
total_reorder_investment = critical_items_df['reorder_cost'].sum()


category_summary = df.groupby('category').agg(
   total_skus = ('sku', 'count'),
   category_value = ('total_capital', 'sum'),
   critical_skus=('quantity_on_hand', lambda x: (x < df.loc[x.index, 'reorder_point']).sum())
).reset_index()


print("=" * 60)
print("     STRATION SOLUTIONS — SUPPLY CHAIN ANALYTICS REPORT     ")
print("=" * 60)
print(f"Total Working Capital Bound: ${total_inventory_value:,.2f}")
print(f"Critical Stockout Alerts    : {total_critical_items} SKUs requiring reorder")
print(f"Capital Required to Replenish: ${total_reorder_investment:,.2f}")
print("-" * 60)

print("\n>> CAPITAL DISTRIBUTION BY CATEGORY:")
print(category_summary.to_string(index=False))

print("\n>> TOP 5 CRITICAL STOCKOUT EXCEPTIONS (ACTION REQUIRED TODAY):")
# Sort by highest reorder cost urgency
top_critical = critical_items_df.sort_values(by='reorder_cost', ascending=False).head(5)
print(top_critical[['sku', 'description', 'category', 'quantity_on_hand', 'reorder_point', 'reorder_cost']].to_string(index=False))
print("=" * 60)
                       


connection.close()

print(df.head())