---
title: "Live Capture Script"
date: 2025-03-17 10:00:00 +0800
categories: [Projects]
tags: [Traffic Network Analysis Tool]
permalink: /live-capture-script/
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

To capture live network traffic, I opted for ```tcpdump``` due to its efficiency, lightweight footprint, and ability to filter and store packet data in .pcap format for offline analysis.

### What does tcpdump capture do?
tcpdump is a packet analyzer that captures network traffic at a low level. It logs:
•	Source and Destination IPs of packets
•	Transport Layer Information (e.g., TCP, UDP, ICMP)
•	Port Numbers (e.g., HTTP uses port 80, HTTPS uses port 443)
•	Packet Headers and Payloads (unless filtered)

#### a. Example capture command:
```bash
sudo tcpdump -i eth0 -w capture.pcap
```
This captures all network packets on eth0 and saves them in .pcap format for later analysis in Wireshark.

#### b. Filtering Example
```bash
sudo tcpdump -i eth0 port 80 or port 443 -w web_traffic.pcap
```
This captures only HTTP and HTTPS traffic

### Alternative Considered:
- Wireshark/tshark: More powerful but resource-intensive for automated scripts.
- PyShark: Python-based, better for analysis but less suited for Bash automation.

### Final Decision
TCPDump was chosen for its native Linux support, ease of automation, and compatibility with Python-based analysis.

## 2.2. Selecting a Web Scraper: curl vs. wget

### Curl

``curl`` is a command-line tool for making HTTP/HTTPS requests. It fetches webpage content and can also:
- Handle authentication (-u: user:pass)
- save files (-o output.html)
- Follow redirect (-L)
- Set an user-agent(-A "Mozilla/5.0")

#### What happens when running curl <URL>?
- ``curl`` sends an HTTP GET request to the server.
- The server responds with the webpage's HTML source code.
- This HTML is not rendered (unlike a browser) but can be saved or anlaysed

### wget
Since the tool required fetching website contents while capturing traffic, I compared curl and wget:

| Feature                      | curl | wget |
|------------------------------|------|------|
| Flexibility                  | ✅   | ❌   |
| Handles redirects            | ✅   | ✅   |
| Supports concurrent downloads | ❌   | ✅   |
| CLI integration              | ✅   | ✅   |

### Final Decision:
``curl`` was selected due to its flexibility and ability to integrate seamlessly into the script.

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

- **Solution**:Use the following command to list interfaces amd found the correct one (en0 instead of eth0)
```bash
# For Linux
ip a

# For MacOS
ifconfig

# For WindowsOS
ipconfig
```

---

# 5. Deployment Considerations

## 5.1. Setting up the Envionmnent

### a. Install Dependencies
```bash
sudo apt install tcpdump curl
```

### b. Ensure Execution Permission
```bash
chmod +x ./capture_traffic.sh
```

## 5.2. Running the script
```bash
sudo ./capture_traffic.sh
```
- sudo is required for tcpdump to access network interface

## 5.3. Output and Storage
- .pcap files are saved in captured_pcaps/
- Example file format:
```shell
example.com_20250317_120000.pcap
```

---

# 6. Conclusion & Next Steps

## 6.1. Key Takeaways
- TCPDump & Curl Integration: Efficient for real-time network capture during web scraping.
- Automated Capture Process: Reduces manual intervention

## 6.2. Future Enhancements
- Multi-threading: Capture multiple website concurrently.
- Machine Learnning-Based Anomaly Detection: Apply AI models to flag suspicious.
- Threat Intelligence Integration: Compare capture traffic with known malicious indicators.

This Bash script is a powerful yet lightweight solution for automated web traffic analysis, making it an essential tool for networks security investigations.

# Appendix: Full Bash Script

For full implementation details, visit the [GitHub Repository](https://github.com/leeannn01/cyber-portfolio/blob/main/projects/network-traffic-analysis-tool/scripts/capture_traffic.sh)

