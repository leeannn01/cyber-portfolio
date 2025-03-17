---
title: "Analyser Module"
date: 2025-03-17 13:00:00 +0800
categories: [Projects]
tags: [Traffic Network Analysis Tool]
permalink: /analyser/
---

# 1. Introduction

The **Analyser Module** (`analyser.py`) module of this PCAP Analysis project is designed to process PCAP files and extract crucial network metadata. The goal is to automate network traffic analysis, allowing for deeper insights into network behavior, device interactions, and potential security threats.

This module focuses on:
- **Packet Dissection** using ***Scapy*** for extracting raw packet data.
- **Protocol Classification** via ***PyShark***, leveraging Wireshark’s dissectors.
- **MAC Address Vendor Identification** using Wireshark’s OUI database.
- **Payload Extraction** to analyze transmitted data for security monitoring.
- **File Extraction** by recognizing file signatures (magic numbers) and reconstructing transmitted files.

The tool’s output is structured into a ***CSV format***, making it suitable for further analysis, visualization, or integration into security monitoring systems.

---

# 2. Design Considerations and Rationale

## 2.1. Selecting the Right Libraries

- **Scapy** was chosen for packet parsing due to its low-level access to network layers.
- **PyShark** was used for protocol classification because of its direct integration with Wireshark’s dissectors.
- **Pandas** was selected to efficiently structure extracted data into a CSV format.

This hybrid approach leveraged **Scapy’s flexibility** while utilizing **PyShark’s deep packet inspection**, providing more accurate protocol detection.

## 2.2. Protocol Classification Challenges

One of the major hurdles was proper protocol classification. PyShark sometimes labeled packets as “DATA” instead of their actual protocol (e.g., QUIC, SMB). To mitigate this:

- Scapy’s Layer Detection was used as a fallback to reclassify some packets.
- Port-Based Heuristics were implemented, mapping well-known ports to their expected protocols.
- PyShark’s highest_layer Attribute was utilized to extract the top-most protocol, ensuring better classification accuracy.

## 2.3. Extracting Downloadable Files

The need for **file reconstruction** was another key feature.

- File extraction was achieved using **magic number detection** to identify PDF, ZIP, JPG, PNG, MP3, and other file types.
- **Reassembled TCP streams** allowed for reconstructing multipart files (e.g., HTTP downloads, SMB file transfers).
- The extracted files were **stored in a separate folder**, ensuring efficient analysis.

## 2.4. MAC Address Vendor Identification

To map MAC addresses to device vendors, the Wireshark OUI database (manuf file) was integrated.

- The tool **parses the OUI file** and **caches vendors** for faster lookup.
- This was chosen over online API lookups, which had rate limits and latency issues.

## 2.5. Efficient Payload Handling

Payloads were stored in a readable format, but large payloads were truncated to prevent Excel overflow when saved to CSV.

---

# 3. Implementation Details

### 3.1. Packet Processing Flow

The module folows this structured flow:
1. **Read PCAP File** → Using rdpcap() from Scapy.
2. **Extract Basic Fields** → Source/Destination IPs, MAC, Ports.
3. **Identify MAC Vendor** → Lookup using Wireshark’s manuf file.
4. **Classify Protocol** → PyShark’s highest_layer field.
5. **Reclassify Protocol if Misidentified** → Using port-based heuristics.
6. **Extract Payload** → Raw data extraction, cleaned and structured.
7. **Reassemble and Extract Files** → Using file signatures (magic numbers).
8. **Store Data** → Save structured CSV output and extracted files.

### 3.2. Protocol Handling via PyShark

- **PyShark’s highest_layer** is used as the primary method for detecting protocols.
- If PyShark labels a packet as **DATA**, fallback logic attempts to reclassify it:
    - Check if Scapy detects a UDP or TCP layer.
	- Check the destination port for well-known services.

