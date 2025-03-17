---
title: "Traffic Network Analysis Tool"
date: 2025-03-16 00:00:00 +0800
categories: [Projects]
tags: [Traffic Network Analysis Tool]
---

# Introduction

In the rapidly evolving landscape of cybersecurity, network traffic analysis is a crucial skill for identifying malicious activities, detecting cyber threats, and securing digital environments. Attackers continuously exploit network vulnerabilities, making it imperative to have automated tools that can analyze, detect, and visualize network activity efficiently.

This project focuses on developing a comprehensive, automated network traffic analysis toolkit that:
	•	Captures live network traffic using TCPDump for monitoring and internet scraping.
	•	Processes PCAP (Packet Capture) files to extract protocols, MAC address vendors, payloads, and downloadable files.
	•	Detects malicious traffic based on packet size, suspicious payloads, and attack target ports.
	•	Visualizes network activity to provide insights into network behavior, threats, and anomalies.

By automating these processes, the toolkit enhances cybersecurity investigations and reduces manual effort while improving detection efficiency and accuracy.

---

# Project Goals

1. Leveraging **TCPDump** for live traffic monitoring and internet scraping.
2. **Automate** network traffic analysis using a **Bash script** to execute analysis scripts.
3. **Process and analyze** PCAP files to extract details such as protocols, MAC address vendors, payloads, and downloadable files.
4. **Implement detection** mechanisms using **Python** to identify malicious traffic patterns.
5. **Visualize** malicious network activity for intuitive understanding and reporting.

This toolkit serves as a practical cybersecurity solution for security analysts, researchers, and forensic investigators, enabling efficient and automated threat detection.

---
# 1. Capturing Live Network Traffic using TCPDump

To analyze network traffic in real time, this project leverages TCPDump for capturing packets. The script capture_traffic.sh automates the process of capturing network packets and saving them in a structured format for further analysis.

## Key Features:
	•	Captures network traffic in real-time using tcpdump
	•	Saves captured packets to a PCAP file for offline analysis.
	•	Supports long-duration monitoring.

## Snippet of Command for Capturing HTTP traffic
```bash
#!/bin/bash

CAPTURE_DURATION=30
PCAP_FILE="network_traffic.pcap"

echo "Capturing network traffic..."
sudo tcpdump -i any -w $PCAP_FILE -G $CAPTURE_DURATION -W 1
```

This command captures HTTP traffic and writes it to a PCAP file for further anaysis.

**[Read More...](/_posts/2025-03-17-Live%20Capture%20Script.md)**
**[View script](../projects/network-traffic-analysis-tool/scripts/capture_traffic.sh)** 

---

# 2. Automated Network Analysis using Bash Script

The run_pcap_analysis.sh script automates the execution of the entire analysis pipeline. 

## Workflow:
	1.	Runs the analyzer module to extract key network details.
	2.	Executes the detector module to identify suspicious traffic.
	3.	Generates visualizations for network activity and security alerts.

## Snippet of automation workflow in run_pcap_analysis.sh
```bash
#!/bin/bash
echo "Analyzing PCAP file..."
python3 analyser.py $PCAP_FILE results/

echo "Detecting malicious activity..."
python3 detector.py results/packet_data.csv results/

echo "Generating network visualizations..."
python3 visualiser.py results/analyser_output.csv results/detector_output.csv results/

echo "Analysis complete! Results saved in results/"
```

By automating the network analysis process, this script significantly reduces manual effort, making it efficient and scalable.

**[Read More...](/_posts/2025-03-17-Automation%20of%20PCAP%20analysis.md)**
**[View script](../projects/network-traffic-analysis-tool/scripts/run_pcap_analysis.sh)**

---

# 3.PCAP Analysis: Extracting Network Details

The analyser.py module processes PCAP files and extracts network metadata, such as:
	•	Packet headers (source/destination IPs, MAC addresses).
	•	Protocol classification (HTTP, SSH, DNS, SMB).
	•	Payload extraction (to detect malicious content).
	•	MAC address vendor identification (using Wireshark’s OUI database).
	•	Reassembling downloadable files (PDFs, ZIPs, images).

