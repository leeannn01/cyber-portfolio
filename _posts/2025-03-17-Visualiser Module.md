---
title: "Visualiser Module"
date: 2025-03-17 15:00:00 +0800
categories: [Projects]
tags: [Traffic Network Analysis Tool]
permalink: /visualiser/
---

# 1. Introduction

The **Visualizer Module** (`visualiser.py`) is a key component of the Network Traffic Analysis Toolkit, designed to convert raw network data into clear, structured visualizations. This helps security analysts quickly detect anomalies, identify patterns, and analyze suspicious activity in network traffic.

The Visualizer consists of **six key visualization** components:
1. **Packet Flow + Alerts Timeline** – Highlights packet volume trends and anomalies over time.
2. **Top Offending IPs** – Identifies IPs responsible for the highest number of flagged events.
3. **Alert Type Distribution** – Visualizes different security threats detected in the network.
4. **Protocol Usage & Suspicious Activity** – Distinguishes between normal and risky protocols.
5. **Communication Network Graph** – Maps device interactions for understanding network topology.
6. **Suspicious Activity Heatmap** – Provides a time-based heatmap of high-risk activity.

This report documents the design considerations, implementation, debugging challenges, and deployment aspects of this module.

# 2. Design Considerations and Rationale

The main goals when designing the Visualizer were:
- **Readability** – Network data should be easy to interpret at a glance.
- **Performance Efficiency** – Able to handle large datasets without excessive resource consumption.
- **Modularity** – Each visualization is independent, allowing for future modifications and reuse.

## 2.1. Design Choices and Justification

1. **Matplotlib & Seaborn for Visualization**: Chosen for their customizability and clarity in cybersecurity data representation.
2. **Handling Missing Data**: Instead of dropping missing timestamps, we set them to 0, ensuring no artificial gaps in the data.
3. **Optimized Legends**: Each visualization now includes a legend for better interpretability.
4. **Graph-based Network Mapping**: We used ***NetworkX*** to visualize communication between IPs dynamically.

# 3. Implementation Details

## 3.1. Data Handling & Preprocessing
- Safe CSV reading using pd.read_csv() with on_bad_lines='skip' to avoid issues with malformed data.
- Time synchronization using pd.to_datetime() to convert timestamps into a standard format.
- Handling missing values by merging datasets and explicitly setting gaps to 0.

## 3.2. Visualisation Modules

### 3.2.1. Packet Flow + Alerts Timeline

**Purpose**: Helps analysts see when suspicious traffic spikes occur.

**Implementation**:
```python
sns.lineplot(data=analyzer_df, x="time", y="length", label="Normal Traffic", linewidth=1.5, alpha=0.7, ci=None)
sns.scatterplot(data=detector_df, x="time", y="length", color='red', marker='x', s=50, label="Suspicious Packets")
```

- Removes CI (ci=None) to avoid unwanted smoothing.
- Scatterplot for Anomalies ensures outliers are highlighted.

### 3.2.2. Top Offending IPs
```python
sns.barplot(y=top_offenders.index, x=top_offenders.values, palette="Reds_r")
plt.legend(title="IP Addresses", loc="best")
```
- Ranks top 10 offending IPs dynamically.
- Uses a red color scheme to indicate risk.

### 3.2.3. Alert Type Distribution (Pie & Bar Chart)
```python
sns.barplot(x=alert_counts.index, y=alert_counts.values, palette="Blues_r")
plt.legend(title="Alert Types", loc="best")
```
- Pie Chart for proportions, Bar Chart for precise comparisons.
- Legend added for clarity.

### 3.2.4. Protocol Usage & Suspicious Activity
```python
sns.barplot(x=protocol_counts_suspicious.index, y=protocol_counts_suspicious.values, palette="Reds_r")
plt.legend(title="Suspicious Protocols", loc="best")
```
- Helps detect protocol abuse (e.g., excessive SSH traffic might indicate brute-force attempts).
- Red highlights riskier protocols.