#### Code Snippet: Protocol Classification
```python
# Use Pyshark’s protocol classification
protocol = pyshark_protocols.get(frame_number, "Unknown")

# If protocol is DATA, further refine classification:
if protocol == "DATA":
    # If the packet has a UDP layer or a TCP layer with a high ephemeral port, classify as UDP
    if packet.haslayer(UDP) or (packet.haslayer(TCP) and int(packet[TCP].sport) > 49152):
        protocol = "UDP"

    # For TCP packets, use port-based heuristics.
    elif packet.haslayer(TCP):
        tcp_sport = packet[TCP].sport
        tcp_dport = packet[TCP].dport
        if tcp_sport == 80 or tcp_dport == 80:
            protocol = "HTTP"
        elif tcp_sport == 443 or tcp_dport == 443:
            protocol = "HTTPS"
        elif tcp_sport == 25 or tcp_dport == 25:
            protocol = "SMTP"
        elif tcp_sport == 110 or tcp_dport == 110:
            protocol = "POP3"
        elif tcp_sport == 143 or tcp_dport == 143:
            protocol = "IMAP"
        elif tcp_sport == 21 or tcp_dport == 21:
            protocol = "FTP"
        elif tcp_sport == 22 or tcp_dport == 22:
            protocol = "SSH"
        else:
            # If no port-based rule applies, attempt payload analysis for file signatures.
            if packet.haslayer(Raw):
                raw_payload = bytes(packet[Raw].load)
                for signature, (extension, eof_marker) in FILE_SIGNATURES.items():
                    if raw_payload.startswith(signature):
                        protocol = extension.upper()
                        break
    else:
        # For non-TCP/UDP packets, try payload analysis if available.
        if packet.haslayer(Raw):
            raw_payload = bytes(packet[Raw].load)
            for signature, (extension, eof_marker) in FILE_SIGNATURES.items():
                if raw_payload.startswith(signature):
                    protocol = extension.upper()
                    break

packet_info["protocol"] = protocol
detected_protocols.add(protocol)
```
**How This Works**:
1. **Initial Classification (PyShark)**:
- The script first assigns the protocol based on highest_layer from PyShark.

2. **Handling "DATA" Classification**:
- If the protocol is labeled as "DATA":
	- **UDP Check**: If Scapy detects a UDP layer or a TCP connection using a high ephemeral port (above 49152), it is classified as UDP.
	- **Port-Based Heuristic Checks**: If the packet has a well-known service port, it is mapped to the correct protocol (e.g., 80 → HTTP, 443 → HTTPS, etc.).
	- **Payload Inspection for File Signatures**: If no heuristic applies, raw payloads are analyzed against known file magic numbers (e.g., JPEG, PDF, ZIP).

This approach reduced misclassification and improved protocol detection accuracy.

### 3.3. Extracting and Reassembling Files
- File reassembly was performed using ***stream-based extraction***.
- Files were reconstructed from TCP streams using payloads detected in specific packet sequences.

#### Code Snippet: File Extraction
```python
def extract_files_and_payloads(packets, output_folder, pcap_filename):
    """Extracts downloadable files and saves full TCP stream payloads."""
    tcp_streams = defaultdict(bytes)
    extracted_files = 0
    payloads_saved = False
    temp_downloads = {}

    print("\n\033[1mExtracting TCP streams and payloads...\033[0m")

    # Step 1: Reassemble TCP Streams
    for packet in packets:
        if packet.haslayer(IP) and packet.haslayer(TCP) and packet.haslayer(Raw):
            stream_id = (packet[IP].src, packet[IP].dst, packet[TCP].sport, packet[TCP].dport)
            tcp_streams[stream_id] += bytes(packet[Raw].load)

    # Step 2: Save Payload Data (if present)
    payload_file = os.path.join(output_folder, f"payload_{pcap_filename}.txt")
    with open(payload_file, "w", encoding="utf-8", errors="ignore") as f_payload:
        for stream_id, data in tcp_streams.items():
            if data:
                src_ip, dst_ip, sport, dport = stream_id
                f_payload.write(f"\n--- TCP Stream {src_ip}:{sport} -> {dst_ip}:{dport} ---\n")
                f_payload.write(data.decode("utf-8", errors="ignore") + "\n")
                payloads_saved = True

    # Step 3: Search for File Signatures in TCP Streams
    for stream_id, data in tcp_streams.items():
        for signature, (extension, eof_marker) in FILE_SIGNATURES.items():
            start_idx = data.find(signature)
            if start_idx != -1:
                extracted_files += 1
                file_id = f"file_{extracted_files}.{extension}"
                temp_downloads[file_id] = data[start_idx:] if eof_marker is None else data[start_idx:data.find(eof_marker) + len(eof_marker)]
```

