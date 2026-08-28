"""CONTINUITY.md synchronization with STATUS.md.

Per ADR-001: Implements selective merge with fallback to full replacement.
Per ADR-002: Log and continue error handling with retry logic.
Per ADR-003: Python standard library only, zero new dependencies.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Sections to merge from STATUS.md to CONTINUITY.md
MERGEABLE_SECTIONS = [
    "Current Phase",
    "Active Tasks",
    "Completed Tasks",
    "Next Steps"
]

# Sections to preserve in CONTINUITY.md (not overwritten)
PRESERVED_SECTIONS = [
    "Mistakes & Learnings",
    "Decisions Made",
    "Open Questions",
    "Blocked Items"
]


@dataclass
class SyncResult:
    """Result of CONTINUITY.md synchronization operation."""
    success: bool
    duration_ms: float
    method_used: str  # "selective_merge" | "full_replacement" | "failed"
    error: Optional[str] = None
    retry_count: int = 0


class ContinuitySyncManager:
    """Manages synchronization between STATUS.md and CONTINUITY.md.
    
    Per ADR-001: Selective merge with fallback to full replacement.
    Per ADR-002: Error handling with retry logic, never raises exceptions.
    """

    def __init__(self, status_path: Path, continuity_path: Path):
        """Initialize the sync manager with file paths.
        
        Args:
            status_path: Path to STATUS.md (read source)
            continuity_path: Path to CONTINUITY.md (write target)
        """
        self.status_path = status_path
        self.continuity_path = continuity_path

    def sync_continuity_with_status(self) -> SyncResult:
        """Main synchronization method with error handling per ADR-002.
        
        Returns:
            SyncResult with success status and timing information
        """
        start_time = time.time()
        retry_count = 0
        max_retries = 3
        
        for attempt in range(max_retries):
            try:
                return self._attempt_sync()
            except Exception as e:
                retry_count = attempt + 1
                self._handle_sync_error(e, retry_count)
                if retry_count == max_retries:
                    duration_ms = (time.time() - start_time) * 1000
                    return SyncResult(
                        success=False,
                        duration_ms=duration_ms,
                        method_used="failed",
                        error=str(e),
                        retry_count=retry_count
                    )
                # Exponential backoff: 1s, 2s, 4s
                backoff = 2 ** (retry_count - 1)
                time.sleep(backoff)

    def _attempt_sync(self) -> SyncResult:
        """Attempt synchronization with selective merge and fallback."""
        start_time = time.time()
        
        # Validate files exist
        if not self.status_path.exists():
            raise FileNotFoundError(f"STATUS.md not found at {self.status_path}")
        
        if not self.continuity_path.exists():
            raise FileNotFoundError(f"CONTINUITY.md not found at {self.continuity_path}")
        
        # Read files
        status_content = self.status_path.read_text(encoding="utf-8")
        continuity_content = self.continuity_path.read_text(encoding="utf-8")
        
        # Try selective merge first
        try:
            merged_content = self._selective_merge(status_content, continuity_content)
            self._write_atomic(merged_content)
            duration_ms = (time.time() - start_time) * 1000
            return SyncResult(
                success=True,
                duration_ms=duration_ms,
                method_used="selective_merge"
            )
        except Exception as e:
            logger.warning(f"Selective merge failed: {e}. Falling back to full replacement.")
            # Fallback to full replacement
            try:
                success = self._full_replacement(status_content)
                duration_ms = (time.time() - start_time) * 1000
                return SyncResult(
                    success=success,
                    duration_ms=duration_ms,
                    method_used="full_replacement"
                )
            except Exception as e2:
                raise Exception(f"Full replacement also failed: {e2}")

    def _validate_compatibility(self) -> bool:
        """Pre-sync validation per ADR-001.
        
        Checks if STATUS.md structure is compatible with CONTINUITY.md.
        For now, this is a lightweight check - full validation is done during merge.
        """
        # Basic check: both files should be markdown with headers
        if not self.status_path.exists() or not self.continuity_path.exists():
            return False
        return True

    def _selective_merge(self, status_content: str, continuity_content: str) -> str:
        """Selective merge implementation per ADR-001.
        
        Merges specific sections from STATUS.md into CONTINUITY.md
        while preserving working memory structure.
        
        Args:
            status_content: Raw STATUS.md content
            continuity_content: Raw CONTINUITY.md content
            
        Returns:
            Merged markdown content
        """
        # Parse both files into section dictionaries
        status_sections = self._parse_markdown_sections(status_content)
        continuity_sections = self._parse_markdown_sections(continuity_content)
        
        # Apply selective merge
        for section in MERGEABLE_SECTIONS:
            if section in status_sections:
                continuity_sections[section] = status_sections[section]
        
        # Reconstruct markdown from merged sections
        return self._reconstruct_markdown(continuity_sections)

    def _full_replacement(self, status_content: str) -> bool:
        """Fallback full replacement per ADR-001.
        
        Used when selective merge fails or is not applicable.
        
        Args:
            status_content: Raw STATUS.md content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self._write_atomic(status_content)
            return True
        except Exception as e:
            logger.error(f"Full replacement failed: {e}")
            return False

    def _handle_sync_error(self, error: Exception, attempt: int) -> None:
        """Error handling with retry logic per ADR-002."""
        logger.warning(
            f"Sync attempt {attempt} failed: {error}. "
            f"Retrying with exponential backoff..."
        )

    def _parse_markdown_sections(self, content: str) -> dict[str, str]:
        """Parse markdown content into section dictionary.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Dictionary mapping section headers to their content
        """
        sections = {}
        lines = content.splitlines()
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith("## "):
                # Save previous section
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                # Start new section
                current_section = line[3:].strip()  # Remove "## "
                current_content = []
            else:
                if current_section:
                    current_content.append(line)
        
        # Save last section
        if current_section:
            sections[current_section] = "\n".join(current_content).strip()
        
        return sections

    def _reconstruct_markdown(self, sections: dict[str, str]) -> str:
        """Reconstruct markdown from section dictionary.
        
        Args:
            sections: Dictionary of section headers to content
            
        Returns:
            Reconstructed markdown content
        """
        lines = []
        for header, content in sections.items():
            lines.append(f"## {header}")
            lines.append("")
            lines.append(content)
            lines.append("")
        return "\n".join(lines)

    def _write_atomic(self, content: str) -> None:
        """Atomic write operation using temp file pattern.
        
        Args:
            content: Content to write
        """
        temp_path = self.continuity_path.with_suffix(".tmp")
        try:
            temp_path.write_text(content, encoding="utf-8")
            temp_path.replace(self.continuity_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()


def sync_continuity_after_phase(
    status_path: Path,
    continuity_path: Path,
    logger_instance: Optional[logging.Logger] = None
) -> SyncResult:
    """Synchronizes CONTINUITY.md with STATUS.md after phase completion.
    
    Per ADR-001: Implements selective merge with fallback to full replacement
    Per ADR-002: Does not raise exceptions, handles all errors gracefully
    
    Args:
        status_path: Path to STATUS.md (read source)
        continuity_path: Path to CONTINUITY.md (write target)
        logger_instance: Logger instance for error reporting (optional)
    
    Returns:
        SyncResult containing:
        - success: bool
        - duration_ms: float
        - method_used: "selective_merge" | "full_replacement" | "failed"
        - error: Optional[str]
    
    Raises:
        Does not raise - all errors handled per ADR-002
    """
    if logger_instance is None:
        logger_instance = logging.getLogger(__name__)
    
    sync_manager = ContinuitySyncManager(status_path, continuity_path)
    result = sync_manager.sync_continuity_with_status()
    
    if result.success:
        logger_instance.info(
            f"CONTINUITY.md sync successful via {result.method_used} "
            f"({result.duration_ms:.2f}ms)"
        )
    else:
        logger_instance.warning(
            f"CONTINUITY.md sync failed after {result.retry_count} attempts: "
            f"{result.error}. Continuing per ADR-002."
        )
    
    return result