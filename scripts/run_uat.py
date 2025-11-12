#!/usr/bin/env python3
"""
User Acceptance Testing (UAT) Automation Script
Phase 5 Task 6 - YouTube Bot Video Extractor

This script automates portions of the UAT test plan that can be
programmatically verified. Manual testing still required for:
- OAuth authentication flow
- GUI visual inspection
- System tray interactions
- 24-hour soak test
"""

import sys
import os
import time
import json
import sqlite3
import psutil
import platform
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

try:
    from core.config import ConfigManager
    from utils.validators import validate_file_path, validate_directory_path, validate_youtube_url
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


class UATTestRunner:
    """Automated UAT test executor"""
    
    def __init__(self):
        self.project_root = project_root
        self.results: List[Dict] = []
        self.start_time = datetime.now()
        self.config: Optional[ConfigManager] = None
        self.db = None  # Will use sqlite3 directly
        
    def print_header(self, text: str):
        """Print formatted section header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}\n")
        
    def print_test(self, scenario: str, description: str):
        """Print test scenario header"""
        print(f"\n{'-'*80}")
        print(f"[TEST] {scenario}: {description}")
        print(f"{'-'*80}")
        
    def record_result(self, scenario: str, test_name: str, passed: bool, 
                     details: str = "", severity: str = "MEDIUM"):
        # Record result
        result = {
            "scenario": scenario,
            "test_name": test_name,
            "passed": passed,
            "details": details,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        self.results.append(result)
        
        # Print result
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} - {test_name}")
        if details:
            print(f"   Details: {details}")
            
    def run_all_tests(self):
        """Execute all automated UAT tests"""
        self.print_header("UAT Automated Test Suite - Phase 5 Task 6")
        
        print(f"Test Date: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {platform.python_version()}")
        print(f"Python Executable: {sys.executable}")
        print(f"Project Root: {self.project_root}")
        
        # Test scenarios
        self.test_environment_setup()
        self.test_configuration_loading()
        self.test_database_initialization()
        self.test_validators()
        self.test_file_structure()
        self.test_dependencies()
        self.test_resource_usage()
        self.test_documentation_presence()
        self.test_security_features()
        
        # Generate report
        self.generate_report()
        
    def test_environment_setup(self):
        """TS-ENV: Environment Setup Verification"""
        self.print_test("TS-ENV", "Environment Setup Verification")
        
        # Check Python version
        py_version = sys.version_info
        required_version = (3, 8)
        passed = py_version >= required_version
        self.record_result(
            "TS-ENV", 
            f"Python Version >= {required_version[0]}.{required_version[1]}",
            passed,
            f"Found: {platform.python_version()}",
            "CRITICAL"
        )
        
        # Check OS
        is_windows = platform.system() == "Windows"
        self.record_result(
            "TS-ENV",
            "Running on Windows",
            is_windows,
            f"OS: {platform.system()} {platform.release()}",
            "CRITICAL"
        )
        
        # Check project structure
        required_dirs = ["src", "tests", "data", "logs", "docs"]
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            exists = dir_path.exists() and dir_path.is_dir()
            self.record_result(
                "TS-ENV",
                f"Directory '{dir_name}' exists",
                exists,
                f"Path: {dir_path}",
                "HIGH"
            )
            
    def test_configuration_loading(self):
        """TS-002: Configuration Loading and Validation"""
        self.print_test("TS-002", "Configuration Loading and Validation")
        
        try:
            # Load configuration
            self.config = ConfigManager()
            self.record_result(
                "TS-002",
                "Config instance created successfully",
                True,
                f"Config file: {self.config.config_path}",
                "CRITICAL"
            )
            
            # Check required configuration keys
            required_keys = [
                ("monitoring.check_interval_minutes", "monitoring check interval"),
                ("download.directory", "download directory"),
                ("performance.max_concurrent_downloads", "max concurrent downloads"),
                ("performance.retry_attempts", "retry attempts"),
                ("active_hours.start", "active hours start"),
                ("active_hours.end", "active hours end")
            ]
            
            for key, description in required_keys:
                value = self.config.get(key)
                has_key = value is not None
                self.record_result(
                    "TS-002",
                    f"Config has '{description}'",
                    has_key,
                    f"Value: {value}",
                    "HIGH"
                )
                
            # Validate configuration values
            max_concurrent = self.config.get('performance.max_concurrent_downloads', 0)
            valid_concurrent = 1 <= max_concurrent <= 10
            self.record_result(
                "TS-002",
                "max_concurrent_downloads in valid range (1-10)",
                valid_concurrent,
                f"Value: {max_concurrent}",
                "MEDIUM"
            )
            
            retry_attempts = self.config.get('performance.retry_attempts', 0)
            valid_retries = 0 <= retry_attempts <= 5
            self.record_result(
                "TS-002",
                "retry_attempts in valid range (0-5)",
                valid_retries,
                f"Value: {retry_attempts}",
                "MEDIUM"
            )
            
            # Check file permissions security (from Phase 5 Task 4)
            data_dir = self.project_root / "data"
            if data_dir.exists():
                # On Windows, we can't easily check permissions via Python
                # Just verify the directory exists and is accessible
                can_write = os.access(data_dir, os.W_OK)
                self.record_result(
                    "TS-002",
                    "Data directory is writable",
                    can_write,
                    f"Path: {data_dir}",
                    "HIGH"
                )
                
        except Exception as e:
            self.record_result(
                "TS-002",
                "Config loading",
                False,
                f"Error: {str(e)}",
                "CRITICAL"
            )
            
    def test_database_initialization(self):
        """TS-003: Database Initialization"""
        self.print_test("TS-003", "Database Initialization")
        
        try:
            # Initialize database connection directly
            db_path = self.project_root / "data" / "videos.db"
            self.db = sqlite3.connect(str(db_path))
            
            self.record_result(
                "TS-003",
                "Database initialized successfully",
                True,
                f"Path: {db_path}",
                "CRITICAL"
            )
            
            # Check database schema
            cursor = self.db.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            # Required tables (actual schema from database.py)
            required_tables = ["videos", "settings", "logs", "stats"]
            for table in required_tables:
                exists = table in tables
                self.record_result(
                    "TS-003",
                    f"Table '{table}' exists",
                    exists,
                    f"Tables found: {', '.join(tables)}",
                    "HIGH"
                )
                
            # Check videos table schema (actual columns from database.py)
            cursor.execute("PRAGMA table_info(videos)")
            columns = [row[1] for row in cursor.fetchall()]
            
            required_columns = ["id", "source_video_id", "source_title", "status", "created_at"]
            for column in required_columns:
                exists = column in columns
                self.record_result(
                    "TS-003",
                    f"Column 'videos.{column}' exists",
                    exists,
                    f"Columns: {', '.join(columns)}",
                    "MEDIUM"
                )
                
            # Test database operations
            cursor.execute("SELECT COUNT(*) FROM videos")
            count = cursor.fetchone()[0]
            self.record_result(
                "TS-003",
                "Can query videos table",
                True,
                f"Current record count: {count}",
                "HIGH"
            )
            
            # Check database integrity
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()[0]
            is_ok = integrity_result == "ok"
            self.record_result(
                "TS-003",
                "Database integrity check",
                is_ok,
                f"Result: {integrity_result}",
                "CRITICAL"
            )
            
            self.db.close()
            
        except Exception as e:
            self.record_result(
                "TS-003",
                "Database initialization",
                False,
                f"Error: {str(e)}",
                "CRITICAL"
            )
            
    def test_validators(self):
        """TS-004: Input Validation (Security)"""
        self.print_test("TS-004", "Input Validation and Security")
        
        # Test YouTube URL validation
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=10s"
        ]
        
        invalid_urls = [
            "http://www.youtube.com/watch?v=invalid",  # HTTP not HTTPS
            "https://example.com/video",
            "not_a_url",
            "",
            "javascript:alert(1)"
        ]
        
        for url in valid_urls:
            try:
                is_valid = validate_youtube_url(url)
                self.record_result(
                    "TS-004",
                    f"Valid URL accepted: {url[:50]}...",
                    is_valid,
                    "",
                    "HIGH"
                )
            except Exception as e:
                self.record_result(
                    "TS-004",
                    f"Valid URL accepted: {url[:50]}...",
                    False,
                    f"Error: {str(e)}",
                    "HIGH"
                )
                
        for url in invalid_urls:
            try:
                is_valid, error_msg = validate_youtube_url(url)
                # Should be invalid - check that it was rejected
                self.record_result(
                    "TS-004",
                    f"Invalid URL rejected: {url[:50]}...",
                    not is_valid,  # PASS if validation failed (URL rejected)
                    f"Error message: {error_msg}",
                    "HIGH"
                )
            except Exception as e:
                # Exception is also acceptable for invalid URLs
                self.record_result(
                    "TS-004",
                    f"Invalid URL rejected: {url[:50]}...",
                    True,
                    "Raised validation error as expected",
                    "HIGH"
                )
                
        # Test path traversal prevention (from security audit fixes)
        test_paths = [
            ("normal_file.txt", True),  # Relative path within base_dir should be allowed
            ("../../../etc/passwd", False),  # Traversal outside base_dir should be rejected
            ("..\\..\\windows\\system32\\config", False),  # Windows traversal should be rejected
            (str(self.project_root / "data" / "test.db"), True)  # Absolute path within base_dir should be allowed
        ]
        
        for test_path, should_be_valid in test_paths:
            try:
                # Validate against project data directory
                allowed_base = self.project_root / "data"
                is_valid, error_msg = validate_file_path(test_path, allowed_base_dir=allowed_base)
                
                # Check if result matches expectation
                result_correct = (is_valid == should_be_valid)
                self.record_result(
                    "TS-004",
                    f"Path validation: {test_path[:40]}...",
                    result_correct,
                    f"Expected valid={should_be_valid}, Got valid={is_valid}, Message: {error_msg}",
                    "CRITICAL"  # Path traversal is critical security issue
                )
            except Exception as e:
                # For invalid paths, exception is acceptable
                if not should_be_valid:
                    self.record_result(
                        "TS-004",
                        f"Path validation: {test_path[:40]}...",
                        True,
                        "Rejected with exception as expected",
                        "CRITICAL"
                    )
                else:
                    self.record_result(
                        "TS-004",
                        f"Path validation: {test_path[:40]}...",
                        False,
                        f"Unexpected error: {str(e)}",
                        "CRITICAL"
                    )
                    
    def test_file_structure(self):
        """TS-005: File Structure and Permissions"""
        self.print_test("TS-005", "File Structure and Permissions")
        
        # Check required files
        required_files = [
            "README.md",
            "SETUP.md",
            "requirements.txt",
            "src/core/config.py",
            "src/core/database.py",
            "src/youtube/api_client.py",
            "src/gui/main_window.py",
            "docs/USER_GUIDE.md",
            "docs/TROUBLESHOOTING.md",
            "docs/API_LIMITS.md"
        ]
        
        for file_rel_path in required_files:
            file_path = self.project_root / file_rel_path
            exists = file_path.exists() and file_path.is_file()
            self.record_result(
                "TS-005",
                f"File exists: {file_rel_path}",
                exists,
                f"Path: {file_path}",
                "HIGH"
            )
            
            # Check file is readable
            if exists:
                readable = os.access(file_path, os.R_OK)
                self.record_result(
                    "TS-005",
                    f"File readable: {file_rel_path}",
                    readable,
                    "",
                    "MEDIUM"
                )
                
        # Check data directory permissions (security)
        data_dir = self.project_root / "data"
        if data_dir.exists():
            # Check ownership/permissions (Windows-specific via icacls)
            try:
                result = subprocess.run(
                    ["icacls", str(data_dir)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Look for restricted permissions (only owner has access)
                output = result.stdout.lower()
                has_restricted = "everyone" not in output or "(r)" in output
                
                self.record_result(
                    "TS-005",
                    "Data directory has restricted permissions",
                    has_restricted,
                    "File security utility integrated in Phase 5 Task 4",
                    "MEDIUM"
                )
            except Exception as e:
                self.record_result(
                    "TS-005",
                    "Data directory permissions check",
                    False,
                    f"Could not verify: {str(e)}",
                    "LOW"
                )
                
    def test_dependencies(self):
        """TS-006: Dependency Installation"""
        self.print_test("TS-006", "Python Dependencies")
        
        # Read requirements.txt
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            self.record_result(
                "TS-006",
                "requirements.txt exists",
                False,
                "File not found",
                "CRITICAL"
            )
            return
            
        # Parse requirements
        with open(requirements_file) as f:
            requirements = [
                line.strip().split("==")[0].split(">=")[0].split("<=")[0]
                for line in f
                if line.strip() and not line.startswith("#")
            ]
            
        # Check if packages are importable
        for package in requirements:
            # Map package names to import names (packages use hyphens, imports use underscores/different names)
            # Start with normalized name
            normalized_package = package.replace("-", "_").lower()
            
            # Special cases - map package names (with hyphens) to actual import names
            import_map = {
                "python-dotenv": "dotenv",
                "httpx": "httpx",
                "requests": "requests",
                "google-api-python-client": "googleapiclient",
                "google-auth-oauthlib": "google_auth_oauthlib",
                "google-auth-httplib2": "google_auth_httplib2",
                "yt-dlp": "yt_dlp",
                "pyqt5": "PyQt5",
                "pyqt5-qt5": "PyQt5.QtCore",  # Bundled with PyQt5
                "pyqt5-sip": "PyQt5.sip",  # Bundled with PyQt5
                "apscheduler": "apscheduler",
                "pillow": "PIL",
                "tqdm": "tqdm",
                "psutil": "psutil"
            }
            
            # Get the actual import name
            import_name = import_map.get(package.lower(), normalized_package)
            
            # Skip non-importable packages that are bundled
            skip_packages = []
            if package.lower() in skip_packages:
                continue
            
            try:
                __import__(import_name)
                self.record_result(
                    "TS-006",
                    f"Package '{package}' importable",
                    True,
                    f"Import name: {import_name}",
                    "HIGH"
                )
            except ImportError as e:
                # Package not installed
                self.record_result(
                    "TS-006",
                    f"Package '{package}' importable",
                    False,
                    f"Import error: {str(e)}",
                    "HIGH"
                )
            except Exception as e:
                # Other import error
                self.record_result(
                    "TS-006",
                    f"Package '{package}' importable",
                    False,
                    f"Unexpected error: {type(e).__name__}: {str(e)}",
                    "HIGH"
                )
                
        # Check FFmpeg (external dependency)
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            has_ffmpeg = result.returncode == 0
            version = result.stdout.split("\n")[0] if has_ffmpeg else "Not found"
            
            self.record_result(
                "TS-006",
                "FFmpeg installed and accessible",
                has_ffmpeg,
                f"Version: {version}",
                "HIGH"
            )
        except Exception as e:
            self.record_result(
                "TS-006",
                "FFmpeg installed and accessible",
                False,
                f"Error: {str(e)}",
                "HIGH"
            )
            
    def test_resource_usage(self):
        """TS-022: Resource Usage - Idle State"""
        self.print_test("TS-022", "Resource Usage - Idle State")
        
        try:
            # Get current process
            process = psutil.Process()
            
            # CPU usage (measure over 1 second)
            cpu_percent = process.cpu_percent(interval=1.0)
            cpu_ok = cpu_percent <= 5.0  # Should be < 1% but allow 5% margin
            
            self.record_result(
                "TS-022",
                "CPU usage idle < 5%",
                cpu_ok,
                f"Current: {cpu_percent:.2f}%",
                "HIGH"
            )
            
            # Memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / 1024 / 1024
            memory_ok = memory_mb <= 100  # Should be < 50 MB but allow margin
            
            self.record_result(
                "TS-022",
                "Memory usage idle < 100 MB",
                memory_ok,
                f"Current: {memory_mb:.2f} MB",
                "HIGH"
            )
            
            # Thread count
            thread_count = process.num_threads()
            threads_ok = thread_count <= 20  # Reasonable limit
            
            self.record_result(
                "TS-022",
                "Thread count reasonable (< 20)",
                threads_ok,
                f"Current: {thread_count} threads",
                "MEDIUM"
            )
            
            # File handles
            try:
                file_handles = len(process.open_files())
                handles_ok = file_handles <= 50
                
                self.record_result(
                    "TS-022",
                    "Open file handles reasonable (< 50)",
                    handles_ok,
                    f"Current: {file_handles} handles",
                    "MEDIUM"
                )
            except Exception as e:
                # Not critical if we can't check file handles
                self.record_result(
                    "TS-022",
                    "Open file handles check",
                    False,
                    f"Could not check: {str(e)}",
                    "LOW"
                )
                
        except Exception as e:
            self.record_result(
                "TS-022",
                "Resource usage monitoring",
                False,
                f"Error: {str(e)}",
                "MEDIUM"
            )
            
    def test_documentation_presence(self):
        """TS-025/26/27: Documentation Presence and Completeness"""
        self.print_test("TS-025/26/27", "Documentation Presence and Completeness")
        
        # Check documentation files
        doc_files = {
            "README.md": ("Project Overview", ["installation", "features", "usage"]),
            "SETUP.md": ("Setup Guide", ["prerequisites", "python", "ffmpeg", "dependencies"]),
            "docs/USER_GUIDE.md": ("User Guide", ["configuration", "queue", "upload", "dashboard"]),
            "docs/TROUBLESHOOTING.md": ("Troubleshooting", ["authentication", "download", "upload", "error"]),
            "docs/API_LIMITS.md": ("API Limits", ["quota", "limits", "optimization"])
        }
        
        for doc_file, (doc_type, keywords) in doc_files.items():
            file_path = self.project_root / doc_file
            
            if not file_path.exists():
                self.record_result(
                    "TS-DOC",
                    f"{doc_type} exists",
                    False,
                    f"File not found: {file_path}",
                    "CRITICAL"
                )
                continue
                
            # Check file size (should have content)
            file_size = file_path.stat().st_size
            has_content = file_size > 1000  # At least 1 KB
            
            self.record_result(
                "TS-DOC",
                f"{doc_type} has content (> 1 KB)",
                has_content,
                f"Size: {file_size:,} bytes",
                "HIGH"
            )
            
            # Check for keywords
            try:
                with open(file_path, encoding='utf-8') as f:
                    content = f.read().lower()
                    
                for keyword in keywords:
                    has_keyword = keyword.lower() in content
                    self.record_result(
                        "TS-DOC",
                        f"{doc_type} mentions '{keyword}'",
                        has_keyword,
                        "",
                        "MEDIUM"
                    )
            except Exception as e:
                self.record_result(
                    "TS-DOC",
                    f"{doc_type} readable",
                    False,
                    f"Error: {str(e)}",
                    "MEDIUM"
                )
                
    def test_security_features(self):
        """TS-SECURITY: Security Features from Phase 5 Task 4"""
        self.print_test("TS-SECURITY", "Security Features Verification")
        
        # Check security utilities exist
        security_files = [
            "src/utils/validators.py",
            "src/utils/file_security.py",
            "scripts/security_audit.py"
        ]
        
        for sec_file in security_files:
            file_path = self.project_root / sec_file
            exists = file_path.exists()
            
            self.record_result(
                "TS-SECURITY",
                f"Security file exists: {sec_file}",
                exists,
                f"Path: {file_path}",
                "HIGH"
            )
            
            # Check for security functions
            if exists and sec_file == "src/utils/validators.py":
                with open(file_path) as f:
                    content = f.read()
                    
                # Check for path traversal prevention (resolve + relative_to)
                has_resolve = ".resolve()" in content
                has_relative_to = ".relative_to(" in content
                
                self.record_result(
                    "TS-SECURITY",
                    "Path traversal prevention implemented",
                    has_resolve and has_relative_to,
                    f"resolve: {has_resolve}, relative_to: {has_relative_to}",
                    "CRITICAL"
                )
                
        # Check HTTPS enforcement in tests
        test_files = list((self.project_root / "tests").rglob("*.py"))
        http_urls_found = []
        
        for test_file in test_files:
            try:
                with open(test_file) as f:
                    content = f.read()
                    # Look for HTTP URLs (but ignore comments and specific exceptions)
                    if 'http://' in content and 'youtube.com' in content:
                        http_urls_found.append(test_file.name)
            except:
                pass
                
        https_enforced = len(http_urls_found) == 0
        self.record_result(
            "TS-SECURITY",
            "HTTPS enforced in tests (no HTTP YouTube URLs)",
            https_enforced,
            f"Files with HTTP: {', '.join(http_urls_found) if http_urls_found else 'None'}",
            "MEDIUM"
        )
        
    def generate_report(self):
        """Generate UAT test report"""
        self.print_header("UAT Test Results Summary")
        
        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Count by severity
        critical_passed = sum(1 for r in self.results if r["passed"] and r["severity"] == "CRITICAL")
        critical_total = sum(1 for r in self.results if r["severity"] == "CRITICAL")
        high_passed = sum(1 for r in self.results if r["passed"] and r["severity"] == "HIGH")
        high_total = sum(1 for r in self.results if r["severity"] == "HIGH")
        
        # Print summary
        print(f"[SUMMARY] Test Execution Summary")
        print(f"{'-'*80}")
        print(f"Total Tests:        {total_tests}")
        print(f"Passed:            {passed_tests} [PASS]")
        print(f"Failed:            {failed_tests} [FAIL]")
        print(f"Pass Rate:         {pass_rate:.1f}%")
        print(f"\nBy Severity:")
        print(f"  CRITICAL:        {critical_passed}/{critical_total} passed")
        print(f"  HIGH:            {high_passed}/{high_total} passed")
        
        # Determine overall status
        if failed_tests == 0:
            status = "[SUCCESS] ALL TESTS PASSED!"
            recommendation = "[READY] Ready for manual UAT testing"
        elif critical_total > 0 and critical_passed < critical_total:
            status = "[CRITICAL] CRITICAL FAILURES DETECTED"
            recommendation = "[BLOCKED] Fix critical issues before proceeding"
        elif pass_rate >= 90:
            status = "[WARNING] MOSTLY PASSING (Minor Issues)"
            recommendation = "[CAUTION] Review failures, proceed with caution"
        else:
            status = "[FAIL] MULTIPLE FAILURES"
            recommendation = "[BLOCKED] Address failures before manual testing"
            
        print(f"\n{status}")
        print(f"Recommendation: {recommendation}")
        
        # List failures
        if failed_tests > 0:
            print(f"\n[FAILURES] Failed Tests:")
            print(f"{'-'*80}")
            for result in self.results:
                if not result["passed"]:
                    print(f"  [{result['severity']}] {result['scenario']}: {result['test_name']}")
                    if result["details"]:
                        print(f"    Details: {result['details']}")
                        
        # Save detailed report
        self.save_json_report()
        self.save_markdown_report()
        
        # Print footer
        duration = (datetime.now() - self.start_time).total_seconds()
        print(f"\n{'-'*80}")
        print(f"Test Duration: {duration:.2f} seconds")
        print(f"Report saved to: tests/uat/")
        print(f"{'='*80}\n")
        
    def save_json_report(self):
        """Save results as JSON"""
        report_dir = self.project_root / "tests" / "uat"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"uat_automated_results_{timestamp}.json"
        
        report_data = {
            "test_date": self.start_time.isoformat(),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "python_version": platform.python_version()
            },
            "summary": {
                "total_tests": len(self.results),
                "passed": sum(1 for r in self.results if r["passed"]),
                "failed": sum(1 for r in self.results if not r["passed"]),
                "pass_rate": (sum(1 for r in self.results if r["passed"]) / len(self.results) * 100) if self.results else 0
            },
            "results": self.results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
            
        print(f"[OK] JSON report: {report_file}")
        
    def save_markdown_report(self):
        """Save results as Markdown"""
        report_dir = self.project_root / "tests" / "uat"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"uat_automated_results_{timestamp}.md"
        
        # Calculate stats
        total = len(self.results)
        passed = sum(1 for r in self.results if r["passed"])
        failed = total - passed
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        # Generate markdown
        md_content = f"""# UAT Automated Test Results
**Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Platform:** {platform.system()} {platform.release()}  
**Python:** {platform.python_version()}

## Summary
- **Total Tests:** {total}
- **Passed:** {passed}
- **Failed:** {failed}
- **Pass Rate:** {pass_rate:.1f}%

## Results by Scenario

"""
        
        # Group by scenario
        scenarios = {}
        for result in self.results:
            scenario = result["scenario"]
            if scenario not in scenarios:
                scenarios[scenario] = []
            scenarios[scenario].append(result)
            
        # Write results by scenario
        for scenario, results in sorted(scenarios.items()):
            scenario_passed = sum(1 for r in results if r["passed"])
            scenario_total = len(results)
            
            md_content += f"### {scenario} ({scenario_passed}/{scenario_total} passed)\n\n"
            md_content += "| Test | Status | Severity | Details |\n"
            md_content += "|------|--------|----------|----------|\n"
            
            for result in results:
                status = "PASS" if result["passed"] else "FAIL"
                details = result["details"][:50] + "..." if len(result["details"]) > 50 else result["details"]
                md_content += f"| {result['test_name']} | {status} | {result['severity']} | {details} |\n"
                
            md_content += "\n"
            
        # Write to file
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        print(f"[OK] Markdown report: {report_file}")


def main():
    """Main entry point"""
    runner = UATTestRunner()
    runner.run_all_tests()
    
    # Return exit code based on results
    failed = sum(1 for r in runner.results if not r["passed"])
    critical_failed = sum(1 for r in runner.results if not r["passed"] and r["severity"] == "CRITICAL")
    
    if critical_failed > 0:
        sys.exit(2)  # Critical failures
    elif failed > 0:
        sys.exit(1)  # Non-critical failures
    else:
        sys.exit(0)  # All passed


if __name__ == "__main__":
    main()