- The output directory was structured as:
```markdown
/output_folder/
  ├── extracted_files/
  ├── payloads/
  ├── analysis_report.csv
```

# 4. Debugging and Challenges

## 4.1. Protocol Misclassification

**Issue**: PyShark classified many UDP packets as “DATA”.

**Fix**: Implemented port-based and heuristic-based detection to reclassify protocols.

## 4.2. MAC Address Vendor Lookup Failures

**Issue**: Some MAC addresses still showed “Unknown”.

**Fix**: The Wireshark manuf file path was corrected and loaded at runtime.
```python
def get_mac_vendor(mac_address):
    """Get vendor name for a MAC address using the Wireshark OUI database."""
    mac_prefix = mac_address[:8].lower()  # Extract first 3 bytes (OUI)
    return MAC_MANUFACTURERS.get(mac_prefix, "Unknown Device")
```

## 4.3. File Extraction Issues

**Issue**: Some extracted files were incomplete.

**Fix**: Implemented stream tracking to ensure all TCP segments were correctly reassembled.

## 4.4. Large Payloads Causing CSV Overflow
**Issue**: Large payloads broke CSV formatting in Excel.

**Fix**: Payloads were truncated to 100 characters for readability.
```python
def clean_payload(raw_payload):
    """Ensures payloads are readable and properly formatted for CSV storage."""
    if raw_payload is None:
        return ""

    try:
        decoded_payload = raw_payload.decode('utf-8', errors='ignore')
        return decoded_payload.strip()[:100]  # Limit to 100 chars to prevent Excel overflow
    except Exception:
        return binascii.hexlify(raw_payload).decode()[:100]  # Return hex if decoding fails
```

# 5. Deployment Considerations

To ensure smooth setup and execution, the following dependencies and system configurations are required:

## 5.1. System Requirements
- Python 3.8+
- **Scapy** (`pip install scapy`)
- **PyShark** (`pip install pyshark`)
- **TShark** (Wireshark CLI Tool) → Required for PyShark to function properly.

## 5.2. Setting Up the Environment

A Bash setup script can be used for automatic installation:
#### For Linux/MacOS:
```bash
#!/bin/bash
echo "Installing dependencies..."
sudo apt install -y tshark      # Linux
brew install tshark             # MacOS
pip install scapy pyshark pandas
echo "Setup Complete!"
```
#### For Windows:
```bash
choco install wireshark
pip install scapy pyshark pandas
```

## 5.3. Running the Analysis
```bash
python3 analyzer.py input.pcap output_folder/
```

## 5.4. Expected Output

The analyser produces:
1. **CSV file (pcap.csv)** - List all packets.
2. **Payload (payload.txt)** - Combined Payload text file
3. **Extracted Files (if any)** - Extracted downloadable files

# 6. Conclusion and Next Steps

## 6.1. Key Takeaways
The Analyser Module has successfully combined Scapy and PyShark to create an efficient and accurate PCAP analysis tool. The module can:
- Extract network metadata (IP, MAC, ports, protocols).
- Classify protocols more accurately.
- Extract and reassemble files.
- Identify MAC vendors efficiently.

## Future Improvements
- Enhancing Protocol Detection
- Expanding the port-based classification database.
- Implementing Machine Learning models for anomaly detection.
- Performance Optimization
- Processing large PCAP files more efficiently using parallelism.
- Reducing Scapy memory overhead.
- Real-Time Network Analysis
- Expanding this tool into live packet capture mode for intrusion detection.
- Create a bash script (`setup_analyser.sh`) for easy setup



# Appendix: Full Python Script

For full implementation details, visit the [GitHub Repository](https://github.com/leeannn01/leeannn01.github.io/blob/main/projects/network-traffic-analysis-tool/src/analyser.py)