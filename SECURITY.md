# Security Policy

ClinicalTrack is a clean public portfolio edition and contains no production database, institutional branding or real trainee records.

- Production requires a strong SECRET_KEY and DEBUG=0.
- HTTPS, secure cookies, CSRF protection and server-side authorization must stay enabled.
- Supervisors can evaluate only placements assigned to them.
- Trainees can see only evaluations explicitly shared with them.
- Never commit real training records, exports, backups or credentials.
- Use synthetic data for demos and screenshots.

Report vulnerabilities privately through GitHub Security Advisories / Private Vulnerability Reporting when available.
