---
title: "OSWAP_A02: Cryptographic Failure"
date: 2025-03-20 11:00:00 +0800
categories: [Research]
tags: [OSWAP]
permalink: /oswap-cryptographic-failure/
---

# About
Cryptographic failures (formerly known as Sensitive Data Exposure) refer to vulnerabilities arising from inadequate encryption practices, including data transmitted without encryption, weak algorithms, improper key management, and plaintext storage. These failures lead to the loss of confidentiality and integrity, exposing sensitive information such as credentials, personal data, and financial records to unauthorized access.

# Common Attack Vectors
Attackers exploit cryptographic failures primarily through:
- Eavesdropping on unencrypted network traffic (Man-in-the-Middle attacks).
- Cracking weak cryptographic hashes (e.g., MD5, SHA-1) to retrieve passwords.
- Stealing sensitive data from unencrypted backups or logs.
- Exploiting leaked or hard-coded cryptographic keys in applications.
- Accessing sensitive information accidentally exposed in plaintext responses or server logs.

# Real-world Case Studies
### Yahoo Data Breach (2013)
The Yahoo breach affected all 3 billion accounts due to the use of weak MD5 hashing algorithms, which allowed attackers to easily crack user passwords. This became one of the largest breaches in history, emphasizing the dangers of relying on outdated cryptographic practices.

### TalkTalk Data Breach (2015)
TalkTalk suffered a breach through SQL injection but faced further consequences due to storing sensitive customer data without proper encryption. Attackers directly accessed and exploited unencrypted personal and banking information.

# Mitigation Strategies
1. Identify and Classify Sensitive Data: Determine which data is sensitive (personal details, financial data) and protect it accordingly.
2. Use Strong Encryption: Ensure robust encryption standards (AES-256, TLS 1.2+) for both data in transit and at rest. Use salted hashing algorithms (bcrypt, Argon2) for passwords.
3. Proper Key Management: Securely store cryptographic keys, avoid hard-coding, and regularly rotate keys. Utilize hardware security modules (HSMs) or key management services.
4. Disable Weak Cryptographic Defaults: Disable deprecated protocols (SSLv3, TLS 1.0) and insecure ciphers. Implement security headers such as HTTP Strict Transport Security (HSTS).
5. Avoid Cryptographic Misconfigurations: Use secure random number generators and ensure sensitive information is not cached or logged inadvertently.
6. Adhere to Security Standards and Regulations: Comply with frameworks such as PCI-DSS for payment data or GDPR for personal data protection.

# References and Resources
- OWASP Cryptographic Failures: https://owasp.org/www-project-top-ten/A02_2021-Cryptographic_Failures/
- Yahoo Data Breach Analysis: https://www.theguardian.com/technology/2016/dec/14/yahoo-hack-security-of-personal-information
- TalkTalk Breach Report: https://www.bbc.com/news/technology-34743185
