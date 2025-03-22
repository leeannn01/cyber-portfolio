"""
- Hybrid AI (Rule-Based + Bayesian) → Detects both known and unknown threats.
- Kalman Filtering → Reduces false positives and smooths anomaly detection.
- Adaptive Thresholding (Modular Option) → Dynamically adjusts sensitivity.
- Contextual Awareness (Modular Option) → Adds risk scoring for better threat intelligence.
- Highly Modular → Simply enable/disable Adaptive Thresholding & Contextual Awareness as needed.

✔ Performance Optimized → Works in real-time for live network analysis
✔ Explainable AI (XAI) → Provides human-readable risk scores and justification

- suspicious_reason != "Normal" → Your trigger for rule-based detections
- is_anomaly == True → Your AI model decision
- visualize both, and especially highlight overlap (AND condition) or divergence (XOR conditions).
"""
import os
import sys
import pandas as pd
import ipaddress
import numpy as np
from collections import defaultdict
from scipy.stats import norm

# === Kalman Filter Class ===
class KalmanFilter:
    """Kalman Filter for Weighted Anomaly Score Refinement"""
    def __init__(self, initial_estimate=0.1, process_variance=1e-4, measurement_variance=1e-1):
        self.estimate = initial_estimate
        self.variance = process_variance
        self.measurement_variance = measurement_variance

    def update(self, measurement):
        """Apply Kalman update step"""
        kalman_gain = self.variance / (self.variance + self.measurement_variance)
        self.estimate = self.estimate + kalman_gain * (measurement - self.estimate)
        self.variance = (1 - kalman_gain) * self.variance
        return self.estimate