## How It Works
	1.	Reads packets from a PCAP file using Scapy and PyShark.
	2.	Extracts relevant fields (IP, MAC, protocol, payload, dport, sport).
	3.	Identifies MAC address vendors to map devices.
	4.	Detects and reconstructs downloadable files based on magic numbers. (Extracted and Downloaded)
	5.	Saves extracted data to a structured CSV format.

## Example CSV output

| Time     | Source       | Destination  | Sport | Dport | Protocol | Payload            |
|----------|-------------|-------------|-------|-------|----------|--------------------|
| 10:01:05 | 192.168.1.2 | 8.8.8.8     | 12345 | 53    | DNS      | Query google.com  |
| 10:02:10 | 192.168.1.2 | 192.168.1.1 | 54321 | 80    | HTTP     | GET /login.php    |
| 10:03:15 | 192.168.1.2 | 192.168.1.100 | 40000 | 445  | SMB      | File Transfer     |

The extracted data serves as input for further malicious traffic detection.

**[Read More...](/_posts/2025-03-17-Analyse%20Module.md)**
**[View script](../projects/network-traffic-analysis-tool/src/analyser.py)**

---

# 4. Detecting Malicious Traffic

The detector.py module applies security heuristics to detect suspicious network activity, such as:
	•	Suspicious ports (SSH, RDP, SMB).
	•	Large packet sizes (potential DDoS attacks or data exfiltration).
	•	Payload analysis for malicious commands (e.g., wget, powershell).
	•	Traffic direction classification (inbound, outbound, internal, external).

## Example Heuristic: Large Packet Detection
```python
LARGE_PACKET_SIZE = 1500
df["suspicious_reason"] = ""

df.loc[df["length"] > LARGE_PACKET_SIZE, "suspicious_reason"] += "Large packet size detected; "
```

## Example Malicious Traffic Detection Output

 Time     | Source       | Destination  | Suspicious Reason 
|----------|-------------|-------------|--------------------|
| 10:01:05 | 192.168.1.2 | 8.8.8.8     | Large packet size detected|
| 10:02:10 | 192.168.1.2 | 192.168.1.1 | Suspicious payload detected| 

By flagging malicious packet, this module helps security teams respond to potential threats quickly.

**[Read More...](/_posts/2025-03-17-Detection%20Module.md)**
**[View script](../projects/network-traffic-analysis-tool/src/detector.py)**

---

# 5. Visualising Network Activity

The visualiser.py module generates visual insights into network traffic and security alerts.

## Key Visualisation
1.	Packet Flow + Alerts Timeline – Shows anomalies over time.
2.	Top Offending IP Addresses -  Identifies the most active suspicious devices.
3.	Alert Type Distribution - Shows distribution of different alert types (Pie and Bar chart)
4.	Protocol Usage & Suspicious Activity – Highlights high-risk protocols.
5.	Communication Network (Graph) – Maps interactions between devices.
6.	Suspicious Activity Heatmap – Visualizes spikes in malicious behavior.

## Example (Snippet): Suspecious Activitiy Heatmap
```python
plt.figure(figsize=(12, 6))
sns.heatmap(heatmap_data.T, cmap="Reds", linewidths=0.5, annot=True, fmt="d")
plt.xlabel("Time")
plt.ylabel("Alert Type")
plt.title("Suspicious Activity Heatmap (Alerts Over Time)")
```

This visualization helps identify attack patterns and peak threat times.

**[Read More...](/_posts/2025-03-17-Visualisation%20Module.md)**
**[View script](../projects/network-traffic-analysis-tool/src/visualiser.py)**

---

# Conclusion

This project delivers a powerful, automated cybersecurity toolkit that:
- Captures live network traffic using TCPDump.
- Automates PCAP analysis using Bash scripting.
- Extracts network metadata and reconstructs files.
- Detects malicious traffic with Python-based heuristics.
- Visualizes security threats for quick insights.

---

# Future Enhancement

- Integrate real-time threat intelligence feeds.
- Implement ML-based anomaly detection.
- Expand protocol analysis for deeper packet inspection.

Cybersecurity is a continuous battle—this toolkit is a step toward securing networks proactively.