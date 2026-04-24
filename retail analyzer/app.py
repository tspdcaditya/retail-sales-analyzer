import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Button, Label, filedialog, messagebox
import os

df = None
monthly = None
cat = None
all_products = None
top5 = None
sales_col = None
date_col = None
category_col = None
product_col = None


def detect_column(df, keywords):
    """Automatically detect column based on keywords"""
    for col in df.columns:
        for key in keywords:
            if key in col.lower():
                return col
    return None


def run_analysis():
    global df, monthly, cat, all_products, top5
    global sales_col, date_col, category_col, product_col

    file_path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    )

    if not file_path:
        return

    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        messagebox.showerror("Error", f"File could not be read:\n{e}")
        return

    df.columns = df.columns.str.strip()

    # Auto detect columns
    sales_col = detect_column(df, ["sale", "revenue", "amount", "price", "total"])
    date_col = detect_column(df, ["date", "month", "time"])
    category_col = detect_column(df, ["category", "segment", "type"])
    product_col = detect_column(df, ["product", "item", "name"])

    if not all([sales_col, date_col, category_col, product_col]):
        messagebox.showerror(
            "Error",
            "Could not detect required columns.\n"
            "Dataset must contain Sales, Date, Category, and Product columns."
        )
        return

    try:
        df[sales_col] = pd.to_numeric(df[sales_col], errors="coerce")
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    except:
        messagebox.showerror("Error", "Error converting sales/date column.")
        return

    df = df.dropna(subset=[sales_col, date_col, category_col, product_col])

    if df.empty:
        messagebox.showerror("Error", "No valid data found after cleaning.")
        return

       # Grouping
    monthly = df.groupby(df[date_col].dt.to_period("M"))[sales_col].sum()
    cat = df.groupby(category_col)[sales_col].sum().sort_values(ascending=False)
    all_products = df.groupby(product_col)[sales_col].sum().sort_values(ascending=False)
    top5 = all_products.head(5)

    # If too many products, show top 15 only
    if len(all_products) > 15:
        display_products = all_products.head(15)
    else:
        display_products = all_products

    plt.style.use("seaborn-v0_8-whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle("Retail Sales Dashboard", fontsize=18, fontweight="bold")

    # 1️⃣ Sales Over Time
    axes[0, 0].plot(monthly.index.to_timestamp(), monthly.values, marker="o")
    axes[0, 0].set_title("Sales Over Time")
    axes[0, 0].tick_params(axis='x', rotation=45)

    # 2️⃣ Category Wise Sales (Horizontal)
    axes[0, 1].barh(cat.index, cat.values)
    axes[0, 1].set_title("Category Wise Sales")

    # 3️⃣ All Products (Top 15 Clean Horizontal)
    axes[1, 0].barh(display_products.index[::-1], display_products.values[::-1])
    axes[1, 0].set_title("Top Products (Max 15 Displayed)")

    # 4️⃣ Sales Distribution
    axes[1, 1].hist(df[sales_col], bins=10)
    axes[1, 1].set_title("Sales Distribution")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.show()

    # Separate clean Top 5 Highlight
    plt.figure(figsize=(8, 5))
    plt.bar(top5.index, top5.values)
    plt.title("Top 5 Products", fontsize=14)
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.show()



def download_graphs():
    if df is None:
        messagebox.showwarning("Warning", "Run analysis first")
        return

    folder = filedialog.askdirectory(title="Select Folder")
    if not folder:
        return

    try:
        # Sales Over Time
        monthly.plot(title="Sales Over Time")
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(folder, "sales_over_time.png"), dpi=300)
        plt.close()

        # Category Wise Sales
        cat.plot(kind="bar", title="Category Wise Sales")
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(folder, "category_sales.png"), dpi=300)
        plt.close()

        # All Products
        all_products.plot(kind="bar", title="All Products Sales")
        plt.xticks(rotation=90)
        plt.savefig(os.path.join(folder, "all_products.png"), dpi=300)
        plt.close()

        # Top 5 Products
        top5.plot(kind="bar", title="Top 5 Products")
        plt.xticks(rotation=45)
        plt.savefig(os.path.join(folder, "top5_products.png"), dpi=300)
        plt.close()

        # Category Share
        cat.plot(kind="pie", autopct="%1.1f%%", title="Category Share")
        plt.savefig(os.path.join(folder, "category_share.png"), dpi=300)
        plt.close()

        # Sales Distribution
        df[sales_col].plot(kind="hist", bins=10, title="Sales Distribution")
        plt.savefig(os.path.join(folder, "sales_distribution.png"), dpi=300)
        plt.close()

        messagebox.showinfo("Success", "Graphs downloaded successfully!")

    except Exception as e:
        messagebox.showerror("Error", f"Error saving graphs:\n{e}")


# UI
root = Tk()
root.title("Dynamic Retail Sales Analyzer - Pro Version")
root.geometry("360x230")

Label(root, text="Dynamic Retail Sales Analyzer", font=("Arial", 12)).pack(pady=10)

Button(root, text="Upload Dataset & Analyze", width=28, command=run_analysis).pack(pady=5)
Button(root, text="Download Visualizations", width=28, command=download_graphs).pack(pady=5)

root.mainloop()
