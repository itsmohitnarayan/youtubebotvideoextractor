"""
Unit tests for Windows Auto-Start Manager
Tests registry operations for Windows startup
"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from src.utils.autostart import AutoStartManager


class TestAutoStartManager:
    """Test AutoStartManager class"""
    
    def setup_method(self):
        """Setup for each test"""
        self.manager = AutoStartManager()
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    @patch('winreg.CloseKey')
    @patch.object(AutoStartManager, '_get_executable_path')
    def test_is_enabled_true(self, mock_get_exe, mock_close, mock_query, mock_open):
        """Test checking if auto-start is enabled"""
        # Mock both registry and exe path to match
        test_path = 'C:\\test\\app.exe'
        mock_get_exe.return_value = test_path
        mock_query.return_value = (test_path, None)
        
        result = self.manager.is_enabled()
        
        assert result is True
        mock_open.assert_called_once()
        mock_query.assert_called_once()
        mock_close.assert_called_once()
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    @patch('winreg.CloseKey')
    def test_is_enabled_false(self, mock_close, mock_query, mock_open):
        """Test checking when auto-start is disabled"""
        # Mock registry key doesn't exist
        mock_query.side_effect = FileNotFoundError()
        
        result = self.manager.is_enabled()
        
        assert result is False
        mock_close.assert_called_once()
    
    @patch('winreg.OpenKey')
    @patch('winreg.QueryValueEx')
    @patch('winreg.CloseKey')
    def test_is_enabled_different_path(self, mock_close, mock_query, mock_open):
        """Test when registry has different exe path"""
        # Mock registry returns different path
        mock_query.return_value = ('C:\\different\\path\\app.exe', None)
        
        result = self.manager.is_enabled()
        
        assert result is False
    
    @patch('winreg.OpenKey')
    @patch('winreg.SetValueEx')
    @patch('winreg.CloseKey')
    def test_enable(self, mock_close, mock_set, mock_open):
        """Test enabling auto-start"""
        result = self.manager.enable()
        
        assert result is True
        mock_open.assert_called_once()
        mock_set.assert_called_once()
        mock_close.assert_called_once()
        
        # Verify correct registry value was set
        call_args = mock_set.call_args
        assert call_args[0][1] == 'YouTubeBotVideoExtractor'  # Key name
    
    @patch('winreg.OpenKey')
    @patch('winreg.SetValueEx')
    def test_enable_error(self, mock_set, mock_open):
        """Test enable with registry error"""
        mock_open.side_effect = Exception("Registry error")
        
        result = self.manager.enable()
        
        assert result is False
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    @patch('winreg.CloseKey')
    def test_disable(self, mock_close, mock_delete, mock_open):
        """Test disabling auto-start"""
        result = self.manager.disable()
        
        assert result is True
        mock_open.assert_called_once()
        mock_delete.assert_called_once_with(mock_open.return_value, 'YouTubeBotVideoExtractor')
        mock_close.assert_called_once()
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    @patch('winreg.CloseKey')
    def test_disable_already_disabled(self, mock_close, mock_delete, mock_open):
        """Test disabling when already disabled"""
        # Mock that registry value doesn't exist
        mock_delete.side_effect = FileNotFoundError()
        
        result = self.manager.disable()
        
        assert result is True  # Still returns True (idempotent)
        mock_close.assert_called_once()
    
    @patch('winreg.OpenKey')
    @patch('winreg.DeleteValue')
    def test_disable_error(self, mock_delete, mock_open):
        """Test disable with registry error"""
        mock_open.side_effect = Exception("Registry error")
        
        result = self.manager.disable()
        
        assert result is False
    
    @patch.object(AutoStartManager, 'is_enabled')
    @patch.object(AutoStartManager, 'enable')
    @patch.object(AutoStartManager, 'disable')
    def test_toggle_enable(self, mock_disable, mock_enable, mock_is_enabled):
        """Test toggling from disabled to enabled"""
        mock_is_enabled.return_value = False
        mock_enable.return_value = True
        
        result = self.manager.toggle()
        
        assert result is True
        mock_enable.assert_called_once()
        mock_disable.assert_not_called()
    
    @patch.object(AutoStartManager, 'is_enabled')
    @patch.object(AutoStartManager, 'enable')
    @patch.object(AutoStartManager, 'disable')
    def test_toggle_disable(self, mock_disable, mock_enable, mock_is_enabled):
        """Test toggling from enabled to disabled"""
        mock_is_enabled.return_value = True
        mock_disable.return_value = True
        
        result = self.manager.toggle()
        
        assert result is False
        mock_disable.assert_called_once()
        mock_enable.assert_not_called()
    
    def test_get_executable_path_frozen(self):
        """Test getting exe path when running as compiled executable"""
        with patch.object(sys, 'frozen', True, create=True):
            with patch.object(sys, 'executable', 'C:\\app\\myapp.exe'):
                path = self.manager._get_executable_path()
                
                assert path == 'C:\\app\\myapp.exe'
    
    def test_get_executable_path_script(self):
        """Test getting exe path when running as Python script"""
        # Ensure frozen attribute doesn't exist
        if hasattr(sys, 'frozen'):
            delattr(sys, 'frozen')
        
        with patch.object(sys, 'executable', 'C:\\Python\\python.exe'):
            with patch.object(sys, 'argv', ['C:\\app\\script.py']):
                path = self.manager._get_executable_path()
                
                # Should use pythonw.exe for silent startup
                assert 'pythonw.exe' in path
                assert 'script.py' in path
    
    def test_get_startup_folder_path(self):
        """Test getting Windows startup folder path"""
        with patch.dict(os.environ, {'APPDATA': 'C:\\Users\\Test\\AppData\\Roaming'}):
            with patch('pathlib.Path.exists', return_value=True):
                path = self.manager.get_startup_folder_path()
                
                assert path is not None
                assert 'Startup' in str(path)
    
    def test_get_startup_folder_path_not_exists(self):
        """Test getting startup folder when it doesn't exist"""
        with patch.dict(os.environ, {'APPDATA': 'C:\\Invalid'}):
            with patch('pathlib.Path.exists', return_value=False):
                path = self.manager.get_startup_folder_path()
                
                assert path is None
    
    def test_get_startup_folder_path_error(self):
        """Test getting startup folder with environment error"""
        with patch.dict(os.environ, {}, clear=True):
            # APPDATA not in environment
            path = self.manager.get_startup_folder_path()
            
            assert path is None
    
    def test_create_startup_shortcut(self):
        """Test creating startup folder shortcut"""
        # Mock the import of win32com within the method
        with patch('builtins.__import__', side_effect=ImportError("No module named 'win32com'")):
            result = self.manager.create_startup_shortcut()
            
            # Should return False gracefully when pywin32 not installed
            assert result is False
    
    def test_create_startup_shortcut_no_pywin32(self):
        """Test creating shortcut without pywin32 installed"""
        # ImportError should be handled gracefully
        result = self.manager.create_startup_shortcut()
        
        # Should return False but not crash
        assert result is False
    
    def test_remove_startup_shortcut(self):
        """Test removing startup folder shortcut"""
        with patch.object(self.manager, 'get_startup_folder_path') as mock_get_path:
            mock_path = MagicMock()
            mock_shortcut = MagicMock()
            mock_shortcut.exists.return_value = True
            mock_path.__truediv__ = lambda self, other: mock_shortcut
            mock_get_path.return_value = mock_path
            
            result = self.manager.remove_startup_shortcut()
            
            assert result is True
            mock_shortcut.unlink.assert_called_once()
    
    def test_remove_startup_shortcut_not_exists(self):
        """Test removing shortcut that doesn't exist"""
        with patch.object(self.manager, 'get_startup_folder_path') as mock_get_path:
            mock_path = MagicMock()
            mock_shortcut = MagicMock()
            mock_shortcut.exists.return_value = False
            mock_path.__truediv__ = lambda self, other: mock_shortcut
            mock_get_path.return_value = mock_path
            
            result = self.manager.remove_startup_shortcut()
            
            assert result is True  # Idempotent
            mock_shortcut.unlink.assert_not_called()
    
    def test_registry_path_constant(self):
        """Test registry path constant"""
        assert AutoStartManager.REGISTRY_PATH == r"Software\Microsoft\Windows\CurrentVersion\Run"
    
    def test_app_name_constant(self):
        """Test application name constant"""
        assert AutoStartManager.APP_NAME == "YouTubeBotVideoExtractor"


