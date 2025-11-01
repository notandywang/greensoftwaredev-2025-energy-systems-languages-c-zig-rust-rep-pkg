#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Set publication quality settings
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 14

# Read data
df = pd.read_csv('/mnt/user-data/uploads/final.csv')
df = df[df['Language'] != 'c_gcc']

# Clean up language names
language_map = {
    'c_zig_cc': 'C (Zig CC)',
    'c_scheduler_clang': 'C (Clang)',
    'rust': 'Rust',
    'zig': 'Zig'
}
df['Language'] = df['Language'].map(language_map)
df.loc[df['Peak_Memory_KB_RSS'] == 0, 'Peak_Memory_KB_RSS'] = np.nan

# Color palette for languages
colors = {'Zig': '#52c41a', 'C (Zig CC)': '#1890ff', 'Rust': '#ff7a45', 'C (Clang)': '#722ed1'}

# Figure 1: Main energy efficiency comparison
fig1, axes = plt.subplots(1, 3, figsize=(14, 4))

# Energy by thread count
ax1 = axes[0]
for lang in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']:
    lang_data = df[df['Language'] == lang]
    mean_energy = lang_data.groupby('Threads')['Energy_Joules'].mean()
    std_energy = lang_data.groupby('Threads')['Energy_Joules'].std()
    ax1.errorbar(mean_energy.index, mean_energy.values, yerr=std_energy.values,
                 marker='o', label=lang, linewidth=2, capsize=3, color=colors[lang])
ax1.set_xlabel('Number of Threads')
ax1.set_ylabel('Energy Consumption (Joules)')
ax1.set_title('(a) Energy Consumption vs Thread Count')
ax1.set_xscale('log', base=2)
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

# Energy efficiency per task
ax2 = axes[1]
df['Energy_per_Task'] = df['Energy_Joules'] / df['Tasks']
for lang in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']:
    lang_data = df[df['Language'] == lang]
    mean_eff = lang_data.groupby('Tasks')['Energy_per_Task'].mean()
    ax2.plot(mean_eff.index, mean_eff.values * 1000, marker='s', 
             label=lang, linewidth=2, markersize=7, color=colors[lang])
ax2.set_xlabel('Number of Tasks')
ax2.set_ylabel('Energy per Task (mJ/Task)')
ax2.set_title('(b) Energy Efficiency vs Workload Size')
ax2.set_xscale('log')
ax2.set_yscale('log')
ax2.legend(loc='best')
ax2.grid(True, alpha=0.3)

# Overall comparison boxplot
ax3 = axes[2]
bp = ax3.boxplot([df[df['Language'] == lang]['Energy_Joules'].values 
                   for lang in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']],
                  labels=['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)'],
                  patch_artist=True, showmeans=True)
for patch, color in zip(bp['boxes'], [colors[l] for l in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax3.set_ylabel('Energy Consumption (Joules)')
ax3.set_title('(c) Overall Energy Distribution')
ax3.grid(True, alpha=0.3, axis='y')

plt.suptitle('Figure 1: Energy Consumption Analysis', y=1.02)
plt.tight_layout()
plt.savefig('/home/claude/figure1_energy_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Figure 2: Performance and scalability analysis
fig2, axes = plt.subplots(1, 3, figsize=(14, 4))

# Execution time
ax1 = axes[0]
for lang in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']:
    lang_data = df[df['Language'] == lang]
    mean_time = lang_data.groupby('Threads')['Real_Time_Seconds'].mean()
    ax1.plot(mean_time.index, mean_time.values * 1000, marker='o', 
             label=lang, linewidth=2, color=colors[lang])
ax1.set_xlabel('Number of Threads')
ax1.set_ylabel('Execution Time (ms)')
ax1.set_title('(a) Execution Time vs Thread Count')
ax1.set_xscale('log', base=2)
ax1.legend(loc='best')
ax1.grid(True, alpha=0.3)

# Memory usage (excluding NaN)
ax2 = axes[1]
df_mem = df.dropna(subset=['Peak_Memory_KB_RSS'])
bp = ax2.boxplot([df_mem[df_mem['Language'] == lang]['Peak_Memory_KB_RSS'].values / 1024
                   for lang in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']],
                  labels=['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)'],
                  patch_artist=True)
for patch, color in zip(bp['boxes'], [colors[l] for l in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']]):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax2.set_ylabel('Peak Memory Usage (MB)')
ax2.set_title('(b) Memory Usage Distribution')
ax2.grid(True, alpha=0.3, axis='y')

# Energy-Time efficiency scatter
ax3 = axes[2]
mean_vals = df.groupby(['Language', 'Threads']).agg({
    'Energy_Joules': 'mean',
    'Real_Time_Seconds': 'mean'
}).reset_index()
for lang in ['Zig', 'C (Zig CC)', 'Rust', 'C (Clang)']:
    lang_data = mean_vals[mean_vals['Language'] == lang]
    ax3.scatter(lang_data['Real_Time_Seconds'] * 1000, lang_data['Energy_Joules'],
               label=lang, s=60, alpha=0.7, color=colors[lang])
ax3.set_xlabel('Execution Time (ms)')
ax3.set_ylabel('Energy Consumption (Joules)')
ax3.set_title('(c) Energy-Time Trade-off')
ax3.legend(loc='best')
ax3.grid(True, alpha=0.3)

plt.suptitle('Figure 2: Performance and Resource Usage Analysis', y=1.02)
plt.tight_layout()
plt.savefig('/home/claude/figure2_performance_analysis.png', dpi=300, bbox_inches='tight')
plt.show()

# Create summary tables
print("Creating summary tables...")

# Table 1: Energy consumption summary
energy_summary = df.groupby('Language')['Energy_Joules'].agg(['mean', 'std', 'min', 'max'])
energy_summary.columns = ['Mean (J)', 'Std Dev (J)', 'Min (J)', 'Max (J)']
energy_summary = energy_summary.round(2)
print("\nTable 1: Energy Consumption Summary")
print(energy_summary.to_string())

# Table 2: Relative efficiency (normalized to C Clang)
baseline = df[df['Language'] == 'C (Clang)']['Energy_Joules'].mean()
relative_eff = df.groupby('Language')['Energy_Joules'].mean() / baseline * 100
relative_eff = relative_eff.round(1)
print("\nTable 2: Relative Energy Efficiency (C Clang = 100%)")
for lang, val in relative_eff.items():
    print(f"{lang}: {val}%")

# Save tables to LaTeX
energy_summary.to_latex('/home/claude/table1_energy_summary.tex', 
                       caption='Energy Consumption Summary Statistics',
                       label='tab:energy_summary')

print("\nFigures and tables saved successfully!")
