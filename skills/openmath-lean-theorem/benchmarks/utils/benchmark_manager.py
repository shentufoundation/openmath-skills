#!/usr/bin/env python3
"""
Benchmark manager for loading and managing LEAN4 benchmarks.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from config import BENCHMARK_DIR, METADATA_FILE, SORRY_PATTERN


@dataclass
class Benchmark:
    """Represents a single benchmark."""
    benchmark_id: str
    file_path: Path
    difficulty: str
    topic: str
    description: str
    lemmas: List[str]
    expected_time_ms: int
    tags: List[str]
    
    def get_full_path(self) -> Path:
        """Get the full path to the benchmark file."""
        return BENCHMARK_DIR / self.file_path
    
    def exists(self) -> bool:
        """Check if the benchmark file exists."""
        return self.get_full_path().exists()


class BenchmarkManager:
    """Manages loading and filtering benchmarks."""
    
    def __init__(self):
        self.benchmarks: List[Benchmark] = []
        self.metadata: Dict = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load benchmark metadata from JSON file."""
        if not METADATA_FILE.exists():
            raise FileNotFoundError(f"Metadata file not found: {METADATA_FILE}")
        
        with open(METADATA_FILE, 'r') as f:
            data = json.load(f)
        
        self.metadata = data.get('metadata', {})
        
        for bench_data in data.get('benchmarks', []):
            benchmark = Benchmark(
                benchmark_id=bench_data['benchmark_id'],
                file_path=Path(bench_data['file_path']),
                difficulty=bench_data['difficulty'],
                topic=bench_data['topic'],
                description=bench_data['description'],
                lemmas=bench_data['lemmas'],
                expected_time_ms=bench_data['expected_time_ms'],
                tags=bench_data.get('tags', [])
            )
            self.benchmarks.append(benchmark)
    
    def get_all_benchmarks(self) -> List[Benchmark]:
        """Get all benchmarks."""
        return self.benchmarks
    
    def get_by_difficulty(self, difficulty: str) -> List[Benchmark]:
        """Get benchmarks by difficulty level."""
        return [b for b in self.benchmarks if b.difficulty == difficulty]
    
    def get_by_topic(self, topic: str) -> List[Benchmark]:
        """Get benchmarks by topic."""
        return [b for b in self.benchmarks if b.topic == topic]
    
    def get_by_id(self, benchmark_id: str) -> Optional[Benchmark]:
        """Get a specific benchmark by ID."""
        for b in self.benchmarks:
            if b.benchmark_id == benchmark_id:
                return b
        return None
    
    def filter_benchmarks(self, difficulty: Optional[str] = None, 
                         topic: Optional[str] = None,
                         tags: Optional[List[str]] = None) -> List[Benchmark]:
        """Filter benchmarks by various criteria."""
        filtered = self.benchmarks
        
        if difficulty:
            filtered = [b for b in filtered if b.difficulty == difficulty]
        
        if topic:
            filtered = [b for b in filtered if b.topic == topic]
        
        if tags:
            filtered = [b for b in filtered 
                       if any(tag in b.tags for tag in tags)]
        
        return filtered
    
    @staticmethod
    def has_sorry(file_path: Path) -> bool:
        """Check if a LEAN file contains 'sorry'."""
        try:
            content = file_path.read_text()
            return bool(re.search(SORRY_PATTERN, content))
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return False
    
    @staticmethod
    def extract_lemmas(file_path: Path) -> List[str]:
        """Extract lemma names from a LEAN file."""
        lemmas = []
        try:
            content = file_path.read_text()
            # Match lemma and theorem declarations
            pattern = r'(?:lemma|theorem)\s+(\w+)'
            matches = re.findall(pattern, content)
            lemmas.extend(matches)
        except Exception as e:
            print(f"Error extracting lemmas from {file_path}: {e}")
        
        return lemmas
    
    def validate_benchmarks(self) -> Dict[str, List[str]]:
        """Validate all benchmarks and return issues."""
        issues = {
            'missing_files': [],
            'mismatched_lemmas': [],
            'no_sorry': []
        }
        
        for benchmark in self.benchmarks:
            full_path = benchmark.get_full_path()
            
            # Check if file exists
            if not benchmark.exists():
                issues['missing_files'].append(benchmark.benchmark_id)
                continue
            
            # Check for sorry
            if not self.has_sorry(full_path):
                issues['no_sorry'].append(benchmark.benchmark_id)
            
            # Check lemmas match
            actual_lemmas = self.extract_lemmas(full_path)
            if set(actual_lemmas) != set(benchmark.lemmas):
                issues['mismatched_lemmas'].append(
                    f"{benchmark.benchmark_id}: expected {benchmark.lemmas}, found {actual_lemmas}"
                )
        
        return issues


if __name__ == "__main__":
    # Test the benchmark manager
    manager = BenchmarkManager()
    print(f"Loaded {len(manager.benchmarks)} benchmarks")
    
    print("\nValidating benchmarks...")
    issues = manager.validate_benchmarks()
    has_issues = False
    for issue_type, issue_list in issues.items():
        if issue_list:
            has_issues = True
            print(f"\n{issue_type}:")
            for issue in issue_list:
                print(f"  - {issue}")
    if not has_issues:
        print("All benchmarks valid!")
