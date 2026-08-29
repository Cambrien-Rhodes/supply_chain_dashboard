import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


connection = sqlite3.connect('supply_chain.db')

query = """
    SELECT p.sku, p.description, p.category, p.unit_price, i.quantity_on_hand, i.reorder_point
    FROM products p
    INNER JOIN inventory_status i ON p.sku = i.sku;
"""

df = pd.read_sql_query(query, connection)
connection.close()

df['total_capital'] = df['quantity_on_hand'] * df['unit_price']
df['stock_deficit'] = df['reorder_point'] - df['quantity_on_hand']
df['reorder_cost'] = df['stock_deficit'].apply(lambda x: x if x > 0 else 0) * df['unit_price']

critical_df = df[df['quantity_on_hand'] < df['reorder_point']].copy()
category_cap = df.groupby('category')['total_capital'].sum().reset_index()
top5_reorder = critical_df.sort_values(by='reorder_cost', ascending=False).head(5)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('SUPPLY CHAIN EXECUTIVE DASHBOARD', fontsize=16, fontweight='bold', y=0.98)


axes[0, 0].barh(category_cap['category'], category_cap['total_capital'], color='#2b5c8f')
axes[0, 0].set_title('Tied-Up Working Capital ($)', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('Total Dollars ($)')

# --- PANEL 2: Inventory Health Ratio (Top Right) ---
healthy_count = len(df) - len(critical_df)
critical_count = len(critical_df)
axes[0, 1].pie(
    [healthy_count, critical_count], 
    labels=['Healthy Stock', 'Critical Reorder'], 
    colors=['#2ea44f', '#cb2431'], 
    autopct='%1.1f%%', 
    startangle=140,
    explode=(0, 0.1) # Pull out the critical slice for visual impact
)
axes[0, 1].set_title('Inventory Health Breakdown', fontsize=12, fontweight='bold')

# --- PANEL 3: Top 5 Highest Dollar Reorders (Bottom Left) ---
axes[1, 0].bar(top5_reorder['sku'], top5_reorder['reorder_cost'], color='#d93f0b')
axes[1, 0].set_title('Top 5 Urgent Reorder Expenses ($)', fontsize=12, fontweight='bold')
axes[1, 0].set_ylabel('Required Capital ($)')
axes[1, 0].tick_params(axis='x', rotation=30)

# --- PANEL 4: Executive Summary KPI Card (Bottom Right) ---
axes[1, 1].axis('off') # Hide graph axes to turn this panel into a text card
summary_text = (
    f"EXECUTIVE SUMMARY METRICS\n"
    f"────────────────────────────\n\n"
    f"• Total SKUs Monitored   : {len(df):,}\n"
    f"• Total Capital Invested : ${df['total_capital'].sum():,.2f}\n"
    f"• Critical Stockout SKUs : {critical_count} items\n"
    f"• Replenishment Cost    : ${critical_df['reorder_cost'].sum():,.2f}\n\n"
    f"STATUS: Action Required for {critical_count} SKUs."
)
axes[1, 1].text(0.1, 0.3, summary_text, fontsize=12, family='monospace', verticalalignment='center')

# 4. Final Polish & Save
plt.tight_layout(rect=[0, 0, 1, 0.95]) # Adjust subplots to fit master title cleanly
plt.savefig('supply_chain_dashboard.png', dpi=300) # Save high-res image
print("[SUCCESS] Dashboard generated and saved as 'supply_chain_dashboard.png'.")