---
title: "OSWAP_A01: Broken Access Control "
date: 2025-03-19 11:00:00 +0800
categories: [Research]
tags: [OSWAP]
permalink: /oswap-broken-access-control/
---

# About:
Broken Access Control occurs when an application does not properly enforce who can do what, allowing attackers to act beyond their intended permissions. This can mean regular users gaining admin-level actions or accessing other users’ data. The impact is severe: attackers may view or modify sensitive information or perform unauthorized operations, essentially impersonating other users or administrators.

# Common attack vectors: 

Common exploits of Broken Access Control include:

- **Insecure Direct Object References (IDOR)**: Attackers manipulate URLs or parameters to access unauthorized resources.
- **Privilege Escalation**: Users bypass or tamper with session management or JSON Web Tokens (JWT) to gain higher privileges.
- **Forced Browsing**: Users directly access hidden or unlinked URLs that lack proper authorization checks.
According to OWASP, approximately 94% of tested applications exhibit some form of Broken Access Control, highlighting the widespread and serious nature of this vulnerability.


# Real-world example: 

### First American Financial Corp (2019)
In 2019, a major vulnerability exposed approximately 885 million financial documents due to an Insecure Direct Object Reference (IDOR). By simply altering document IDs in URLs, attackers could access sensitive records without authentication. This incident underscores the potential severity of inadequate access controls.

### Facebook–Cambridge Analytica Scandal (2018)
An overly permissive API on Facebook’s platform allowed a third-party application to harvest millions of users' data without explicit consent. This Broken Access Control facilitated unauthorized data extraction, influencing significant public backlash and privacy concerns.

# Mitigation strategies:

1. **Enforce least privilege**
Deny access by default and ensure each API endpoint or function checks user roles/permissions on every request . Users should only have access to the resources and actions explicitly granted.

2. **Implement and reuse robust access control mechanisms**
Centralize the authorization logic and use well-tested frameworks for session management and access control rules. This reduces the chance of a forgotten check on some path.

3. **Prevent IDOR by reference mapping**: Avoid exposing database keys or predictable identifiers in URLs. Instead, use opaque references or GUIDs and always verify the current user’s privilege for the requested object.

4. **Conduct thorough testing and code reviews**: Use automated testing or security scripting to simulate unauthorized access attempts (e.g., changing IDs, elevating roles) and ensure the system properly denies them. Regular penetration testing can catch access control lapses before attackers do.

5. **Log and monitor access control failures**: Alert on unusual activity, such as a single account attempting to access many records in sequence, which might indicate IDOR exploitation. This ties into threat detection: monitoring network and application logs can expose an attacker probing for access control weaknesses.

## References and Resources
- OWASP Broken Access Control: https://owasp.org/www-project-top-ten/A01_2021-Broken_Access_Control/
- First American Financial Data Breach (SEC Report): https://www.sec.gov/news/press-release/2021-102
- Facebook–Cambridge Analytica Data Scandal Explained: https://www.theguardian.com/news/series/cambridge-analytica-files
