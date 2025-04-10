import pandas as pd
import matplotlib.pyplot as plt
import os
from matplotlib.ticker import MaxNLocator

def plot_error_label_distribution(file_path):
    # 1. LOAD THE DATA
    df = pd.read_excel(file_path)

    # 2. Extract model name from filename
    model_name = os.path.basename(file_path).replace("_results_analysis.xlsx", "")
    model_name_clean = model_name.replace("_", r"\ ")

    # 3. FILTER OUT CORRECT ANSWERS
    df_errors = df[df['Correct'] != True]
    df_correct = df[df['Correct'] == True]
    num_correct = len(df_correct)
    total_queries = len(df)

    # 4. COLLECT ERROR CATEGORIES
    error_cols = ["Error Category", "Error Category 2", "Error Category 3", "Error Category 4"]
    all_error_labels = df_errors[error_cols].stack().dropna()

    # NEW: Calculate average number of errors per query
    total_errors = len(all_error_labels)
    avg_errors_per_query = round(total_errors / total_queries, 2)

    # 5. COUNT FREQUENCIES
    label_counts = all_error_labels.value_counts()

    # 6. PLOT
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(label_counts.index, label_counts.values, color='gray', edgecolor='black')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    # 7. Title & subtitle with avg. errors
    plt.title(
        f"$\\bf{{Label\\ Frequency\\ of\\ Errors\\ –\\ {model_name_clean}}}$\n"
        f"Correctly Answered: {num_correct} / {total_queries} | "
        f"Avg. Errors per Query: {avg_errors_per_query}",
        fontsize=12
    )
    plt.xlabel("Error Category", fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.xticks(rotation=45, ha='right', fontsize=11)
    plt.yticks(fontsize=11)

    # 8. Add values on top of bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, height + 0.5, f'{int(height)}',
                ha='center', va='bottom', fontsize=10)

    # 9. Aesthetic cleanup
    ax.set_facecolor('white')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(False)
    plt.tight_layout()
    plt.show()
