#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style for better-looking plots
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Read the data
df = pd.read_csv('/mnt/user-data/uploads/final.csv')

# Exclude c_gcc as requested
df = df[df['Language'] != 'c_gcc']

# Clean up language names for better presentation
language_map = {
    'c_zig_cc': 'C (Zig CC)',
    'c_scheduler_clang': 'C (Clang)',
    'rust': 'Rust',
    'zig': 'Zig'
}
df['Language'] = df['Language'].map(language_map)

# Handle zero memory values - replace with NaN for now
df.loc[df['Peak_Memory_KB_RSS'] == 0, 'Peak_Memory_KB_RSS'] = np.nan

# Calculate means and standard deviations for each configuration
summary_stats = df.groupby(['Language', 'Threads', 'Tasks']).agg({
    'Energy_Joules': ['mean', 'std'],
    'Peak_Memory_KB_RSS': ['mean', 'std'],
    'Real_Time_Seconds': ['mean', 'std']
}).round(3)

# Save summary statistics to CSV
summary_stats.to_csv('/home/claude/summary_statistics.csv')

print("=== SUMMARY STATISTICS ===")
print("\nOverall means by language:")
overall_means = df.groupby('Language').agg({
    'Energy_Joules': 'mean',
    'Peak_Memory_KB_RSS': 'mean',
    'Real_Time_Seconds': 'mean'
}).round(3)
print(overall_means)

# Create comprehensive visualizations
fig = plt.figure(figsize=(20, 16))

# 1. Energy consumption by threads for different task sizes
ax1 = plt.subplot(3, 3, 1)
for task_size in df['Tasks'].unique():
    task_data = df[df['Tasks'] == task_size]
    energy_by_thread = task_data.groupby(['Language', 'Threads'])['Energy_Joules'].mean().reset_index()
    for lang in energy_by_thread['Language'].unique():
        lang_data = energy_by_thread[energy_by_thread['Language'] == lang]
        ax1.plot(lang_data['Threads'], lang_data['Energy_Joules'], 
                marker='o', label=f'{lang} ({task_size} tasks)', linewidth=2)
ax1.set_xlabel('Number of Threads')
ax1.set_ylabel('Energy (Joules)')
ax1.set_title('Energy Consumption vs Thread Count')
ax1.set_xscale('log', base=2)
ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
ax1.grid(True, alpha=0.3)

# 2. Energy efficiency comparison - boxplot
ax2 = plt.subplot(3, 3, 2)
sns.boxplot(data=df, x='Language', y='Energy_Joules', ax=ax2)
ax2.set_xlabel('Language')
ax2.set_ylabel('Energy (Joules)')
ax2.set_title('Energy Consumption Distribution by Language')
ax2.tick_params(axis='x', rotation=45)

# 3. Task scaling - energy consumption
ax3 = plt.subplot(3, 3, 3)
for lang in df['Language'].unique():
    lang_data = df[df['Language'] == lang]
    energy_by_task = lang_data.groupby('Tasks')['Energy_Joules'].mean()
    ax3.plot(energy_by_task.index, energy_by_task.values, 
            marker='s', label=lang, linewidth=2, markersize=8)
ax3.set_xlabel('Number of Tasks')
ax3.set_ylabel('Energy (Joules)')
ax3.set_title('Energy Consumption vs Task Count')
ax3.set_xscale('log')
ax3.legend()
ax3.grid(True, alpha=0.3)

# 4. Execution time by threads
ax4 = plt.subplot(3, 3, 4)
for lang in df['Language'].unique():
    lang_data = df[df['Language'] == lang]
    time_by_thread = lang_data.groupby('Threads')['Real_Time_Seconds'].mean()
    ax4.plot(time_by_thread.index, time_by_thread.values, 
            marker='o', label=lang, linewidth=2)
ax4.set_xlabel('Number of Threads')
ax4.set_ylabel('Time (Seconds)')
ax4.set_title('Execution Time vs Thread Count')
ax4.set_xscale('log', base=2)
ax4.legend()
ax4.grid(True, alpha=0.3)

# 5. Memory usage comparison (excluding NaN values)
ax5 = plt.subplot(3, 3, 5)
df_memory = df.dropna(subset=['Peak_Memory_KB_RSS'])
if not df_memory.empty:
    sns.boxplot(data=df_memory, x='Language', y='Peak_Memory_KB_RSS', ax=ax5)
    ax5.set_xlabel('Language')
    ax5.set_ylabel('Peak Memory (KB)')
    ax5.set_title('Memory Usage Distribution by Language')
    ax5.tick_params(axis='x', rotation=45)

# 6. Energy efficiency ratio (Energy/Task)
ax6 = plt.subplot(3, 3, 6)
df['Energy_per_Task'] = df['Energy_Joules'] / df['Tasks']
for lang in df['Language'].unique():
    lang_data = df[df['Language'] == lang]
    efficiency_by_task = lang_data.groupby('Tasks')['Energy_per_Task'].mean()
    ax6.plot(efficiency_by_task.index, efficiency_by_task.values, 
            marker='d', label=lang, linewidth=2)
ax6.set_xlabel('Number of Tasks')
ax6.set_ylabel('Energy per Task (Joules/Task)')
ax6.set_title('Energy Efficiency (Energy per Task)')
ax6.set_xscale('log')
ax6.set_yscale('log')
ax6.legend()
ax6.grid(True, alpha=0.3)

