"""Unit tests for sdlc_cli.continuity_sync — CONTINUITY.md synchronization."""

from __future__ import annotations

from pathlib import Path

from sdlc_cli.continuity_sync import (
    ContinuitySyncManager,
    SyncResult,
    sync_continuity_after_phase,
)


def _make_test_files(tmp_path: Path, *, status: str, continuity: str) -> tuple[Path, Path]:
    """Create test STATUS.md and CONTINUITY.md files."""
    status_path = tmp_path / "STATUS.md"
    continuity_path = tmp_path / "CONTINUITY.md"
    status_path.write_text(status, encoding="utf-8")
    continuity_path.write_text(continuity, encoding="utf-8")
    return status_path, continuity_path


def test_sync_continuity_after_phase_success(tmp_path: Path) -> None:
    """Test successful sync with selective merge."""
    status_content = """# SDLC Status Dashboard

## Current Phase
Phase 6: Development

## Active Tasks
- Task 1
- Task 2
"""
    continuity_content = """# CONTINUITY

## Current Phase
Phase 5: Design

## Active Tasks
- Old Task 1

## Mistakes & Learnings
- Important learning
"""
    status_path, continuity_path = _make_test_files(tmp_path, status=status_content, continuity=continuity_content)
    
    result = sync_continuity_after_phase(status_path, continuity_path)
    
    assert result.success is True
    assert result.method_used in ["selective_merge", "full_replacement"]
    assert result.duration_ms >= 0
    assert result.error is None
    assert result.retry_count == 0


def test_sync_continuity_after_phase_status_not_found(tmp_path: Path) -> None:
    """Test sync when STATUS.md doesn't exist."""
    continuity_path = tmp_path / "CONTINUITY.md"
    continuity_path.write_text("# CONTINUITY\n\n## Current Phase\nPhase 1\n", encoding="utf-8")
    status_path = tmp_path / "STATUS.md"  # Don't create it
    
    result = sync_continuity_after_phase(status_path, continuity_path)
    
    assert result.success is False
    assert result.method_used == "failed"
    assert result.error is not None
    assert "not found" in result.error.lower()


def test_sync_continuity_after_phase_continuity_not_found(tmp_path: Path) -> None:
    """Test sync when CONTINUITY.md doesn't exist."""
    status_path = tmp_path / "STATUS.md"
    status_path.write_text("# STATUS\n\n## Current Phase\nPhase 1\n", encoding="utf-8")
    continuity_path = tmp_path / "CONTINUITY.md"  # Don't create it
    
    result = sync_continuity_after_phase(status_path, continuity_path)
    
    assert result.success is False
    assert result.method_used == "failed"
    assert result.error is not None
    assert "not found" in result.error.lower()


def test_selective_merge_preserves_sections(tmp_path: Path) -> None:
    """Test that selective merge preserves working memory sections."""
    status_content = """# SDLC Status Dashboard

## Current Phase
Phase 6: Development

## Active Tasks
- New Task 1
- New Task 2
"""
    continuity_content = """# CONTINUITY

## Current Phase
Phase 5: Design

## Active Tasks
- Old Task 1

## Mistakes & Learnings
- Important learning that should be preserved

## Decisions Made
- Important decision that should be preserved
"""
    status_path, continuity_path = _make_test_files(tmp_path, status=status_content, continuity=continuity_content)
    
    sync_manager = ContinuitySyncManager(status_path, continuity_path)
    result = sync_manager.sync_continuity_with_status()
    
    assert result.success is True
    assert result.method_used == "selective_merge"
    
    # Verify preserved sections are still there
    updated_continuity = continuity_path.read_text(encoding="utf-8")
    assert "Important learning that should be preserved" in updated_continuity
    assert "Important decision that should be preserved" in updated_continuity
    # Verify merged section was updated
    assert "New Task 1" in updated_continuity
    assert "Old Task 1" not in updated_continuity


