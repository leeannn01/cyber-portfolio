---
title: "Detector Module"
date: 2025-03-17 14:00:00 +0800
categories: [Projects]
tags: [Traffic Network Analysis Tool]
permalink: /detector/
---

# 1. Introduction

The **Detector Module** (`detector.py`) module is an essential component of the Network Traffic Analysis Toolkit, designed to analyze and flag potentially malicious network traffic. 

By leveraging heuristic-based analysis, the detector identifies:
- **Unusual port activity** (e.g., SSH brute-force attempts, unauthorized SMB access).
- **Large packet sizes**, indicative of data exfiltration or denial-of-service (DoS) attacks.
- **Suspicious payload content**, detecting common attacker commands (e.g., wget, powershell, /bin/bash).
- **Traffic direction classification**, distinguishing inbound, outbound, internal, and external traffic patterns.

This module plays a crucial role in **automated cybersecurity monitoring**, aiding security analysts in identifying and mitigating threats efficiently.

# 2. Design Considerations and Rationale

## 2.1. Why Heuristic-Based Detection?

Instead of relying on signature-based detection (like traditional antivirus software), this module applies heuristics to detect anomalies. The rationale behind this approach includes:

- **Flexibility**: Can detect unknown threats without predefined signatures.
- **Low Overhead**: Runs efficiently on large datasets without requiring complex machine learning models.
- **Actionable Insights**: Clearly identifies why a packet is suspicious.

## 2.2. Key Detection Criteria

| Feature                   | Reason for Inclusion                                                                 |
|---------------------------|-------------------------------------------------------------------------------------|
| **Port-based filtering**   | Identifies traffic on commonly abused ports (e.g., SSH-22, RDP-3389, SMB-445).     |
| **Packet size analysis**   | Large packets may indicate **data exfiltration** or **DoS attacks**.               |
| **Payload inspection**     | Detects **attack commands** embedded in network traffic.                           |
| **Traffic direction analysis** | Determines if traffic is **inbound, outbound, internal, or external**, aiding investigation. |

## 2.3. Design Choices

| Decision                                      | Reasoning                                                                 |
|-----------------------------------------------|---------------------------------------------------------------------------|
| **Removed source_ip & dest_ip**              | The dataset already included `source` and `destination`, making these redundant. |
| **Used on_bad_lines="skip" when reading CSV** | Prevents parsing failures on malformed data.                             |
| **Converted NaN values in payload to empty strings** | Ensures payload detection does not fail on missing values.           |



# 3. Implementation Details
The implementation consists of several key functions, each handling a different aspect of traffic analysis. Below are some of the major components:

## 3.1. Port-Based Threat Detection

A predefined set of commonly targeted ports is used to detect suspicious traffic:

```python
SUSPICIOUS_PORTS = {21, 22, 23, 53, 80, 443, 445, 1433, 1521, 3306, 3389}

df.loc[df["sport"].isin(map(str, SUSPICIOUS_PORTS)), "suspicious_reason"] += "Suspicious source port; "
df.loc[df["dport"].isin(map(str, SUSPICIOUS_PORTS)), "suspicious_reason"] += "Suspicious destination port; "
```

## 3.2. Large Packet Detection

Packets exceeding a predefined size threshold are flagged as potentially suspicious:

```python
LARGE_PACKET_SIZE = 1500
df.loc[df["length"] > LARGE_PACKET_SIZE, "suspicious_reason"] += "Large packet size detected; "
```

## 3.3. Payload Inspection

The module searches for known malicious commands in packet payloads, detecting potential remote code execution attempts:

```python
SUSPICIOUS_KEYWORDS = ["cmd.exe", "powershell", "wget", "curl", "/bin/sh", "/bin/bash"]
df["suspicious_payload"] = df["payload"].fillna("").apply(contains_suspicious_payload)
df.loc[df["suspicious_payload"], "suspicious_reason"] += "Suspicious payload detected; "
```

## 3.4. Traffic Direction Classification

To better understand attack patterns, the module classifies network traffic as inbound, outbound, internal, or external:
```python
def classify_traffic_direction(row):
    src = row["source"]
    dst = row["destination"]
    src_internal = is_internal_ip(src)
    dst_internal = is_internal_ip(dst)

    if src_internal and not dst_internal:
        return "outbound"
    elif not src_internal and dst_internal:
        return "inbound"
    elif src_internal and dst_internal:
        return "internal"
    else:
        return "external"

df["traffic_direction"] = df.apply(classify_traffic_direction, axis=1)
```

# 4. Debugging and Challenges

## 4.1. Malformed CSV Parsing Error: 
4.1 Malformed CSV Parsing Errors

**Issue**: Some CSV files contained corrupt or malformed data, causing Pandas to throw a `ParserError`.

**Fix**: Skipped problematic lines:
```python
df = pd.read_csv(file, engine="python", on_bad_lines="skip")
```

## 4.2. Missing Payload Column

**Issue**: Some datasets did not include a payload column, causing the payload analysis function to fail.

**Fix**: Ensured the column exists before processing:
```python
if "payload" not in df.columns:
    df["payload"] = ""
```

## 4.3 Handling NaN Values in Payload Detection

**Issue**: Applying the `contains_suspicious_payload()` function on missing values caused filtering issues.

**Fix**: Converted `NaN` values to empty strings before analysis:
```python
df["suspicious_payload"] = df["payload"].fillna("").apply(contains_suspicious_payload)
```

## 4.4. Traffic Direction Analysis Fails on Invalid IPs

**Issue**: Some records contained invalid or missing IPs, breaking the `is_internal_ip()` function.

**Fix**: Wrapped the function in a `try-except` block:
```python
try:
    ip_obj = ipaddress.ip_address(ip)
    return any(ip_obj in net for net in INTERNAL_NETWORKS)
except ValueError:
    return False
```

# 5. Deployment Considerations

## 5.1. Instllation Requirements
The following dependencies must be installed:
```bash
pip install pandas ipaddress
```

## 5.2. Running the Detector
```bash
python3 detector.py <input_csv> <output_folder>
```

## 5.3. Expected Output

The detector produces:
- **CSV file (malicious_traffic.csv)** – Lists all suspicious packets.
- **Summary report (malicious_summary.txt)** – Provides a high-level overview of detected threats.

#### Example CSV file output

| Time     | Source      | Destination | Suspicious Reason           | Traffic Direction |
|----------|------------|-------------|-----------------------------|-------------------|
| 10:01:05 | 192.168.1.2 | 8.8.8.8     | Large packet size detected  | Outbound          |
| 10:02:10 | 192.168.1.2 | 192.168.1.1 | Suspicious payload detected | Internal          |

# 6. Conclusion and next steps

## 6.1. Key Takeaways
The detector.py module successfully implements multiple heuristic techniques for identifying malicious network activity. Key benefits include:

- Detects multiple threat indicators (suspicious ports, large packets, payload anomalies).
- Traffic direction analysis provides additional context for investigations.
- Automated processing of large datasets with minimal overhead.

## 6.2. Future Enhancements
- Integrate real-time network monitoring to analyze live traffic instead of just PCAP files.
- Enhance payload analysis using machine learning to detect previously unseen attack patterns.
- Add external threat intelligence feeds to enrich analysis results.
- Create a bash script (`setup_detector.sh`) for easy setup

# Appendix: Full Python Script
For full implementation details, visit the [GitHub Repository](https://github.com/leeannn01/leeannn01.github.io/blob/main/projects/network-traffic-analysis-tool/src/detector.py)