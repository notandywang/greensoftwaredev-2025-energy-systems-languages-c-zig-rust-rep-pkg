# Energy Efficiency in Systems Languages: A Comparative Study of Zig, C, and Rust for Multithreaded Applications

This repository is a companion page for the following thesis / publication:  
> **Genchev, E. and Wang, A. (2025). Energy Efficiency in Systems Languages: A Comparative Study of Zig, C, and Rust for Multithreaded Applications. Classroom of Fernando.**

It contains all the material required for replicating the study, including:  
* Source code used in the paper  
* Data used in the paper  
* Scripts to perform the statistical analysis and reproduce all tables and figures  

---

## How to cite us

The scientific article describing design, execution, and main results of this study is available [here](https://www.youtube.com/watch?v=lLWEXRAnQd0).  
If this study is helping your research, consider citing it as follows — thank you!

```
@article{genchev_wang_2025,
  title={Energy Efficiency in Systems Languages: A Comparative Study of Zig, C, and Rust for Multithreaded Applications},
  author={Genchev, Evgeni and Wang, Andy},
  journal={Classroom of Fernando},
  year={2025},
  pages={12}
}
```

---

## Quick Start

This repository contains all materials required to replicate the experiments described in the paper.  
Follow the instructions below to build, execute, and analyze the experiments.

### Getting Started

1. **Clone this repository**
   ```bash
   git clone https://github.com/notandywang/replication-package-group8.git
   cd replication-package-group8
   ```

2. **Install required tools**

   Ensure the following are available on your system:
   * `perf` (version ≥ 6.16)
   * `/usr/bin/time`
   * `pidstat` (from `sysstat`, version ≥ 12.7.7)
   * `ps` (from `procps-ng`, version ≥ 4.0.5)
   * `bc`

   On Arch Linux, these can be installed via:
   ```bash
   sudo pacman -S linux-tools sysstat procps-ng bc
   ```

3. **Compile all scheduler implementations**

   All languages (C, Rust, Zig) are built via a unified script to ensure consistent compiler flags and configurations:
   ```bash
   ./compile_all.sh
   ```

   The following compiler toolchains are used:
   * C: GCC 15.2.1, Clang 16.x (LLVM), and Zig CC 0.15.1  
   * Rust: rustc 1.89  
   * Zig: Zig 0.15.1  

4. **Run the experiments**

   The full suite of experiments (720 runs) can be reproduced automatically:
   ```bash
   ./run_tests.sh
   ```

   This script automates:
   * Verification of required tools (`perf`, `/usr/bin/time`, `pidstat`, `bc`)
   * Execution of all combinations of:
     * Programming Language (C, Rust, Zig)
     * Workload Sizes (100–10,000 tasks)
     * Thread Counts (2–64 threads)
     * Compiler Backends (GCC, Clang, Zig CC)
   * Collection of energy (J), time (s), and peak memory (KB) data  
   * Storage of results in a CSV file for later analysis

5. **Perform statistical analysis**

   The analysis script located in the [`analysis/`](analysis/) directory reproduces the descriptive statistics, ANOVA, and plots presented in the paper:
   ```bash
   python3 analysis/analyze_results.py
   ```

   The output includes:
   * Descriptive statistics tables  
   * Kruskal–Wallis and Mann–Whitney U tests  
   * Figures of energy consumption, performance, and trade-offs  

---

## Repository Structure

This is the root directory of the replication package. The directory is structured as follows:

```
replication-package-group8
│
├── src/                           # Source code of the scheduler implementations
│   ├── compile_all.sh             # Unified compilation script for all languages
│   ├── run_tests.sh               # Automated experimental runner
│   ├── c/                         # C implementations (Clang, Zig CC, GCC)
│   ├── rust/                      # Rust implementation
│   └── zig/                       # Zig implementation
│
├── data/                          # Collected and processed data used in the paper
│   ├── raw/                       # Raw measurement data (CSV)
│   ├── processed/                 # Aggregated data and summary statistics
│   └── plots/                     # Figures included in the paper
│
├── analysis/                      # Scripts for statistical analysis and plotting
│   ├── create_report_figures.py   # Generating plots 
│   └── analyze_results.py         # Statistical analysis
│
├── documentation/                 # Additional documentation 
│   └── final_report_gsd_ass3.pdf  # Final report
│
├── LICENSE                        # License file (does not exist)
└── README.md                      # This document
```

---

## Measurement and Environment Details

**Hardware:**  
AMD Ryzen Threadripper PRO 5995WX (64 cores)  
192 GB RAM  

**Software Environment:**  
Arch Linux (kernel 6.13.2)  

All experiments were conducted directly on the host system in a controlled environment.  
Before each batch of experiments, all non-essential user applications and background services were terminated to ensure stable measurements.

**Measurement Tools:**  
* Energy consumption: `perf stat` (v6.16) using `power/energy-pkg/` RAPL counter  
* Process monitoring: `pidstat` (v12.7.7) and `ps` (v4.0.5)  
* Execution time and memory: `/usr/bin/time -v`  

Each configuration was repeated ten times (720 total runs), with a one-second cool-down interval between repetitions to minimize thermal bias.  
All measurements are stored in `results.csv` with the following schema:

```
Language,Threads,Tasks,Repetition,Energy_Joules,Peak_Memory_KB_RSS,Real_Time_Seconds
```

---

## Results Reproduction

The experiment replicates the key findings from the publication:

* Zig and Zig CC achieved **7–8% lower energy consumption** compared to C (Clang) and Rust.  
* Execution time differences were minimal; both Zig and Zig CC averaged **0.23s**, compared to **0.25s** for Clang and Rust.  
* Zig’s higher memory consumption (~2×) indicates a trade-off between energy efficiency and memory footprint.  
* GCC was excluded due to **catastrophic optimization failures** (up to 700× slower).  

All result plots (Figures 1–4 in the paper) can be reproduced from scripts in [`analysis/`](analysis/).


## Acknowledgements

This replication package accompanies the Master’s course project *Green Software Development (2025)* at the University of Twente, supervised by Dr. Fernando.  
Both authors contributed equally to the design, implementation, and analysis.

---
