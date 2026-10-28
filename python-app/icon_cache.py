import os
import time
from pathlib import Path
from typing import Optional

class IconCache:
    def __init__(self, cache_dir: str = "static/icon-cache", max_size_mb: int = 10):
        self.cache_dir = Path(cache_dir)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._ensure_cache_dir()

    def _ensure_cache_dir(self):
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, icon_name: str) -> Path:
        """Get the full path for a cached icon."""
        return self.cache_dir / f"{icon_name}.svg"

    def get(self, icon_name: str) -> Optional[str]:
        """
        Get icon from cache.
        Returns the file path if found, None otherwise.
        """
        cache_path = self._get_cache_path(icon_name)
        if cache_path.exists():
            return str(cache_path)
        return None

    def put(self, icon_name: str, svg_content: str) -> str:
        """
        Save icon to cache.
        Returns the file path where the icon was saved.
        """
        cache_path = self._get_cache_path(icon_name)
        
        # Check if we need to make space before saving
        self._enforce_size_limit(len(svg_content.encode('utf-8')))
        
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        
        return str(cache_path)

    def _get_total_size(self) -> int:
        """Calculate total size of all files in cache."""
        total = 0
        for file_path in self.cache_dir.glob("*.svg"):
            total += file_path.stat().st_size
        return total

    def _enforce_size_limit(self, new_file_size: int):
        """
        Enforce size limit by deleting oldest files if necessary.
        Uses FIFO (oldest by modification time).
        """
        current_size = self._get_total_size()
        
        if current_size + new_file_size <= self.max_size_bytes:
            return
        
        # Get all SVG files with their modification times
        files_with_times = []
        for file_path in self.cache_dir.glob("*.svg"):
            files_with_times.append((file_path, file_path.stat().st_mtime))
        
        # Sort by modification time (oldest first)
        files_with_times.sort(key=lambda x: x[1])
        
        # Delete oldest files until we have enough space
        for file_path, _ in files_with_times:
            if current_size + new_file_size <= self.max_size_bytes:
                break
            
            file_size = file_path.stat().st_size
            file_path.unlink()
            current_size -= file_size
