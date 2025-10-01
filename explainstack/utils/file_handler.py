"""File handling utilities for ExplainStack."""

import os
import tempfile
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class FileHandler:
    """Handler for uploaded files and file processing."""
    
    SUPPORTED_EXTENSIONS = {'.py', '.diff', '.patch', '.txt', '.md'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        """Initialize file handler."""
        self.temp_dir = tempfile.mkdtemp(prefix="explainstack_")
        logger.info(f"File handler initialized with temp dir: {self.temp_dir}")
    
    def validate_file(self, file_path: str, file_size: int) -> Tuple[bool, Optional[str]]:
        """Validate uploaded file.
        
        Args:
            file_path: Path to the file
            file_size: Size of the file in bytes
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check file size
            if file_size > self.MAX_FILE_SIZE:
                return False, f"File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB"
            
            # Check file extension
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.SUPPORTED_EXTENSIONS:
                return False, f"Unsupported file type. Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            
            # Check if file exists and is readable
            if not os.path.exists(file_path):
                return False, "File not found"
            
            if not os.access(file_path, os.R_OK):
                return False, "File not readable"
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error validating file {file_path}: {e}")
            return False, f"Validation error: {str(e)}"
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Save uploaded file to temporary directory.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            # Validate file size
            if len(file_content) > self.MAX_FILE_SIZE:
                return False, None, f"File too large. Maximum size: {self.MAX_FILE_SIZE // (1024*1024)}MB"
            
            # Create safe filename
            safe_filename = self._create_safe_filename(filename)
            file_path = os.path.join(self.temp_dir, safe_filename)
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            # Validate saved file
            is_valid, error_msg = self.validate_file(file_path, len(file_content))
            if not is_valid:
                os.remove(file_path)
                return False, None, error_msg
            
            logger.info(f"File saved successfully: {file_path}")
            return True, file_path, None
            
        except Exception as e:
            logger.error(f"Error saving file {filename}: {e}")
            return False, None, f"Error saving file: {str(e)}"
    
    def read_file_content(self, file_path: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Read file content.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (success, content, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            logger.info(f"File content read successfully: {file_path}")
            return True, content, None
            
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                logger.info(f"File content read with latin-1 encoding: {file_path}")
                return True, content, None
            except Exception as e:
                logger.error(f"Error reading file {file_path} with latin-1: {e}")
                return False, None, f"Error reading file: {str(e)}"
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return False, None, f"Error reading file: {str(e)}"
    
    def process_file_for_analysis(self, file_path: str) -> Tuple[bool, Optional[Dict[str, Any]], Optional[str]]:
        """Process file for analysis.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (success, file_info, error_message)
        """
        try:
            # Read file content
            success, content, error_msg = self.read_file_content(file_path)
            if not success:
                return False, None, error_msg
            
            # Get file info
            file_info = {
                'path': file_path,
                'filename': os.path.basename(file_path),
                'size': len(content),
                'extension': Path(file_path).suffix.lower(),
                'content': content,
                'lines': len(content.splitlines())
            }
            
            logger.info(f"File processed successfully: {file_path}")
            return True, file_info, None
            
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {e}")
            return False, None, f"Error processing file: {str(e)}"
    
    def cleanup_temp_files(self):
        """Clean up temporary files."""
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temp directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {e}")
    
    def _create_safe_filename(self, filename: str) -> str:
        """Create a safe filename for storage.
        
        Args:
            filename: Original filename
            
        Returns:
            Safe filename
        """
        import re
        import time
        
        # Remove or replace unsafe characters
        safe_name = re.sub(r'[^\w\-_\.]', '_', filename)
        
        # Add timestamp to avoid conflicts
        timestamp = int(time.time())
        name, ext = os.path.splitext(safe_name)
        return f"{name}_{timestamp}{ext}"
    
    def get_supported_extensions(self) -> List[str]:
        """Get list of supported file extensions.
        
        Returns:
            List of supported extensions
        """
        return list(self.SUPPORTED_EXTENSIONS)
    
    def get_max_file_size(self) -> int:
        """Get maximum file size in bytes.
        
        Returns:
            Maximum file size in bytes
        """
        return self.MAX_FILE_SIZE
