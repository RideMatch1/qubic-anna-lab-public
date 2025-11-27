"""Shared utilities for report writing to reduce code duplication."""
from pathlib import Path
from analysis.utils.data_loader import ensure_directory

def ensure_report_dir(report_path: Path) -> None:
 """Ensure the report directory exists."""
 ensure_directory(report_path.parent)

def write_markdown_report(report_path: Path, lines: list[str]) -> None:
 """Write a markdown report to disk.
 
 Args:
 report_path: Path where the report should be written
 lines: List of strings (lines) to write
 """
 ensure_report_dir(report_path)
 report_path.write_text('\n'.join(lines), encoding='utf-8')

__all__ = ['ensure_report_dir', 'write_markdown_report']