# === AI Detector Class ===
class AIDetector:
    """
    AI-Based Hybrid Threat Detection System
    - Rule-Based Detection (Known Threats: SYN Flood, Loopback Anomalies)
    - Bayesian Anomaly Scoring (Unknown Threats)
    - Adaptive Learning (Dynamic Threshold Adjustments)
    """

    # Known Threat Signatures (Prior Knowledge)
    SUSPICIOUS_PORTS = {21, 22, 23, 53, 80, 443, 445, 1433, 1521, 3306, 3389}
    LARGE_PACKET_SIZE = 1500  # Suspicious packet threshold
    SUSPICIOUS_KEYWORDS = ["cmd.exe", "powershell", "wget", "curl", "/bin/sh", "/bin/bash"]
    
    INTERNAL_NETWORKS = [
        ipaddress.ip_network("10.0.0.0/8"),
        ipaddress.ip_network("172.16.0.0/12"),
        ipaddress.ip_network("192.168.0.0/16")
    ]

    def __init__(self, use_adaptive_threshold=False):
        """Initialize AI Detector with Rule-Based + Bayesian AI"""
        self.normal_traffic_mean = 500
        self.normal_traffic_std = 100
        self.syn_packet_count = defaultdict(int)    # Track SYN flood per source
        self.kalman_filter = KalmanFilter()         # Kalman filter
        self.use_adaptive_threshold = use_adaptive_threshold         # Disabled Adaptivtive thresholding (optional)
        self.previous_anomaly_scores = []  # Used for adaptive thresholding

        # self.use_contextual_awareness = False       # Disabled contextual awareness (optional)
        # self.known_malicious_ips = set()   # Used for contextual awareness

    def is_internal_ip(self, ip):
        """Check if an IP belongs to an internal network."""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return any(ip_obj in net for net in self.INTERNAL_NETWORKS)
        except ValueError:
            return False

    def contains_suspicious_payload(self, payload):
        """Check if payload contains suspicious commands."""
        if pd.isna(payload):
            return False
        payload_lower = str(payload).lower()
        return any(keyword in payload_lower for keyword in self.SUSPICIOUS_KEYWORDS)

    def detect_known_threats(self, packet):
        """Apply Rule-Based Threat Detection, including SYN Flood & Loopback Traffic"""
        threat_reason = []

        # Port Checks (Safe conversion)
        try:
            sport = int(float(packet.get("sport", -1)))
            dport = int(float(packet.get("dport", -1)))
            if sport in self.SUSPICIOUS_PORTS:
                threat_reason.append("Suspicious Source Port")
            if dport in self.SUSPICIOUS_PORTS:
                threat_reason.append("Suspicious Destination Port")
        except (ValueError, TypeError):
            pass  # Invalid or missing port values

        # Large Packet Size (Possible Data Exfiltration)
        if packet["length"] > self.LARGE_PACKET_SIZE:
            threat_reason.append("Large Packet Size (Possible Data Exfiltration)")

        # Suspicious Payload
        if self.contains_suspicious_payload(packet.get("payload", "")):
            threat_reason.append("Suspicious Payload Detected")

        # Unusual Outbound Connection (Internal → External)
        if self.is_internal_ip(packet["source"]) and not self.is_internal_ip(packet["destination"]):
            threat_reason.append("Unusual Outbound Connection")

        # SYN Flood Detection (Too many SYN packets from one source)
        if "flags" in packet and packet["flags"] == "SYN":
            self.syn_packet_count[packet["source"]] += 1
            if self.syn_packet_count[packet["source"]] > 100:
                threat_reason.append(f"SYN Flood Attack Detected from {packet['source']}")

        # Loopback Traffic Anomaly (Source == Destination)
        if packet["source"] == packet["destination"]:
            threat_reason.append("Loopback Traffic Anomaly Detected")

        return "; ".join(threat_reason) if threat_reason else "Normal"

    def compute_anomaly_score(self, packet_size):
        """Compute Bayesian Probability for Anomalous Traffic."""
        normal_traffic = norm(loc=self.normal_traffic_mean, scale=self.normal_traffic_std)
        suspicious_traffic = norm(loc=2000, scale=500)
        
        p_normal = normal_traffic.pdf(packet_size)
        p_suspicious = suspicious_traffic.pdf(packet_size)
        
        raw_anomaly_score = p_suspicious / (p_suspicious + p_normal)
        refined_anomaly_score = self.kalman_filter.update(raw_anomaly_score)

        return refined_anomaly_score
    
    def compute_dynamic_threshold(self):
        """Compute Adaptive Thresholding for Anomaly Detection"""
        if len(self.previous_anomaly_scores) < 10:
            return 0.7  # Default threshold

        threshold_mean = np.mean(self.previous_anomaly_scores)
        threshold_std = np.std(self.previous_anomaly_scores)
        return threshold_mean + (1.5 * threshold_std)  
      
    # def update_threshold(self, new_packet_size):
    #     """Adaptively update the normal packet size threshold."""
    #     self.normal_traffic_mean = (self.normal_traffic_mean + new_packet_size) / 2
    #     self.normal_traffic_std = np.std([self.normal_traffic_mean, new_packet_size])

    def detect_malicious_traffic(self, input_csv, output_folder):
        """Process CSV file, detect threats, and save results."""

        with open(input_csv, "r", encoding="utf-8", errors="replace") as file:
            df = pd.read_csv(file, engine="python", on_bad_lines="skip")

        if "payload" not in df.columns:
            df["payload"] = ""

        df["length"] = pd.to_numeric(df["length"], errors="coerce").fillna(0).astype(int)

        # Apply Hybrid AI Detection
        df["suspicious_reason"] = df.apply(self.detect_known_threats, axis=1)
        df["anomaly_score"] = df["length"].apply(self.compute_anomaly_score)
        
        # Mean adjustment
        # df["adaptive_threshold"] = df["length"].apply(self.update_threshold)
        # df["is_anomaly"] = df["anomaly_score"] > 0.7  # Flag anomalies with high probability

        # Adaptive Threshold
        if self.use_adaptive_threshold:
            self.previous_anomaly_scores.extend(df["anomaly_score"].tolist())
            dynamic_threshold = self.compute_dynamic_threshold()
            df["is_anomaly"] = df["anomaly_score"] > dynamic_threshold
        else:
            df["is_anomaly"] = df["anomaly_score"] > 0.7

        # Save results
        results_folder = os.path.join(output_folder, "Malicious_Traffic_Detected")
        os.makedirs(results_folder, exist_ok=True)

        pcap_filename = os.path.splitext(os.path.basename(input_csv))[0].replace("packet_data_", "")
        output_csv = os.path.join(results_folder, f"malicious_traffic_{pcap_filename}.csv")

        df.to_csv(output_csv, index=False)
        print(f"✅ AI Detector Analysis Complete. Results saved to {output_csv}")

### === MAIN EXECUTION === ###
def main():
    if len(sys.argv) != 3:
        print("Usage: python3 ai_detector.py <input_csv> <output_folder>")
        sys.exit(1)

    input_csv = sys.argv[1]
    output_folder = sys.argv[2]
    
    detector = AIDetector()
    detector.detect_malicious_traffic(input_csv, output_folder)
    
if __name__ == "__main__":
    main()