@pytest.mark.skipif(sys.platform != 'win32', reason="Windows-only tests")
class TestAutoStartManagerIntegration:
    """Integration tests for AutoStartManager (Windows only)"""
    
    def setup_method(self):
        """Setup for each test"""
        self.manager = AutoStartManager()
        # Clean up any existing registry entry
        self.manager.disable()
    
    def teardown_method(self):
        """Cleanup after each test"""
        # Clean up registry entry
        self.manager.disable()
    
    @pytest.mark.slow
    def test_enable_disable_cycle(self):
        """Test actual registry enable/disable cycle"""
        # Should be disabled initially
        assert self.manager.is_enabled() is False
        
        # Enable
        success = self.manager.enable()
        assert success is True
        assert self.manager.is_enabled() is True
        
        # Disable
        success = self.manager.disable()
        assert success is True
        assert self.manager.is_enabled() is False
    
    @pytest.mark.slow
    def test_toggle_cycle(self):
        """Test actual toggle cycle"""
        # Start disabled
        self.manager.disable()
        
        # Toggle to enabled
        result = self.manager.toggle()
        assert result is True
        assert self.manager.is_enabled() is True
        
        # Toggle to disabled
        result = self.manager.toggle()
        assert result is False
        assert self.manager.is_enabled() is False