### 3.2.5. Communication Network Graph
```python
plt.title(f"Communication Network\nTotal Nodes: {total_nodes}", fontsize=14, fontweight="bold")
plt.legend(handles=legend_labels, loc="best")
```
- Nodes dynamically sized based on activity level.
- Purple edges indicate mixed (normal + suspicious) traffic.

### 3.2.6. Suspicious Activity Heatmap
```python
sns.heatmap(heatmap_data.T, cmap="Reds", linewidths=0.5, annot=True, fmt="d")
```
- Directly highlights peak attack times.
- White spaces indicate low/no activity.

# 4. Debugging and Challenges

## 4.1. Floating “X” in Scatter Plots

**Issue**: Suspicious traffic appeared detached from normal traffic.

**Fix**: Ensured timestamps with missing data were explicitly set to 0, preventing misleading gaps.

## 4.2. `FutureWarnings` in Seaborn (ci=False)

**Issue**: Seaborn’s ci=False option was deprecated.
**Fix**: Used ci=None instead of ci=False, as per the latest Seaborn recommendations.

## 4.3. `AttributeError` (numpy.ndarray has no attribute 'name')

**Issue**: Occurred when adding legends in bar plots.
**Fix**: Explicitly assigned legend labels instead of relying on automatic naming.

## 4.4. Communication Graph Clutter

**Issue**: Overlapping nodes and edges made the graph unreadable.
**Fix**: Adjusted node spacing (k=0.5 in spring_layout) and limited labels to high-degree nodes.

# 5. Deployment Considerations

To ensure smooth setup and execution of the Visualizer Module, the following dependencies and system configurations are required:

## 5.1. System Requirements
- Python 3.8+ (Recommended for compatibility and performance)
- Required Python Libraries:
    - pandas
	- matplotlib
	- seaborn
	- networkx

#### Installation Command:
```bash
pip install pandas matplotlib seaborn networkx
```

## 5.2. Setting Up the Environment

A Bash setup script can be used to automatically install dependencies and configure the environment.

#### For Linux/ MacOS:
```bash
#!/bin/bash
echo "Installing dependencies..."
pip install pandas matplotlib seaborn networkx
echo "Setup Complete!"
```

#### For Windows (Using PowerShell or CMD):
```powershell
pip install pandas matplotlib seaborn networkx
```
Additionally, Windows users may need to ensure their Python environment is correctly configured in their system PATH.

## 5.3. Running the Visualizer

Once installed, the visualizer can be run using the following command:
Where:
- `analyzer_output.csv` → Processed network traffic data.
- `detector_output.csv` → Identified suspicious activity.
- `output_folder/` → Directory where visualizations will be stored.

## 5.4. Expected Output

The Visualizer Module generates multiple graphical outputs for analyzing network activity:
1. **packet_flow_with_alerts.png** → Displays normal & suspicious traffic over time.
2. **top_offending_ips.png** → Identifies the most frequently flagged IPs.
3. alert_type_distribution_pie.png & alert_type_distribution_bar.png → Show different alert categories.
4. **protocol_usage_normal.png & protocol_usage_suspicious.png** → Highlights protocol distribution.
5. **communication_network.png** → Network graph showing interactions between devices.
6. **suspicious_activity_heatmap.png** → Heatmap of high-risk activity over time.

All these outputs help security analysts visualize **potential threats** and **gain insights into network traffic patterns**.

# 6. Conclusion and Next Steps

## 6.1. Key Takeaways
- Modular design enhances maintainability.
- Proper data handling prevents misleading graphs.
- Legends and annotations significantly improve clarity.

## 6.2. Future Enhancements
- Interactive dashboards instead of static plots.
- Real-time visualization support.
- Machine learning for anomaly detection.
- Create a bash script (`setup_visualiser.sh`) for easy setup

# Appendix: Full Python Script
For full implementation details, visit the [GitHub Repository](https://github.com/leeannn01/leeannn01.github.io/blob/main/projects/network-traffic-analysis-tool/src/visualiser)