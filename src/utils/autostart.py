"""
Windows Auto-Start Functionality
Manages application startup with Windows
"""
import os
import sys
import winreg
import logging
from pathlib import Path
from typing import Optional


class AutoStartManager:
    """
    Manages Windows auto-start functionality
    Uses Windows Registry method for reliability
    """
    
    # Registry key path
    REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
    APP_NAME = "YouTubeBotVideoExtractor"
    
    def __init__(self):
        """Initialize auto-start manager"""
        self._logger = logging.getLogger(__name__)
    
    def is_enabled(self) -> bool:
        """
        Check if auto-start is currently enabled
        
        Returns:
            True if enabled, False otherwise
        """
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_PATH,
                0,
                winreg.KEY_READ
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, self.APP_NAME)
                winreg.CloseKey(key)
                
                # Check if the value matches our executable
                exe_path = self._get_executable_path()
                return value == exe_path
            
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        
        except Exception as e:
            self._logger.error(f"Error checking auto-start status: {e}")
            return False
    
    def enable(self) -> bool:
        """
        Enable auto-start on Windows startup
        
        Returns:
            True if successful, False otherwise
        """
        try:
            exe_path = self._get_executable_path()
            
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            
            # Set value
            winreg.SetValueEx(
                key,
                self.APP_NAME,
                0,
                winreg.REG_SZ,
                exe_path
            )
            
            winreg.CloseKey(key)
            self._logger.info(f"Auto-start enabled: {exe_path}")
            return True
        
        except Exception as e:
            self._logger.error(f"Error enabling auto-start: {e}", exc_info=True)
            return False
    
    def disable(self) -> bool:
        """
        Disable auto-start on Windows startup
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Open registry key
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                self.REGISTRY_PATH,
                0,
                winreg.KEY_SET_VALUE
            )
            
            try:
                # Delete value
                winreg.DeleteValue(key, self.APP_NAME)
                self._logger.info("Auto-start disabled")
                success = True
            
            except FileNotFoundError:
                # Value doesn't exist, already disabled
                self._logger.debug("Auto-start was already disabled")
                success = True
            
            finally:
                winreg.CloseKey(key)
            
            return success
        
        except Exception as e:
            self._logger.error(f"Error disabling auto-start: {e}", exc_info=True)
            return False
    
    def toggle(self) -> bool:
        """
        Toggle auto-start on/off
        
        Returns:
            True if now enabled, False if now disabled
        """
        if self.is_enabled():
            self.disable()
            return False
        else:
            self.enable()
            return True
    
    def _get_executable_path(self) -> str:
        """
        Get the path to the application executable
        
        Returns:
            Full path to executable
        """
        if getattr(sys, 'frozen', False):
            # Running as compiled executable (PyInstaller)
            exe_path = sys.executable
        else:
            # Running as Python script
            # Point to pythonw.exe with script path for silent startup
            python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
            script_path = os.path.abspath(sys.argv[0])
            exe_path = f'"{python_exe}" "{script_path}"'
        
        return exe_path
    
    def get_startup_folder_path(self) -> Optional[Path]:
        """
        Get the Windows startup folder path (alternative method)
        
        Returns:
            Path to startup folder or None if not found
        """
        try:
            startup_folder = Path(os.environ['APPDATA']) / 'Microsoft' / 'Windows' / 'Start Menu' / 'Programs' / 'Startup'
            return startup_folder if startup_folder.exists() else None
        except Exception as e:
            self._logger.error(f"Error getting startup folder path: {e}")
            return None
    
    def create_startup_shortcut(self) -> bool:
        """
        Create a shortcut in the Windows Startup folder (alternative method)
        Requires pywin32 package
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # This requires pywin32, which might not be installed
            # We'll use the registry method instead
            import win32com.client
            
            startup_folder = self.get_startup_folder_path()
            if not startup_folder:
                return False
            
            shortcut_path = startup_folder / f"{self.APP_NAME}.lnk"
            target_path = self._get_executable_path()
            
            # Create shortcut
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(str(shortcut_path))
            shortcut.TargetPath = target_path
            shortcut.WorkingDirectory = str(Path(target_path).parent)
            shortcut.IconLocation = target_path
            shortcut.save()
            
            self._logger.info(f"Created startup shortcut: {shortcut_path}")
            return True
        
        except ImportError:
            self._logger.warning("pywin32 not installed, cannot create shortcut. Using registry method instead.")
            return False
        
        except Exception as e:
            self._logger.error(f"Error creating startup shortcut: {e}", exc_info=True)
            return False
    
    def remove_startup_shortcut(self) -> bool:
        """
        Remove the startup folder shortcut (alternative method)
        
        Returns:
            True if successful, False otherwise
        """
        try:
            startup_folder = self.get_startup_folder_path()
            if not startup_folder:
                return False
            
            shortcut_path = startup_folder / f"{self.APP_NAME}.lnk"
            
            if shortcut_path.exists():
                shortcut_path.unlink()
                self._logger.info(f"Removed startup shortcut: {shortcut_path}")
                return True
            else:
                self._logger.debug("Startup shortcut doesn't exist")
                return True
        
        except Exception as e:
            self._logger.error(f"Error removing startup shortcut: {e}", exc_info=True)
            return False
