"""
Security Audit Script
Comprehensive security analysis for YouTube Bot Video Extractor

Checks:
1. OAuth token storage security
2. API key protection
3. Input validation (file paths, URLs)
4. SQL injection prevention
5. HTTPS-only API calls
6. Hardcoded secrets detection
7. Dependency vulnerabilities
8. File permission security
"""

import os
import re
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class SecurityAuditor:
    """Performs comprehensive security audit"""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.findings: List[Dict[str, Any]] = []
        self.severity_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0, 'INFO': 0}
        
    def add_finding(self, category: str, severity: str, title: str, 
                    description: str, file_path: str = None, line: int = None,
                    recommendation: str = None):
        """Add a security finding"""
        finding = {
            'category': category,
            'severity': severity,
            'title': title,
            'description': description,
            'file': file_path,
            'line': line,
            'recommendation': recommendation,
            'timestamp': datetime.now().isoformat()
        }
        self.findings.append(finding)
        self.severity_counts[severity] += 1
        
    def scan_hardcoded_secrets(self):
        """Scan for hardcoded secrets, API keys, passwords"""
        print("\n[1/8] Scanning for hardcoded secrets...")
        
        # Patterns for common secrets
        patterns = {
            'api_key': r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']{20,})["\']',
            'password': r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']+)["\']',
            'secret': r'(?i)(secret|token)\s*[=:]\s*["\']([^"\']{20,})["\']',
            'aws_key': r'(?i)(aws[_-]?access[_-]?key[_-]?id)\s*[=:]\s*["\']([A-Z0-9]{20})["\']',
            'private_key': r'-----BEGIN (RSA |DSA )?PRIVATE KEY-----',
            'oauth_token': r'(?i)(oauth[_-]?token)\s*[=:]\s*["\']([^"\']{20,})["\']',
        }
        
        # Files to scan
        python_files = list(self.project_root.rglob('*.py'))
        config_files = list(self.project_root.rglob('*.json')) + \
                      list(self.project_root.rglob('*.yaml')) + \
                      list(self.project_root.rglob('*.yml'))
        
        all_files = python_files + config_files
        secrets_found = 0
        
        for file_path in all_files:
            # Skip virtual environment and test files
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern_name, pattern in patterns.items():
                        if re.search(pattern, line):
                            # Exclude example files and comments
                            if 'example' in str(file_path).lower() or \
                               'TODO' in line or \
                               'PLACEHOLDER' in line or \
                               line.strip().startswith('#'):
                                continue
                            
                            secrets_found += 1
                            self.add_finding(
                                category='Hardcoded Secrets',
                                severity='CRITICAL',
                                title=f'Potential {pattern_name} found',
                                description=f'Found pattern matching {pattern_name} in code',
                                file_path=str(file_path.relative_to(self.project_root)),
                                line=line_num,
                                recommendation='Move secrets to environment variables or secure credential storage'
                            )
            except Exception as e:
                print(f"  ⚠️  Error scanning {file_path}: {e}")
        
        if secrets_found == 0:
            print(f"  ✅ No hardcoded secrets detected")
        else:
            print(f"  ⚠️  Found {secrets_found} potential hardcoded secrets")
            
    def check_oauth_security(self):
        """Check OAuth token storage security"""
        print("\n[2/8] Checking OAuth token storage...")
        
        # Check if tokens are stored in plain text
        token_files = [
            'token.json',
            'credentials.json',
            'oauth_token.json',
            'data/token.json',
            'data/credentials.json'
        ]
        
        insecure_storage = 0
        for token_file in token_files:
            file_path = self.project_root / token_file
            if file_path.exists():
                # Check file permissions (Windows)
                try:
                    import stat
                    file_stat = file_path.stat()
                    mode = file_stat.st_mode
                    
                    # On Windows, check if file is accessible to everyone
                    if mode & stat.S_IROTH or mode & stat.S_IWOTH:
                        insecure_storage += 1
                        self.add_finding(
                            category='OAuth Security',
                            severity='HIGH',
                            title='OAuth token file has insecure permissions',
                            description=f'{token_file} is readable/writable by others',
                            file_path=token_file,
                            recommendation='Restrict file permissions to current user only'
                        )
                except Exception as e:
                    print(f"  ⚠️  Could not check permissions for {token_file}: {e}")
                
                # Check if token is encrypted
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if '"access_token"' in content or '"refresh_token"' in content:
                            # Token stored in plain text JSON
                            self.add_finding(
                                category='OAuth Security',
                                severity='HIGH',
                                title='OAuth tokens stored in plain text',
                                description=f'{token_file} contains unencrypted tokens',
                                file_path=token_file,
                                recommendation='Encrypt tokens at rest using Windows DPAPI or similar'
                            )
                            insecure_storage += 1
                except Exception as e:
                    pass
        
        if insecure_storage == 0:
            print(f"  ✅ No OAuth token storage issues found")
        else:
            print(f"  ⚠️  Found {insecure_storage} OAuth security issues")
            
    def check_sql_injection(self):
        """Check for SQL injection vulnerabilities"""
        print("\n[3/8] Checking SQL injection prevention...")
        
        python_files = list(self.project_root.rglob('*.py'))
        vulnerabilities = 0
        
        # Patterns indicating potential SQL injection
        unsafe_patterns = [
            r'cursor\.execute\([f"\'].*\{.*\}',  # f-string in execute
            r'cursor\.execute\(.*\+.*\)',         # String concatenation
            r'cursor\.execute\(.*%.*\)',          # % formatting
            r'cursor\.execute\(.*\.format\(',     # .format() method
        ]
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in unsafe_patterns:
                        if re.search(pattern, line):
                            # Check if it's actually using parameterized queries
                            if ', (' in line or ', [' in line:
                                continue  # Likely parameterized
                            
                            vulnerabilities += 1
                            self.add_finding(
                                category='SQL Injection',
                                severity='HIGH',
                                title='Potential SQL injection vulnerability',
                                description='SQL query uses string formatting instead of parameterized queries',
                                file_path=str(file_path.relative_to(self.project_root)),
                                line=line_num,
                                recommendation='Use parameterized queries: cursor.execute(query, (param1, param2))'
                            )
            except Exception as e:
                print(f"  ⚠️  Error scanning {file_path}: {e}")
        
        # Check database.py specifically for proper parameterization
        db_file = self.project_root / 'src' / 'core' / 'database.py'
        if db_file.exists():
            with open(db_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Count parameterized queries (good practice)
                parameterized_count = len(re.findall(r'cursor\.execute\([^,]+,\s*[\(\[]', content))
                print(f"  ℹ️  Found {parameterized_count} parameterized queries in database.py")
        
        if vulnerabilities == 0:
            print(f"  ✅ No SQL injection vulnerabilities detected")
        else:
            print(f"  ⚠️  Found {vulnerabilities} potential SQL injection points")
            
    def check_input_validation(self):
        """Check input validation for file paths and URLs"""
        print("\n[4/8] Checking input validation...")
        
        # Check validators.py
        validators_file = self.project_root / 'src' / 'utils' / 'validators.py'
        validation_issues = 0
        
        if validators_file.exists():
            with open(validators_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for URL validation
                if 'validate_youtube_url' in content:
                    print(f"  ✅ YouTube URL validation found")
                else:
                    validation_issues += 1
                    self.add_finding(
                        category='Input Validation',
                        severity='MEDIUM',
                        title='Missing YouTube URL validation',
                        description='No validation function for YouTube URLs',
                        file_path='src/utils/validators.py',
                        recommendation='Implement validate_youtube_url() function'
                    )
                
                # Check for path traversal protection
                if 'validate_file_path' in content:
                    # Check if it prevents path traversal (needs resolve() and relative_to check)
                    if 'resolve()' in content and 'relative_to' in content:
                        print(f"  ✅ File path validation with traversal protection found")
                    else:
                        validation_issues += 1
                        self.add_finding(
                            category='Input Validation',
                            severity='HIGH',
                            title='Path traversal not prevented',
                            description='File path validation may not prevent directory traversal attacks',
                            file_path='src/utils/validators.py',
                            recommendation='Use Path.resolve() and check if result is within allowed directory'
                        )
                else:
                    validation_issues += 1
                    self.add_finding(
                        category='Input Validation',
                        severity='MEDIUM',
                        title='Missing file path validation',
                        description='No validation function for file paths',
                        file_path='src/utils/validators.py',
                        recommendation='Implement validate_file_path() with path traversal checks'
                    )
        else:
            validation_issues += 1
            self.add_finding(
                category='Input Validation',
                severity='HIGH',
                title='Missing validators module',
                description='No validators.py file found',
                recommendation='Create validators module for input sanitization'
            )
        
        if validation_issues == 0:
            print(f"  ✅ Input validation checks passed")
        else:
            print(f"  ⚠️  Found {validation_issues} input validation issues")
            
    def check_https_enforcement(self):
        """Check that all API calls use HTTPS"""
        print("\n[5/8] Checking HTTPS enforcement...")
        
        python_files = list(self.project_root.rglob('*.py'))
        http_usage = 0
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    # Check for http:// URLs (not https://)
                    if re.search(r'["\']http://(?!localhost|127\.0\.0\.1|192\.168)', line):
                        # Exclude comments and test URLs
                        if line.strip().startswith('#') or 'example' in line.lower():
                            continue
                        
                        http_usage += 1
                        self.add_finding(
                            category='HTTPS Enforcement',
                            severity='MEDIUM',
                            title='HTTP URL used instead of HTTPS',
                            description='Found non-HTTPS URL in API call or configuration',
                            file_path=str(file_path.relative_to(self.project_root)),
                            line=line_num,
                            recommendation='Use HTTPS for all external API calls'
                        )
            except Exception as e:
                print(f"  ⚠️  Error scanning {file_path}: {e}")
        
        # Check YouTube API usage
        api_file = self.project_root / 'src' / 'youtube' / 'api_client.py'
        if api_file.exists():
            with open(api_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'https://www.googleapis.com' in content or 'https://' in content:
                    print(f"  ✅ YouTube API uses HTTPS")
                else:
                    print(f"  ⚠️  Could not verify HTTPS usage in YouTube API")
        
        if http_usage == 0:
            print(f"  ✅ All API calls use HTTPS")
        else:
            print(f"  ⚠️  Found {http_usage} non-HTTPS URLs")
            
    def check_dependency_vulnerabilities(self):
        """Check for known vulnerabilities in dependencies"""
        print("\n[6/8] Checking dependency vulnerabilities...")
        
        requirements_file = self.project_root / 'requirements.txt'
        
        if not requirements_file.exists():
            self.add_finding(
                category='Dependencies',
                severity='INFO',
                title='No requirements.txt found',
                description='Cannot check dependency versions',
                recommendation='Create requirements.txt with pinned versions'
            )
            print(f"  ℹ️  No requirements.txt found")
            return
        
        # Read dependencies
        with open(requirements_file, 'r', encoding='utf-8') as f:
            dependencies = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"  ℹ️  Found {len(dependencies)} dependencies")
        
        # Check for unpinned versions
        unpinned = 0
        for dep in dependencies:
            if not any(op in dep for op in ['==', '>=', '<=', '~=', '!=']):
                unpinned += 1
                self.add_finding(
                    category='Dependencies',
                    severity='LOW',
                    title='Unpinned dependency version',
                    description=f'Dependency {dep} has no version constraint',
                    file_path='requirements.txt',
                    recommendation='Pin versions with == or use ~= for compatible releases'
                )
        
        if unpinned == 0:
            print(f"  ✅ All dependencies have version constraints")
        else:
            print(f"  ⚠️  {unpinned} dependencies have no version constraints")
        
        # Recommend safety check
        print(f"  ℹ️  Recommendation: Run 'pip install safety && safety check' for CVE scanning")
        self.add_finding(
            category='Dependencies',
            severity='INFO',
            title='Consider automated vulnerability scanning',
            description='Use tools like safety or pip-audit for CVE detection',
            recommendation='Add to CI/CD: pip install safety && safety check'
        )
        
    def check_file_permissions(self):
        """Check file and directory permissions"""
        print("\n[7/8] Checking file permissions...")
        
        # Check data directory
        data_dir = self.project_root / 'data'
        if data_dir.exists():
            print(f"  ✅ Data directory exists")
            
            # Check if database file exists
            db_file = data_dir / 'app.db'
            if db_file.exists():
                import stat
                try:
                    file_stat = db_file.stat()
                    mode = file_stat.st_mode
                    
                    # Check if readable by others
                    if mode & stat.S_IROTH:
                        self.add_finding(
                            category='File Permissions',
                            severity='MEDIUM',
                            title='Database file readable by others',
                            description='app.db has overly permissive read permissions',
                            file_path='data/app.db',
                            recommendation='Restrict permissions to owner only'
                        )
                    else:
                        print(f"  ✅ Database file has secure permissions")
                except Exception as e:
                    print(f"  ⚠️  Could not check database permissions: {e}")
        else:
            print(f"  ℹ️  Data directory not yet created")
        
        # Check log directory
        logs_dir = self.project_root / 'logs'
        if logs_dir.exists():
            print(f"  ✅ Logs directory exists")
        
    def check_logging_security(self):
        """Check that sensitive data is not logged"""
        print("\n[8/8] Checking logging security...")
        
        python_files = list(self.project_root.rglob('*.py'))
        sensitive_logging = 0
        
        # Patterns for sensitive data in logs
        sensitive_patterns = [
            r'logger\.(info|debug|warning)\(.*password.*\)',
            r'logger\.(info|debug|warning)\(.*token.*\)',
            r'logger\.(info|debug|warning)\(.*api[_-]?key.*\)',
            r'logger\.(info|debug|warning)\(.*secret.*\)',
        ]
        
        for file_path in python_files:
            if 'venv' in str(file_path) or '__pycache__' in str(file_path):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    
                for line_num, line in enumerate(lines, 1):
                    for pattern in sensitive_patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            sensitive_logging += 1
                            self.add_finding(
                                category='Logging Security',
                                severity='MEDIUM',
                                title='Potential sensitive data in logs',
                                description='Logging statement may include passwords, tokens, or keys',
                                file_path=str(file_path.relative_to(self.project_root)),
                                line=line_num,
                                recommendation='Sanitize sensitive data before logging or use DEBUG level'
                            )
            except Exception as e:
                print(f"  ⚠️  Error scanning {file_path}: {e}")
        
        if sensitive_logging == 0:
            print(f"  ✅ No sensitive data found in logging statements")
        else:
            print(f"  ⚠️  Found {sensitive_logging} potentially sensitive logging statements")
            
    def generate_report(self):
        """Generate security audit report"""
        print("\n" + "="*70)
        print("SECURITY AUDIT SUMMARY")
        print("="*70)
        
        print(f"\nTotal Findings: {len(self.findings)}")
        print(f"  CRITICAL: {self.severity_counts['CRITICAL']}")
        print(f"  HIGH:     {self.severity_counts['HIGH']}")
        print(f"  MEDIUM:   {self.severity_counts['MEDIUM']}")
        print(f"  LOW:      {self.severity_counts['LOW']}")
        print(f"  INFO:     {self.severity_counts['INFO']}")
        
        # Group by category
        by_category = {}
        for finding in self.findings:
            cat = finding['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(finding)
        
        print(f"\nFindings by Category:")
        for category, findings in sorted(by_category.items()):
            print(f"  {category}: {len(findings)}")
        
        # Save JSON report
        report_dir = self.project_root / 'security_reports'
        report_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_report = report_dir / f'security_audit_{timestamp}.json'
        
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_findings': len(self.findings),
                'by_severity': self.severity_counts,
                'by_category': {cat: len(findings) for cat, findings in by_category.items()}
            },
            'findings': self.findings
        }
        
        with open(json_report, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n✅ JSON report saved: {json_report}")
        
        # Generate Markdown report
        md_report = report_dir / f'security_audit_{timestamp}.md'
        self._generate_markdown_report(md_report, report_data, by_category)
        print(f"✅ Markdown report saved: {md_report}")
        
        # Print critical/high findings
        critical_high = [f for f in self.findings if f['severity'] in ['CRITICAL', 'HIGH']]
        if critical_high:
            print(f"\n⚠️  ATTENTION: {len(critical_high)} CRITICAL/HIGH severity findings require immediate action!")
        else:
            print(f"\n✅ No CRITICAL or HIGH severity issues found!")
        
    def _generate_markdown_report(self, file_path: Path, report_data: dict, by_category: dict):
        """Generate Markdown format report"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Security Audit Report\n\n")
            f.write(f"**Generated**: {report_data['timestamp']}\n\n")
            
            f.write("## Summary\n\n")
            f.write(f"- **Total Findings**: {report_data['summary']['total_findings']}\n")
            f.write(f"- **Critical**: {report_data['summary']['by_severity']['CRITICAL']}\n")
            f.write(f"- **High**: {report_data['summary']['by_severity']['HIGH']}\n")
            f.write(f"- **Medium**: {report_data['summary']['by_severity']['MEDIUM']}\n")
            f.write(f"- **Low**: {report_data['summary']['by_severity']['LOW']}\n")
            f.write(f"- **Info**: {report_data['summary']['by_severity']['INFO']}\n\n")
            
            f.write("## Findings by Severity\n\n")
            
            for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
                severity_findings = [f for f in self.findings if f['severity'] == severity]
                if severity_findings:
                    f.write(f"### {severity} ({len(severity_findings)})\n\n")
                    
                    for finding in severity_findings:
                        f.write(f"#### {finding['title']}\n\n")
                        f.write(f"- **Category**: {finding['category']}\n")
                        f.write(f"- **Description**: {finding['description']}\n")
                        if finding['file']:
                            f.write(f"- **File**: `{finding['file']}`")
                            if finding['line']:
                                f.write(f" (Line {finding['line']})")
                            f.write("\n")
                        if finding['recommendation']:
                            f.write(f"- **Recommendation**: {finding['recommendation']}\n")
                        f.write("\n")
            
            f.write("## Findings by Category\n\n")
            for category in sorted(by_category.keys()):
                findings = by_category[category]
                f.write(f"### {category} ({len(findings)})\n\n")
                for finding in findings:
                    f.write(f"- **[{finding['severity']}]** {finding['title']}\n")
                f.write("\n")
            
            f.write("## Recommendations\n\n")
            f.write("1. Address all CRITICAL and HIGH severity findings immediately\n")
            f.write("2. Review and remediate MEDIUM severity issues\n")
            f.write("3. Consider LOW and INFO recommendations for future improvements\n")
            f.write("4. Re-run security audit after fixes to verify remediation\n")
            f.write("5. Integrate automated security scanning into CI/CD pipeline\n")
            
    def run_audit(self):
        """Run complete security audit"""
        print("="*70)
        print("YOUTUBE BOT VIDEO EXTRACTOR - SECURITY AUDIT")
        print("="*70)
        print(f"Project Root: {self.project_root}")
        print(f"Audit Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all checks
        self.scan_hardcoded_secrets()
        self.check_oauth_security()
        self.check_sql_injection()
        self.check_input_validation()
        self.check_https_enforcement()
        self.check_dependency_vulnerabilities()
        self.check_file_permissions()
        self.check_logging_security()
        
        # Generate report
        self.generate_report()


if __name__ == '__main__':
    auditor = SecurityAuditor()
    auditor.run_audit()
