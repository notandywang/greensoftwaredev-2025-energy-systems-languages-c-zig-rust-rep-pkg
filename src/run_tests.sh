#!/bin/bash

# This script compiles and runs the C, Rust, and Zig schedulers
# with varying threads and tasks, measuring energy, memory, and performance
# Results are written to a CSV file for external analysis.

set -e

# --- Configuration ---
WORKLOAD_SIZES=(100 1000 10000 100000 1000000)
NUM_THREADS_ARRAY=(8 16 32 64 128)
REPETITIONS=10
COOL_DOWN_SECONDS=1

OUTPUT_BASE_DIR="test_results_methodology"
CSV_FILE="${OUTPUT_BASE_DIR}/results.csv"

# --- Check for necessary tools ---
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: '$1' command not found. Please install it."
        exit 1
    fi
}

check_command "perf"
check_command "/usr/bin/time" # this is not the normal time command
check_command "bc"

# --- Create base output directory and CSV file ---
mkdir -p "$OUTPUT_BASE_DIR"

echo "Language,Threads,Tasks,Repetition,Energy_Joules,Peak_Memory_KB_RSS,Real_Time_Seconds" > "$CSV_FILE"

echo "--- Compiling all schedulers ---"
./src/compile.sh

echo "--- Running tests matching PDF methodology ---"

declare -A executables
#executables["c_gcc"]="./src/c/c_scheduler_gcc"
executables["c_zig_cc"]="./src/c/c_scheduler_zig_cc"
executables["c_scheduler_clang"]="./src/c/c_scheduler_clang"
executables["rust"]="./src/rust/rust_scheduler"
executables["zig"]="./src/zig/zig_scheduler"

# Loop through each language
for lang_key in "${!executables[@]}"; do
    EXEC_PATH="${executables[$lang_key]}"
    EXEC_NAME=$(basename "$EXEC_PATH")

    # Loop through each workload size
    for total_tasks in "${WORKLOAD_SIZES[@]}"; do

        # Loop through each number of threads
        for num_threads in "${NUM_THREADS_ARRAY[@]}"; do

            echo "\n--- Testing ${EXEC_NAME} (${lang_key}) with ${num_threads} threads and ${total_tasks} tasks ---"

            # Loop for repetitions
            for i in $(seq 1 $REPETITIONS); do
                echo "  Repetition $i/$REPETITIONS..."

                CURRENT_OUTPUT_DIR="${OUTPUT_BASE_DIR}/${lang_key}_${num_threads}threads_${total_tasks}tasks"
                mkdir -p "$CURRENT_OUTPUT_DIR"

                PERF_OUTPUT="${CURRENT_OUTPUT_DIR}/rep${i}_perf.txt"
                TIME_OUTPUT="${CURRENT_OUTPUT_DIR}/rep${i}_time.txt"

                echo "    Running perf stat for energy..."
                perf stat -e power/energy-pkg/ -o "$PERF_OUTPUT" -- "$EXEC_PATH" "$num_threads" "$total_tasks" &> /dev/null

                echo "    Running /usr/bin/time for execution time and other stats..."
                /usr/bin/time -v -o "$TIME_OUTPUT" "$EXEC_PATH" "$num_threads" "$total_tasks"

                ENERGY=$(grep "energy-pkg" "$PERF_OUTPUT" | awk '{print $1}' | sed 's/,//')
                MEMORY=$(grep "Maximum resident set size (kbytes):" "$TIME_OUTPUT" | awk '{print $NF}')
                TIME_STR=$(grep "Elapsed (wall clock) time" "$TIME_OUTPUT" | awk '{print $NF}')

                TOTAL_SECONDS=0
                if [[ "$TIME_STR" =~ ^([0-9]+):([0-9]{2}).([0-9]{2})$ ]]; then
                    MINUTES=${BASH_REMATCH[1]}
                    SECONDS=${BASH_REMATCH[2]}
                    MILLISECONDS=${BASH_REMATCH[3]}
                    TOTAL_SECONDS=$(echo "$MINUTES * 60 + $SECONDS + $MILLISECONDS / 100" | bc -l)
                elif [[ "$TIME_STR" =~ ^([0-9]+).([0-9]{2})$ ]]; then
                    SECONDS=${BASH_REMATCH[1]}
                    MILLISECONDS=${BASH_REMATCH[2]}
                    TOTAL_SECONDS=$(echo "$SECONDS + $MILLISECONDS / 100" | bc -l)
                else
                    TOTAL_SECONDS=0 
                fi

                echo "$lang_key,$num_threads,$total_tasks,$i,$ENERGY,$MEMORY,$TOTAL_SECONDS" >> "$CSV_FILE"

                if [ "$i" -lt "$REPETITIONS" ]; then
                    echo "    Cooling down for ${COOL_DOWN_SECONDS} seconds..."
                    sleep "$COOL_DOWN_SECONDS"
                fi
            done
        done # End num_threads loop
    done # End total_tasks loop
done # End lang_key loop

echo "\n--- All tests finished. Raw results are in '${CSV_FILE}'. ---"
