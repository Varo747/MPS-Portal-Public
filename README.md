# MPS Portal – Marine Products Scotland App

**Automated reporting, analysis, and user management for production environments.**

---

## Disclaimer: Demo Data

> **Note:**  
> This project is designed for demonstration purposes only.  
> The example data and generated files **do NOT contain any real confidential information**.

---

## Overview

**MPS Portal** is an all-in-one Python solution for automating production reporting, analysis, and user management.  
It features a modern graphical interface, account and password management, customizable notification preferences, and robust log exporting—tailored for organizations that value efficiency and transparency.

With this app, users can:
- Manage their profile and password securely.
- View interactive charts of their activity.
- Export filtered logs by user and security level.
- Generate and analyze production reports from Excel files.
- Customize UI style and notification settings.

---

## Features

- **Modern GUI** (PyQt6) for all operations.
- **Automated processing** of Excel reports and data analysis.
- **Log export and filtering** by user and security role.
- **Advanced account management:** password change, avatar upload, roles, notifications.
- **Customizable notifications:** email alerts, “remember me”, and more.
- **Visual dashboard:** performance graphs and reporting activity.
- **Support for large Excel files** (using openpyxl and pandas).
- **Multi-level security authentication.**
- **Encryption-ready:** cryptography library for secure data handling.

---

## Typical Use Cases

- Automating production report generation.
- Team or agency performance analysis.
- Access control and user activity auditing.
- Food industry, manufacturing, or logistics teams working with Excel.

---

## Tech Stack

- **Language:** Python 3.10+
- **GUI:** PyQt6
- **Data & Reporting:** pandas, openpyxl
- **Visualization:** matplotlib
- **Encryption/Security:** cryptography
- **Email & Logs:** smtplib, email, csv, json
- **Other:** threading, xlwings (for some advanced Excel calculations)

---

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/Varo747/MPS-Portal-Public.git
   cd MPS-public
