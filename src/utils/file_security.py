"""
File Security Utilities
Secure file and directory permissions on Windows
"""

import os
import sys
from pathlib import Path


def secure_file_permissions(file_path: str) -> bool:
    """
    Secure file permissions to owner-only access (Windows).
    
    Args:
        file_path: Path to file to secure
    
    Returns:
        True if successful, False otherwise
    """
    if sys.platform != 'win32':
        # On Unix-like systems, use chmod
        try:
            os.chmod(file_path, 0o600)  # Owner read/write only
            return True
        except Exception as e:
            print(f"Error setting permissions: {e}")
            return False
    
    # Windows: Use icacls to restrict permissions
    try:
        import subprocess
        
        # Get current user
        username = os.environ.get('USERNAME')
        
        # Remove all permissions
        subprocess.run(
            ['icacls', str(file_path), '/inheritance:r'],
            check=True,
            capture_output=True
        )
        
        # Grant full control to current user only
        subprocess.run(
            ['icacls', str(file_path), f'/grant:r', f'{username}:F'],
            check=True,
            capture_output=True
        )
        
        print(f"✅ Secured permissions for: {file_path}")
        return True
    except Exception as e:
        print(f"⚠️  Error securing file permissions: {e}")
        return False


def secure_directory_permissions(dir_path: str) -> bool:
    """
    Secure directory permissions to owner-only access (Windows).
    
    Args:
        dir_path: Path to directory to secure
    
    Returns:
        True if successful, False otherwise
    """
    if sys.platform != 'win32':
        try:
            os.chmod(dir_path, 0o700)  # Owner read/write/execute only
            return True
        except Exception as e:
            print(f"Error setting permissions: {e}")
            return False
    
    try:
        import subprocess
        
        username = os.environ.get('USERNAME')
        
        # Remove inheritance and grant to current user only
        subprocess.run(
            ['icacls', str(dir_path), '/inheritance:r'],
            check=True,
            capture_output=True
        )
        
        subprocess.run(
            ['icacls', str(dir_path), f'/grant:r', f'{username}:(OI)(CI)F'],
            check=True,
            capture_output=True
        )
        
        print(f"✅ Secured permissions for directory: {dir_path}")
        return True
    except Exception as e:
        print(f"⚠️  Error securing directory permissions: {e}")
        return False


def secure_sensitive_files():
    """Secure all sensitive files in the application"""
    from pathlib import Path
    
    # Get project root
    project_root = Path(__file__).parent.parent
    
    # Files and directories to secure
    sensitive_paths = [
        project_root / 'data',
        project_root / 'data' / 'app.db',
        project_root / 'data' / 'token.json',
        project_root / 'data' / 'credentials.json',
        project_root / 'logs',
    ]
    
    for path in sensitive_paths:
        if path.exists():
            if path.is_dir():
                secure_directory_permissions(str(path))
            else:
                secure_file_permissions(str(path))


if __name__ == '__main__':
    print("Securing sensitive files and directories...")
    secure_sensitive_files()
    print("Done!")
