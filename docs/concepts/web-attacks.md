# Web Application Attacks: XSS and SQL Injection

**MITRE ATT&CK:**  
- T1059.007 — Command and Scripting Interpreter: JavaScript (XSS)  
- T1190 — Exploit Public-Facing Application (SQLi initial access)

**OWASP Top 10 (2021):**  
- A03:2021 — Injection (covers SQL injection)  
- A03:2021 — Injection (XSS is now under A03 as well)

---

## Cross-Site Scripting (XSS)

### What is it?

XSS occurs when an application takes untrusted input (from a URL parameter, form field, etc.) and includes it in a web page **without proper encoding**. The browser then executes it as JavaScript.

### Types

| Type | Where payload is stored | Who is affected |
|---|---|---|
| **Reflected** | Not stored — lives in URL/request | User who clicks the crafted link |
| **Stored (Persistent)** | Stored in the database | Every user who views the page |
| **DOM-based** | Manipulates the DOM in the browser | User visiting the page |

### What attackers can do with XSS

- Steal session cookies → hijack authenticated sessions
- Redirect users to phishing pages
- Log keystrokes
- Perform actions on behalf of the victim (CSRF-like)
- Deliver malware via drive-by download (stored XSS)

### Lab example (bWAPP Reflected XSS)

The bWAPP `xss_get.php` page reflects the `firstname` and `lastname` parameters directly into the HTML response without encoding. Payload: `<script>alert('XSS')</script>` appears verbatim in the response.

### Defenses

| Control | Notes |
|---|---|
| **Output encoding** | Encode `<`, `>`, `"`, `'`, `&` when rendering user data in HTML context |
| **Content Security Policy (CSP)** | HTTP header restricting which scripts the browser will execute |
| **HttpOnly cookies** | Prevents JavaScript from reading session cookies via `document.cookie` |
| **Input validation** | Reject unexpected characters early — but encoding is the real fix |
| **Modern frameworks** | React, Angular, Vue auto-encode output by default |

---

## SQL Injection (SQLi)

### What is it?

SQL injection occurs when user-supplied input is incorporated into a database query without parameterization. The attacker can break out of the intended query structure and inject arbitrary SQL.

### Example

Vulnerable code:
```python
query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
```

Payload: `username = ' OR '1'='1`  
Result: `SELECT * FROM users WHERE username = '' OR '1'='1' AND password = '...'`  
→ Returns all rows → authentication bypass.

### Impact levels

| Severity | What's possible |
|---|---|
| **Read** | Dump all data from the database (usernames, passwords, PII) |
| **Write** | Modify or delete records |
| **File access** | Read/write files on the OS (MySQL `LOAD_FILE`, `INTO OUTFILE`) |
| **OS commands** | `xp_cmdshell` (MSSQL), UDF injection (MySQL) → shell on the server |

### Lab (bWAPP)

bWAPP has multiple SQLi labs. The login form is vulnerable with security level set to Low.

### Defenses

| Control | Notes |
|---|---|
| **Parameterized queries / prepared statements** | The only reliable fix — separates code from data |
| **ORM usage** | ORMs use parameterized queries by default (when used correctly) |
| **Least privilege DB user** | App DB account should not have `DROP`, `FILE`, or admin rights |
| **WAF** | Can catch known payloads but bypassable; not a substitute for fixing code |
| **Input validation** | Secondary control — reject digits-only fields containing quotes, etc. |

---

## Lab commands

```bash
# Web attack lesson (XSS via bWAPP)
python labctl.py lesson --track web --run

# Run the bWAPP attack script from the host; it targets
# http://localhost:8080/bWAPP/ on the host, not from inside Kali.
python labctl.py attack-web

# Quiz on web concepts
python labctl.py quiz --track web

# CTF web challenge
python labctl.py ctf --track web --setup
python labctl.py ctf --track web --check <FLAG>
```

## Further reading

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [MITRE T1059.007](https://attack.mitre.org/techniques/T1059/007/)
- [MITRE T1190](https://attack.mitre.org/techniques/T1190/)
- [PortSwigger Web Security Academy](https://portswigger.net/web-security)
