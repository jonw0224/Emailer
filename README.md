A self‑hosted command‑line tool to schedule email campaigns using any SMTP‑compatible server.

---  

### ✅ Purpose
This Python script (`emailer.py`) schedules and sends emails to recipient lists via a campaign file. It works with any SMTP server that supports password authentication, making it ideal for self‑managed email marketing without third‑party services.

---

### 🚀 Usage

```bash
# Run the default configuration (smtp.conf + email_campaigns.csv)
python3 emailer.py
```

```bash
# Show help/available arguments
python3 emailer.py --help
```

```bash
# Use custom files for SMTP and campaign data
python3 emailer.py \
    --conf smtpUserSpecified.conf \
    --campaign email_campaignsUserSpecified.csv
```

**Key options**

| Option          | Description                                                    |
|-----------------|----------------------------------------------------------------|
| `--help`        | Display usage information.                                     |
| `--conf <file>` | Path to the SMTP configuration file (default: *smtp.conf*).   |
| `--campaign <file>` | Path to the email campaign CSV (default: *email_campaigns.csv*). |

---

### 📅 Cron Scheduling  

Schedule daily runs with **cron**:

```bash
# Edit your crontab
crontab -e

# Add a line – example runs at 6 AM every day, logging output to emailer.log
0 6 * * * python3 /path/to/script/emailer.py \
    --conf smtpUserSpecified.conf \
    --campaign email_campaignsUserSpecified.csv > /path/to/script/emailer.log
```

*Adjust the paths and timing as needed.*

---

### 🔧 SMTP Setup  

Configuration lives in `smtp.conf` (or any similarly named file).  
**Important notes**

- The script supports **only password‑based authentication**.
- For services like Google Gmail, generate an **Application Password** to enable SMTP connections.

```ini
[SMTP]
host = smtp.gmail.com
port = 587
user = your_email@gmail.com
password = YOUR_APP_PASSWORD
```

Refer to the comments inside `smtp.conf` for a full list of supported fields.

---

### 📄 Email Templates  

The script sends **HTML** emails.  
Template files (e.g., `test.html`) can contain placeholders:

```html
<p>Hello {{FirstName}},</p>
<p>Thank you for your interest in {{ProductName}}.</p>
```

Placeholders (`{{fieldname}}`) are replaced by values from either the recipient CSV (e.g. 'audience.csv') or campaign CSV (e.g. 'email_campaigns.csv').

**Email Template example (`test.html`)**

---

### 👥 Recipient Lists  

The recipient list must be a **CSV** with at least these columns:

| Column      | Required? |
|-------------|------------|
| FirstName   | Yes        |
| LastName    | Yes        |
| Email       | Yes        |

Additional custom fields (e.g., `Phone`, `SubscriptionType`) can be added and referenced in templates or subject lines.

**Recipient list CSV example (`audience.csv`)**

```csv
FirstName,LastName,Email,Phone
Alice,Austin,a@example.com,555‑1234
Bob,Brown,b@example.com,
```

---

### 📨 Email Campaigns  

Campaign data lives in a **CSV** where each row defines when and how an email is sent.

| Column          | Description                                                  |
|-----------------|--------------------------------------------------------------|
| Date            | YYYY-MM-DD – the day the email should be dispatched.       |
| Subject         | Email subject line (supports `{{field}}` placeholders).     |
| EmailList       | Path to the recipient CSV file.                             |
| Body            | Path to the HTML template file.                            |

**CSV example (`email_campaigns.csv`)**

```csv
Date,Subject,EmailList,Template
2025-04-15,"Welcome {{FirstName}}!",recipients.csv,test.html
2025-05-01,"Monthly Newsletter",recipients.csv,newsletter.html
```

The `Subject` line can reference recipient fields (e.g., `{{FirstName}}`) for personalization.

---

### 📜 License  

**MIT License**

Copyright (c) 2026 Jonathan Weaver  

You may freely modify, distribute, and use this script under the terms of the MIT license.

---  


