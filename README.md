# Cybersecurity Portfolio
Portfolio showcasing cybersecurity projects, insights, and learnings

## Table of Contents  
- [About This Portfolio](#about-this-portfolio)  
- [Portfolio Structure](#portfolio-structure)
- [Projects](#projects)  
- [Blog](#blog)  
- [Installation & Setup](#installation--setup)  
- [Skills & Technologies Used](#skills--technologies-used)  

## About This Portfolio  
This portfolio contains my cybersecurity-related projects, including:  
- **Network Traffic Analysis Toolkit** – A Python & Bash toolset for capturing, analyzing, detecting, and visualizing network traffic anomalies.  
- **Security Research & Learning Notes** – Research articles and documentation on cybersecurity techniques, threat intelligence, and system vulnerabilities.  

These projects demonstrate my ability to work with **packet analysis (PCAPs), network monitoring, security scripting, and automated threat detection.**  

## Portfolio Structure
```
cybersecurity-portfolio/
├── _config.yml                             # Site settings
├── index.md                                # Homepage
|
├── posts/                                  # Blog posts 
│   ├── 2025-03-12-example.md
│   └── 2025-03-10-pcap-analysis.md
|
├── _tabs/                                  # Chirpy blog navigation tabs
│   ├── about.md                            # About me
│   ├── categories.md                       # Blog categories
│   ├── tags.md                             # Blog tags
│   └── archives.md                         # Archives page
|
├── .github/                                # GitHub Actions for Jekyll deployment
│   ├── workflows/                          # Automated CI/CD build system
│
├── projects/                               # Project details
│   └── network-traffic-analysis-tool/  
│       ├── README.md                       # Project write-up
│       ├── src/                            # Python scripts for processing
|       ├── scripts/                        # Bash scripts 
|       ├── docs/                           # Documentation and reports
|       ├── data/                           # Folder (PCAP files - from both web scrapping/downloaded)
|       └── results/                        # All analysed results saved within 
|           └── pcap1
|               ├── downloads_pcap1/        # Downlable content within payload saved within 
|               ├── payload_pcap1.txt       # Payload extracted
|               ├── pcap1.csv               # Packet Data extracted
|               ├── Malicious Traffic/      # Results from Detector saved within (a csv and text summary)
|               └── Visuals/                # Results from Visualiser
├── .gitignore                              # Files to ignore in Git
├── Gemfile                                 # Jekyll dependencies
├── LICENSE                                 # Project license
└── README.md                               # Portfolio overview
```

## Projects  
### **Network Traffic Analysis Toolkit**  
**Description:**  
A set of Python and Bash scripts for **capturing, analyzing, detecting, and visualizing** network traffic patterns and security threats from PCAP files.  

**Key Features:**  
- Capture real-time network traffic using `tcpdump`.  
- Analyze `.pcap` files to extract insights.  
- Detect suspicious patterns using Python-based anomaly detection.  
- Visualize results using Matplotlib and Pandas.  

**[View My Projects](./projects/network-traffic-analysis-tool/)** 

## Blog 
**Description**
This portfolio leveraged on a chirpy-starter template to generate the blog. 


### Usage and Installation
**How to add a New Blog Post**
1. Navigate to _/posts directory
2. Create a new Markdown file using the format:
```YYYY-MM-DD-title-of-post.md```
3. Add the required Front Matter at the beginning of the file:

```
---
title: "Your Blog Post Title"
date: YYYY-MM-DD HH:MM:SS +/-TTTT
categories: [Cybersecurity, Network Security]
tags: [Threat Detection, PCAP Analysis]
---
```
4. Commit and push changes -- your new post will appear after deployment
```bash
git add .
git commit -m "message"
git push origin main
```
  
**[Read My Blog](./_post/)**  

## **Installation & Setup:** 
This portfolio is built using Markdown and GitHub Pages (using chirpy template)

### To view the portfolio locally:
1. Clone the Repository
```bash
git clone https://github.com/leeannn01/cyber-portfolio.git
cd cybersecurity-portfolio
```

2. Run Locally with Jekyll
```bash
bundle install
bundle exec jekyll serve --livereload
```

## Skills & Technologies Used  
- **Programming & Scripting:** Python, Bash, PowerShell  
- **Networking & Security:** Wireshark, Tcpdump, Scapy, pyshark
- **Data Analysis & Visualization:** Pandas, Matplotlib 
- **Web Technologies** Jekyll, GitHub Pages, Chirpy Theme
  