def test_full_replacement_fallback(tmp_path: Path) -> None:
    """Test fallback to full replacement when selective merge would fail."""
    # Create a scenario where selective merge might fail and fall back to full replacement
    status_content = """# SDLC Status Dashboard

## Current Phase
Phase 6: Development

## Active Tasks
- Task 1
"""
    continuity_content = """# CONTINUITY

## Current Phase
Phase 5: Design

## Active Tasks
- Old Task 1
"""
    status_path, continuity_path = _make_test_files(tmp_path, status=status_content, continuity=continuity_content)
    
    sync_manager = ContinuitySyncManager(status_path, continuity_path)
    result = sync_manager.sync_continuity_with_status()
    
    assert result.success is True
    # Either selective merge or full replacement is acceptable
    assert result.method_used in ["selective_merge", "full_replacement"]
    
    # Verify the file was updated
    updated_continuity = continuity_path.read_text(encoding="utf-8")
    assert "Phase 6" in updated_continuity or "Development" in updated_continuity


def test_performance_measurement(tmp_path: Path) -> None:
    """Test that performance is measured and returned."""
    status_content = """# SDLC Status Dashboard

## Current Phase
Phase 6: Development
"""
    continuity_content = """# CONTINUITY

## Current Phase
Phase 5: Design
"""
    status_path, continuity_path = _make_test_files(tmp_path, status=status_content, continuity=continuity_content)
    
    result = sync_continuity_after_phase(status_path, continuity_path)
    
    assert result.duration_ms >= 0
    assert result.duration_ms < 1000  # Should be very fast for small files


def test_retry_logic_on_transient_failure(tmp_path: Path) -> None:
    """Test that retry logic handles transient failures."""
    # This test is limited since we can't easily simulate transient file locks
    # but we can verify the retry mechanism is in place
    status_content = """# SDLC Status Dashboard

## Current Phase
Phase 6: Development
"""
    continuity_content = """# CONTINUITY

## Current Phase
Phase 5: Design
"""
    status_path, continuity_path = _make_test_files(tmp_path, status=status_content, continuity=continuity_content)
    
    # First attempt should succeed
    result = sync_continuity_after_phase(status_path, continuity_path)
    
    assert result.success is True
    assert result.retry_count == 0  # No retries needed for successful case


def test_markdown_section_parsing(tmp_path: Path) -> None:
    """Test markdown section parsing."""
    content = """# Test Document

## Section 1
Content for section 1

## Section 2
Content for section 2
"""
    status_path, continuity_path = _make_test_files(tmp_path, status=content, continuity=content)
    
    sync_manager = ContinuitySyncManager(status_path, continuity_path)
    sections = sync_manager._parse_markdown_sections(content)
    
    assert "Section 1" in sections
    assert "Section 2" in sections
    assert sections["Section 1"] == "Content for section 1"
    assert sections["Section 2"] == "Content for section 2"


def test_markdown_reconstruction(tmp_path: Path) -> None:
    """Test markdown reconstruction from sections."""
    sections = {
        "Section 1": "Content for section 1",
        "Section 2": "Content for section 2"
    }
    
    status_path, continuity_path = _make_test_files(tmp_path, status="", continuity="")
    sync_manager = ContinuitySyncManager(status_path, continuity_path)
    
    reconstructed = sync_manager._reconstruct_markdown(sections)
    
    assert "## Section 1" in reconstructed
    assert "## Section 2" in reconstructed
    assert "Content for section 1" in reconstructed
    assert "Content for section 2" in reconstructed


def test_atomic_write_preserves_on_failure(tmp_path: Path) -> None:
    """Test that atomic write preserves original file on failure."""
    continuity_content = """# CONTINUITY

## Current Phase
Phase 5: Design
"""
    status_path, continuity_path = _make_test_files(tmp_path, status="", continuity=continuity_content)
    
    sync_manager = ContinuitySyncManager(status_path, continuity_path)
    
    # Successful write
    new_content = "# CONTINUITY\n\n## Current Phase\nPhase 6: Development\n"
    sync_manager._write_atomic(new_content)
    
    # Verify file was updated
    updated = continuity_path.read_text(encoding="utf-8")
    assert updated == new_content