# CPTS SysReptor Finding Templates

46 pre-built finding templates for the **HTB Certified Penetration Testing Specialist (CPTS)** exam report. Designed for use with [SysReptor](https://github.com/syslifters/sysreptor) and the HTB CPTS Report v1.1 project type.

Each template includes a filled-out title, CVSS 3.1 vector, summary, technical description, impact statement, remediation steps, CWE references, and placeholder format for affected components.

## Template Breakdown

| Severity | Count | CVSS Range |
|----------|-------|------------|
| Critical | 11 | 9.0 - 10.0 |
| High | 23 | 7.0 - 8.9 |
| Medium | 12 | 4.0 - 6.9 |
| Low | 1 | 0.1 - 3.9 |

### Categories

- **Web Application (16):** SQLi, LFI/RFI, Command Injection, File Upload, SSRF, XXE, XSS, IDOR, CSRF, Broken Access Control, Default Web Creds, Exposed Files, Insecure Cookies, URL Param Disclosure, HTTP Headers, User Enumeration
- **Active Directory (17):** Password Spraying, Weak AD Password Policy, Kerberoasting, AS-REP Roasting, DCSync, Pass-the-Hash/Pass-the-Ticket, Kerberos Delegation, ADCS (ESC), Excessive AD Permissions, GPP Credentials, Cleartext Creds, LLMNR/NBT-NS Poisoning, SMB Signing, Domain Trust Exploitation, Credential Extraction, Sensitive Info in AD Attributes, Anonymous Enumeration
- **Privilege Escalation (3):** Windows Service Misconfig, Sudo Misconfig, Impersonation Privileges (SeImpersonate/SeAssignPrimaryToken)
- **Infrastructure (5):** Unsupported OS, Missing Patches, Network Segmentation, Insecure Protocols, Insufficient Logging
- **Credentials (2):** Default/Weak Service Creds, Local Admin Password Reuse
- **Other (3):** Untrusted TLS, Session Management, File Share Permissions

## How to Import

### Option 1: Python Script (Recommended)

```bash
pip install requests
python import.py --url http://localhost:8000 --user reptor --password YOUR_PASSWORD
```

Preview before importing:

```bash
python import.py --url http://localhost:8000 --user reptor --password YOUR_PASSWORD --dry-run
```

Import a single template:

```bash
python import.py --url http://localhost:8000 --user reptor --password YOUR_PASSWORD --file templates/sql-njection-sqli.json
```

### Option 2: PowerShell (Windows)

```powershell
$base = "http://localhost:8000"
$login = Invoke-RestMethod -Uri "$base/api/v1/auth/login/" -Method POST `
    -ContentType "application/json" `
    -Body '{"username":"reptor","password":"YOUR_PASSWORD"}' `
    -SessionVariable session

$csrf = $session.Cookies.GetCookies("http://localhost:8000") | Where-Object { $_.Name -eq "csrftoken" } | Select-Object -ExpandProperty Value
$headers = @{ "X-CSRFToken" = $csrf; "Referer" = $base }

Get-ChildItem .\templates\*.json | ForEach-Object {
    $data = Get-Content $_.FullName -Raw | ConvertFrom-Json
    $payload = @{
        translations = @(@{
            language = $data.translations[0].language
            is_main = $true
            status = "finished"
            data = $data.translations[0].data
        })
        tags = $data.tags
    } | ConvertTo-Json -Depth 20

    $result = Invoke-RestMethod -Uri "$base/api/v1/findingtemplates/" -Method POST `
        -ContentType "application/json" -Body $payload `
        -WebSession $session -Headers $headers
    Write-Host "Imported: $($data.translations[0].data.title)"
}
```

### Option 3: curl (Linux/Mac)

```bash
# Login and get session cookie
curl -s -c cookies.txt -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"reptor","password":"YOUR_PASSWORD"}'

CSRF=$(grep csrftoken cookies.txt | awk '{print $NF}')

# Import each template
for f in templates/*.json; do
  TITLE=$(python3 -c "import json; print(json.load(open('$f'))['translations'][0]['data']['title'])")
  
  # Build minimal payload from the template file
  python3 -c "
import json
t = json.load(open('$f'))
payload = {
    'translations': [{'language': t['translations'][0].get('language','en-US'), 'is_main': True, 'status': 'finished', 'data': t['translations'][0]['data']}],
    'tags': t.get('tags', [])
}
print(json.dumps(payload))
" | curl -s -b cookies.txt -X POST http://localhost:8000/api/v1/findingtemplates/ \
    -H "Content-Type: application/json" \
    -H "X-CSRFToken: $CSRF" \
    -H "Referer: http://localhost:8000" \
    -d @-
  
  echo " -> $TITLE"
done
```

## File Structure

```
cpts-sysreptor-templates/
  README.md              # This file
  import.py              # Python import script
  manifest.json          # Template index (title, file, tags)
  all-templates.json     # All 46 templates in one file
  templates/             # Individual template JSON files
    sql-njection-sqli.json
    kerberoasting-service-accounts-with-weak-passwords.json
    dcsync-replication-of-domain-credentials.json
    ...
```

## Notes

- Templates are exported from SysReptor v2026.75. They should work with any recent SysReptor version.
- The import script creates new templates. It does not check for duplicates. If you run it twice, you'll get duplicate templates.
- CVSS scores are calculated from the CVSS 3.1 vector string by SysReptor, not from the `risk_score` field.
- Each template has `<PLACEHOLDER>` values in the `affected_components` field. Replace these with real data during the exam.
- The `description` field contains full technical detail with tool commands and exploitation steps.
- Designed for use with the HTB CPTS Report v1.1 project type.

## Usage During CPTS Exam

1. Set up SysReptor with the HTB CPTS Report v1.1 project type
2. Import these templates
3. For each vulnerability found during the exam:
   - Go to your project -> Findings -> Create from template
   - Select the matching template
   - Replace all `<PLACEHOLDER>` values with your actual data
   - Add screenshots
   - Adjust CVSS if needed for your specific scenario
4. Write the attack chain walkthrough separately in the project sections
5. Fill the appendix tables (flags, compromised hosts, users)
