---
title: "Live Capture Script"
date: 2025-03-17 10:00:00 +0800
categories: [Projects]
tags: [Traffic Network Analysis Tool]
---

# 1. Introduction

In the realm of cybersecurity, network traffic analysis plays a vital role in threat detection, security investigations, and forensic analysis. As part of the Traffic Network Analysis Toolkit, I designed and implemented a Bash-based web scraping and traffic capture tool.

This tool automates the process of:
	•	Scraping web pages from a list of predefined URLs.
	•	Capturing network traffic while interacting with these websites.
	•	Storing traffic data in .pcap format for analysis.
	•	Automating periodic data collection with minimal manual intervention.

This report documents the design choices, implementation process, challenges faced, debugging methods, and key considerations for deployment.

---

# 2. Design Considerations and Rationale

## 2.1. Choosing TCPdump for Traffic Capture

To capture live network traffic, I opted for tcpdump due to its efficiency, lightweight footprint, and ability to filter and store packet data in .pcap format for offline analysis.

**Alternative Considered:**
- Wireshark/tshark: More powerful but resource-intensive for automated scripts.
- PyShark: Python-based, better for analysis but less suited for Bash automation.

**Final Decision**
TCPDump was chosen for its native Linux support, ease of automation, and compatibility with Python-based analysis.

## 2.2. Selecting a Web Scraper: curl vs. wget

Since the tool required fetching website contents while capturing traffic, I compared curl and wget:

| Feature                      | curl | wget |
|------------------------------|------|------|
| Flexibility                  | ✅   | ❌   |
| Handles redirects            | ✅   | ✅   |
| Supports concurrent downloads | ❌   | ✅   |
| CLI integration              | ✅   | ✅   |

**Final Decision:**
**curl** was selected due to its flexibility and ability to integrate seamlessly into the script.

## 2.3. Storing Captured Data Efficiently
- Each .pcap file needed to be individually named using the website name + timestamp for traceability.
- A dedicated storage directory (captured_pcaps/) was created to organize the captured files.

---

# 3. Implementation Details

## 3.1. Script Workflow
1. Read the list of target websites from a .txt file.
2.	Loop through each website, starting a tcpdump session.
3.	Use curl to retrieve the web page while traffic is being captured.
4.	Stop tcpdump after a predefined duration.
5.	Store each .pcap file with a timestamped filename in a designated folder.

## 3.2. Key Code Snippets

### Reading the Website List
```bash
URL_LIST="websites.txt"
while IFS= read -r website; do
    scrape_website "$website"
done < "$URL_LIST"
```

### Starting and Stopping Traffic Capture
```bash
sudo tcpdump -i eth0 -w "${OUTPUT_DIR}/${domain}_$(date +%Y%m%d_%H%M%S).pcap" &
PID=$!
```
This command starts tcpdump and stores packets in a time-stamped file at a specified output_directory.

### To stop the process
```bash
sudo kill "$PID"
```

### Fetching the Webpage
```bash
curl -s "$website" > /dev/null 2>&1
```
The -s option ensures silent execution, and output is discarded to focus only on traffic analysis. If you wish to...

---

# 4. Debugging and Challenges

## 4.1. Identifying the Correct Network Interface
The script failed intitally as tcpdump was listening on the **wrong interface**