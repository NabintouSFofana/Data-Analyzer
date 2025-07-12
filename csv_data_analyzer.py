# ================================
# 📊 CSV Data Analyzer (Pro Version with Safe Fallback)
# ================================

import matplotlib
matplotlib.use('Agg')
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import argparse
import os

# ================================
# Load CSV
# ================================
def load_csv(file_path):
    try:
        df = pd.read_csv(file_path)
        print("✅ CSV loaded successfully!")
        return df
    except Exception as e:
        print(f"❌ Failed to load CSV: {e}")
        return None

# ================================
# Clean Data
# ================================
def clean_data(df):
    initial_rows = len(df)
    df = df.drop_duplicates()
    final_rows = len(df)
    print(f"🧹 Removed {initial_rows - final_rows} duplicate rows.")
    return df

# ================================
# Compute Data Quality Score
# ================================
def compute_data_quality_score(df):
    total_cells = df.size
    missing_values = df.isnull().sum().sum()
    duplicate_rows = df.duplicated().sum()
    constant_columns = [col for col in df.columns if df[col].nunique() == 1]

    quality_score = 100
    missing_pct = (missing_values / total_cells) * 100 if total_cells else 0
    duplicate_pct = (duplicate_rows / len(df)) * 100 if len(df) else 0

    quality_score -= missing_pct
    quality_score -= duplicate_pct
    quality_score -= len(constant_columns) * 5

    quality_score = max(0, round(quality_score, 2))

    print(f"🔍 Data Quality Report:")
    print(f" Missing: {missing_values} ({missing_pct:.2f}%)")
    print(f" Duplicates: {duplicate_rows} ({duplicate_pct:.2f}%)")
    print(f" Constant Columns: {len(constant_columns)} {constant_columns}")
    print(f" 👉 Data Quality Score: {quality_score}%")

    return quality_score

# ================================
# Analyze Column (Safe)
# ================================
def analyze_column(df, column):
    if column not in df.columns:
        print(f"❌ Column '{column}' not found.")
        return None

    if pd.api.types.is_numeric_dtype(df[column]):
        stats = {
            'mean': df[column].mean(),
            'median': df[column].median(),
            'std': df[column].std(),
            'min': df[column].min(),
            'max': df[column].max(),
        }
    else:
        stats = {}
        print(f"ℹ️ Column '{column}' is non-numeric. Skipping numeric stats.")

    print(f"📊 Stats for '{column}': {stats}")
    return stats

# ================================
# Smart Plot (Safe)
# ================================
def plot_column(df, column, filename="plot.png"):
    plt.figure(figsize=(10, 6))
    if pd.api.types.is_numeric_dtype(df[column]) and df[column].nunique() > 20:
        plt.hist(df[column].dropna(), bins=20, color='skyblue', edgecolor='black')
    else:
        counts = df[column].value_counts().sort_index()
        if counts.empty:
            print(f"⚠️ No data to plot for column '{column}'. Skipping plot.")
            return
        counts.plot(kind='bar', color='skyblue', edgecolor='black')
    plt.title(f"Distribution of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()
    print(f"✅ Plot saved as '{filename}'.")

# ================================
# Save Cleaned CSV
# ================================
def save_cleaned_csv(df):
    df.to_csv("cleaned_data.csv", index=False)
    print("✅ Cleaned CSV saved as 'cleaned_data.csv'.")

# ================================
# Generate PDF Report
# ================================
def generate_pdf(file_path, column, stats, score, plot_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "CSV Data Analyzer Report", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"File: {os.path.basename(file_path)}", ln=True)
    pdf.cell(0, 10, f"Column: {column}", ln=True)
    if stats:
        for k, v in stats.items():
            pdf.cell(0, 10, f"{k.capitalize()}: {v:.2f}", ln=True)
    else:
        pdf.cell(0, 10, "No numeric stats available.", ln=True)
    pdf.cell(0, 10, f"Quality Score: {score}%", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, "Plot:", ln=True)
    pdf.image(plot_file, x=10, y=None, w=180)
    pdf.output("analysis_report.pdf")
    print("✅ PDF report saved as 'analysis_report.pdf'.")

# ================================
# Main CLI
# ================================
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', required=True, help="Path to CSV file")
    parser.add_argument('--column', required=True, help="Column to analyze")
    args = parser.parse_args()

    df = load_csv(args.file)
    if df is not None:
        df = clean_data(df)
        score = compute_data_quality_score(df)
        stats = analyze_column(df, args.column)
        save_cleaned_csv(df)
        plot_file = "column_plot.png"
        plot_column(df, args.column, plot_file)
        generate_pdf(args.file, args.column, stats, score, plot_file)

if __name__ == "__main__":
    main()
