import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# Load datasets
sales_data1 = pd.read_csv("sales data1.csv")
sales_data2 = pd.read_csv("sales data2.csv")

# Merge datasets on 'Category' ensuring 'Date' from sales_data1 is retained
merged_data = pd.merge(
    sales_data1,
    sales_data2,
    on="Category",
    how="inner",
    suffixes=('_sales', '_marketing')
)

# Validate the presence of required columns
required_columns = ['Date_sales', 'TotalSales', 'Cost', 'QuantitySold']
missing_columns = [col for col in required_columns if col not in merged_data.columns]
if missing_columns:
    raise ValueError(f"Missing columns in the dataset: {', '.join(missing_columns)}")

# Yearly KPIs: Calculate Total Sales, ROMS, and AOV per Category
kpi_sales = merged_data.groupby('Category')['TotalSales'].sum().reset_index()

# Calculate ROMS per Category: Return on Marketing Spend
kpi_roms = merged_data.groupby('Category').apply(
    lambda x: x['TotalSales'].sum() / x['Cost'].sum()
).reset_index(name='ROMS')

# Calculate AOV per Category: Average Order Value
kpi_aov = merged_data.groupby('Category').apply(
    lambda x: x['TotalSales'].sum() / x['QuantitySold'].sum()
).reset_index(name='AOV')

# Sales Prediction per Category (using 'Date_sales' for year-based prediction)
def predict_sales(data):
    predictions = {}
    for category in data['Category'].unique():
        category_data = data[data['Category'] == category].copy()  # Use .copy() to avoid SettingWithCopyWarning
        
        # Ensure 'Date_sales' column is in datetime format for date-based calculations
        category_data['Date_sales'] = pd.to_datetime(category_data['Date_sales'])
        category_data['Year'] = category_data['Date_sales'].dt.year
        
        yearly_sales = category_data.groupby('Year')['TotalSales'].sum().reset_index()
        X = yearly_sales['Year'].values.reshape(-1, 1)
        y = yearly_sales['TotalSales'].values
        
        if len(X) > 1:
            model = LinearRegression()
            model.fit(X, y)
            next_year = np.array([[X[-1][0] + 1]])  # Predict for the next year
            predictions[category] = model.predict(next_year)[0]
        else:
            predictions[category] = "Insufficient data"
    return predictions

# Predict sales for each category
sales_predictions = predict_sales(merged_data)

# Visualization functions
def plot_bar(data, x, y, title, ylabel, filename):
    plt.figure(figsize=(10, 6))
    plt.bar(data[x], data[y], color='skyblue')
    plt.title(title)
    plt.ylabel(ylabel)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Plot KPIs
plot_bar(kpi_sales, 'Category', 'TotalSales', "Total Sales per Category", "Sales", "total_sales.png")
plot_bar(kpi_roms, 'Category', 'ROMS', "Return on Marketing Spend per Category", "ROMS", "roms.png")
plot_bar(kpi_aov, 'Category', 'AOV', "Average Order Value per Category", "AOV", "aov.png")

# Generate HTML Report
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KPI Dashboard Report</title>
    <style>
        body { font-family: Arial, sans-serif; }
        h1 { text-align: center; }
        .chart { text-align: center; margin-bottom: 30px; }
        .predictions { color: green; font-weight: bold; }
        table { width: 100%; border-collapse: collapse; margin-bottom: 30px; }
        table, th, td { border: 1px solid black; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>KPI Dashboard Report</h1>

    <h2>Total Sales per Category</h2>
    <div class="chart">
        <img src="total_sales.png" alt="Total Sales per Category">
    </div>

    <h2>Return on Marketing Spend per Category</h2>
    <div class="chart">
        <img src="roms.png" alt="Return on Marketing Spend per Category">
    </div>

    <h2>Average Order Value per Category</h2>
    <div class="chart">
        <img src="aov.png" alt="Average Order Value per Category">
    </div>

    <h2>Sales Predictions per Category</h2>
    <div>
        <table>
            <tr>
                <th>Category</th>
                <th>Predicted Sales for Next Year</th>
            </tr>
"""

# Add predicted sales data
for category, prediction in sales_predictions.items():
    html_content += f"""
    <tr>
        <td>{category}</td>
        <td class="predictions">{prediction}</td>
    </tr>
    """

html_content += """
        </table>
    </div>
</body>
</html>
"""

# Save the HTML file
output_file = "kpi_dashboard.html"
with open(output_file, "w") as file:
    file.write(html_content)

print(f"HTML report generated: {output_file}")

"""
# Automation Instructions
def setup_cron():
    print("To schedule this script using cron:")
    print("1. Open terminal and type `crontab -e`.")
    print(f"2. Add the line: `0 0 * * * python3 {os.path.abspath('kpi_dashboard.py')}` to run daily at midnight.")
    print("3. Save and exit.")

setup_cron()"""