# 7. Heatmap of energy consumption
ax7 = plt.subplot(3, 3, 7)
pivot_energy = df.groupby(['Language', 'Threads'])['Energy_Joules'].mean().reset_index()
pivot_energy = pivot_energy.pivot(index='Language', columns='Threads', values='Energy_Joules')
sns.heatmap(pivot_energy, annot=True, fmt='.1f', cmap='YlOrRd', ax=ax7)
ax7.set_title('Average Energy Consumption Heatmap\n(Language x Threads)')

# 8. Thread efficiency (speedup analysis)
ax8 = plt.subplot(3, 3, 8)
for lang in df['Language'].unique():
    lang_data = df[df['Language'] == lang]
    # Get baseline (2 threads) time for each task size and average
    baseline = lang_data[lang_data['Threads'] == 2].groupby('Tasks')['Real_Time_Seconds'].mean().mean()
    speedup_by_thread = []
    thread_counts = sorted(lang_data['Threads'].unique())
    for threads in thread_counts:
        avg_time = lang_data[lang_data['Threads'] == threads]['Real_Time_Seconds'].mean()
        speedup = baseline / avg_time
        speedup_by_thread.append(speedup)
    ax8.plot(thread_counts, speedup_by_thread, marker='o', label=lang, linewidth=2)
# Add ideal speedup line
ideal_speedup = [t/2 for t in sorted(df['Threads'].unique())]
ax8.plot(sorted(df['Threads'].unique()), ideal_speedup, 'k--', alpha=0.5, label='Ideal Speedup')
ax8.set_xlabel('Number of Threads')
ax8.set_ylabel('Speedup')
ax8.set_title('Parallel Speedup Analysis')
ax8.set_xscale('log', base=2)
ax8.legend()
ax8.grid(True, alpha=0.3)

# 9. Energy-Time trade-off scatter plot
ax9 = plt.subplot(3, 3, 9)
mean_values = df.groupby(['Language', 'Threads', 'Tasks']).agg({
    'Energy_Joules': 'mean',
    'Real_Time_Seconds': 'mean'
}).reset_index()
for lang in mean_values['Language'].unique():
    lang_data = mean_values[mean_values['Language'] == lang]
    ax9.scatter(lang_data['Real_Time_Seconds'], lang_data['Energy_Joules'], 
               label=lang, s=50, alpha=0.6)
ax9.set_xlabel('Execution Time (Seconds)')
ax9.set_ylabel('Energy (Joules)')
ax9.set_title('Energy-Time Trade-off')
ax9.legend()
ax9.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('/home/claude/energy_analysis_comprehensive.png', dpi=300, bbox_inches='tight')
plt.show()

# Calculate statistical comparisons
print("\n=== STATISTICAL COMPARISONS ===")
print("\nEnergy consumption differences between languages:")

# Perform Kruskal-Wallis test for energy consumption
languages = df['Language'].unique()
energy_groups = [df[df['Language'] == lang]['Energy_Joules'].values for lang in languages]
h_stat, p_value = stats.kruskal(*energy_groups)
print(f"Kruskal-Wallis H-statistic: {h_stat:.4f}, p-value: {p_value:.6f}")

if p_value < 0.05:
    print("Significant difference in energy consumption between languages detected.")
    
    # Pairwise comparisons
    print("\nPairwise Mann-Whitney U tests:")
    from itertools import combinations
    for lang1, lang2 in combinations(languages, 2):
        data1 = df[df['Language'] == lang1]['Energy_Joules'].values
        data2 = df[df['Language'] == lang2]['Energy_Joules'].values
        u_stat, p_val = stats.mannwhitneyu(data1, data2)
        print(f"{lang1} vs {lang2}: U={u_stat:.2f}, p={p_val:.6f}")

# Additional analysis tables
print("\n=== DETAILED ANALYSIS TABLES ===")

# Table 1: Average energy by language and thread count
energy_pivot = df.groupby(['Language', 'Threads'])['Energy_Joules'].mean().unstack()
print("\nTable 1: Average Energy Consumption (Joules) by Language and Thread Count")
print(energy_pivot.round(2))

# Table 2: Average execution time by language and thread count  
time_pivot = df.groupby(['Language', 'Threads'])['Real_Time_Seconds'].mean().unstack()
print("\nTable 2: Average Execution Time (Seconds) by Language and Thread Count")
print(time_pivot.round(3))

# Table 3: Energy efficiency ranking
print("\nTable 3: Energy Efficiency Ranking (Lower is Better)")
efficiency_rank = df.groupby('Language')['Energy_Joules'].mean().sort_values()
for rank, (lang, energy) in enumerate(efficiency_rank.items(), 1):
    print(f"{rank}. {lang}: {energy:.2f} Joules (average)")

# Save detailed results to file
with open('/home/claude/statistical_results.txt', 'w') as f:
    f.write("=== ENERGY EFFICIENCY ANALYSIS RESULTS ===\n\n")
    f.write(f"Overall Statistics:\n{overall_means.to_string()}\n\n")
    f.write(f"Energy Consumption by Language and Threads:\n{energy_pivot.to_string()}\n\n")
    f.write(f"Execution Time by Language and Threads:\n{time_pivot.to_string()}\n\n")
    f.write(f"Energy Efficiency Ranking:\n{efficiency_rank.to_string()}\n")

print("\nAnalysis complete! Files saved to /home/claude/")
