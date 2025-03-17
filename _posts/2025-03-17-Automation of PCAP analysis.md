---
title: "Automation of PCAP analysis"
date: 2025-03-17 11:00:00 +0800
categories: [Projects]
tags: [Traffic Network Analysis Tool]
permalink: /automation-of-pcap-analysis/
---

# 1. Introduction

Analyzing PCAP (Packet Capture) files is a crucial task in network security and traffic monitoring. Traditionally, security analysts manually execute multiple scripts for each file, leading to inefficiencies, errors, and scalability issues.

To address this, the run_pcap_analysis.sh script was developed to:
- List available PCAP files for easy selection.
- Automate execution of key analysis scripts (`analyser.py`, `detector.py`, `visualiser.py`).
    1. **[analyser.py](https://leeannn01.github.io/analyser/)**: Extracts key network details.
	2. **[detector.py](https://leeannn01.github.io/detector/)**: Identifies suspicious activity.
	3. **[visualiser.py](https://leeannn01.github.io/visualiser/)**: Generates network traffic visualizations.
- Handle input errors and process multiple files efficiently.
ß
This report outlines the design choices, technical implementation, debugging strategies, and deployment considerations.

---

# 2. Design Considerations and Rationale

## 2.1. Goals of Automation

The script was designed with the following objectives:
- **Efficiency** - Eliminate the need to manually execute scripts.
- **Scalability** – Support batch processing of multiple PCAP files.
- **User-Friendliness** – Provide a numbered list for easy selection.
- **Robustness** – Handle incorrect user inputs and missing files gracefully.

## 2.2. Key Design Choices

| Design Choice                    | Rationale                                                        |
|----------------------------------|------------------------------------------------------------------|
| **Listing PCAP files dynamically** | Avoids hardcoding file names and allows real-time selection.   |
| **User selection via indices**    | Prevents typos and ensures valid filenames.                     |
| **Validating user input**         | Ensures the script does not break due to invalid selections.    |
| **Sequential script execution**   | Ensures a structured pipeline from analysis to visualization.   |


---

# 3. Implementation details

The script follows a structure workflow:

## 3.1. Listing Available PCAP Files

The script first scans the **specified directory** and retrive all .pcap files:

```bash
PCAP_FILES=($(ls "$PCAP_DIR"/*.pcap 2>/dev/null))
if [[ ${#PCAP_FILES[@]} -eq 0 ]]; then
    echo "No PCAP files found in $PCAP_DIR."
    exit 1
fi
```

- Uses an array to store filenames.
- Handles empty directories gracefully.

## 3.2. Displaying and Selecting Files

To allow users to select specific files, a numbered list is displayed:
```bash
for i in "${!PCAP_FILES[@]}"; do
    echo "[$i] ${PCAP_FILES[$i]##*/}"
done

read -p "Enter indices of the PCAP files to analyze (comma-separated): " INPUT
INPUT=$(echo "$INPUT" | sed 's/ //g')  # Removes spaces
IFS=',' read -r -a SELECTED_INDICES <<< "$INPUT"
```
- Removes spaces for cleaner input parsing.
- Uses an array to store user selections.

## 3.3. Validating Input and Running Scripts

To prevent errors, the script validates user input before executing:
```bash
for INDEX in "${SELECTED_INDICES[@]}"; do
    if [[ "$INDEX" =~ ^[0-9]+$ ]] && (( INDEX >= 0 && INDEX < ${#PCAP_FILES[@]} )); then
        FILE="${PCAP_FILES[$INDEX]}"
        echo "Processing: ${FILE##*/}"
        python3 analyser.py "$FILE"
        python3 detector.py "$FILE"
        python3 visualiser.py "$FILE"
        echo "Completed processing: ${FILE##*/}"
    else
        echo "Invalid index: $INDEX"
    fi
done
```
- Ensures indices are numeric and within range.
- Executes all three Python scripts sequentially.

# 4. Debugging and Challenges

Several issues were encountered and resolved during implementation:

## 4.1. Invalid User Input Handling

**Issues**
Users might enter: 
- Non-numeric values (abc,2,3)
- Out-of-range values (10,20,30)
- Whitespace issues (0,  2,3)

**Fix**:
- Used regex validation ```([[ "$INDEX" =~ ^[0-9]+$ ]])```.
- Trimmed spaces using ```sed 's/ //g'```.

## 4.2. Empty Directory Handling

**Issue**: If no PCAP files were in the directory, the script would fail.

**Fix**:
```bash
if [[ ${#PCAP_FILES[@]} -eq 0 ]]; then
    echo "No PCAP files found in $PCAP_DIR."
    exit 1
fi
```
- Ensures the script exits gracefully instead of failing.

## 4.3. Ensuring Python Scripts Receive Correct Paths

**Issue**: Python scripts needed absolute paths to function correctly.

**Fix**:
```bash
python3 analyser.py "$FILE"
```

# 5. Deployment Considerations

## 5.1. Prerequisites
To use the script, ensure the following:

#### 1. Install Python dependencies:
```bash
pip install scapy pandas matplotlib
```

#### 2. **Modify PCAP_DIR** in run_pcap_analysis.sh to match your directory.

#### 3. Ensure the script has execution permissions:
```bash
chmod +x run_pcap_analysis.sh
```

## 5.2. Running the script

#### 1. Execute:
```bash
./run_pcap_analysis.sh
```

#### 2. Select PCAP files using displayed indices.
#### 3. The script will automatically analyze and visualize the data.

---

# 6. Conclusion and Next Steps

## 6.1. Key Takeaways
The run_pcap_analysis.sh script successfully automates network traffic analysis, providing a scalable and efficient solution.

- Faster execution – Eliminates manual execution of scripts.
-  Error-handling – Handles incorrect inputs gracefully.
-  Scalability – Supports multiple PCAP files.

## 6.2. Future Improvements

- GUI-Based Selection – Replace CLI input with a user-friendly interface.
- Parallel Processing – Speed up execution using background jobs.
- Machine Learning Integration – Extend detector.py with AI-driven anomaly detection.

By automating PCAP analysis, cybersecurity professionals can focus on threat hunting rather than manual data processing.

# Appendix: Full Bash Script

For full implementation details, visit the [GitHub Repository](https://github.com/leeannn01/leeannn01.github.io/blob/main/projects/network-traffic-analysis-tool/scripts/run-pcap-analysis)