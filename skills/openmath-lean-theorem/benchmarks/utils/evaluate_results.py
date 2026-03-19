#!/usr/bin/env python3

"""
Script to analyze and summarize benchmark test results.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from collections import defaultdict

from config import RESULTS_DIR


class ResultsEvaluator:
    """Analyzes and summarizes benchmark results."""
    
    def __init__(self):
        self.results_files: List[Path] = []
        self.results_data: List[Dict] = []
    
    def load_results(self, pattern: str = "results_*.json"):
        """Load all result files matching the pattern."""
        self.results_files = sorted(RESULTS_DIR.glob(pattern))
        
        for file in self.results_files:
            try:
                with open(file, 'r') as f:
                    data = json.load(f)
                    self.results_data.append(data)
            except Exception as e:
                print(f"Error loading {file}: {e}")
        
        print(f"Loaded {len(self.results_data)} result file(s)")
    
    def print_latest_summary(self):
        """Print summary of the latest results."""
        if not self.results_data:
            print("No results to analyze")
            return
        
        latest = self.results_data[-1]
        metadata = latest['run_metadata']
        
        print("\n" + "="*70)
        print("LATEST BENCHMARK RESULTS")
        print("="*70)
        print(f"Timestamp:        {metadata['timestamp']}")
        print(f"LEAN Version:     {metadata['lean_version']}")
        print(f"Total Benchmarks: {metadata['total_benchmarks']}")
        print(f"Passed:           {metadata['total_passed']} ({self._percentage(metadata['total_passed'], metadata['total_benchmarks'])}%)")
        print(f"Failed:           {metadata['total_failed']} ({self._percentage(metadata['total_failed'], metadata['total_benchmarks'])}%)")
        print(f"Errors:           {metadata['total_errors']} ({self._percentage(metadata['total_errors'], metadata['total_benchmarks'])}%)")
        print(f"Total Time:       {metadata['total_time_ms']:.2f}ms")
        print(f"Wall Time:        {metadata['wall_time_seconds']:.2f}s")
        print(f"Total Memory:     {metadata['total_memory_mb']:.2f}MB")
        print("="*70)
        
        # Break down by difficulty
        self._print_breakdown_by_category(latest['results'], "difficulty")
        
        # Break down by topic
        self._print_breakdown_by_category(latest['results'], "topic")
        
        # Show individual results
        self._print_individual_results(latest['results'])
    
    def _print_breakdown_by_category(self, results: List[Dict], category: str):
        """Print results breakdown by a category (difficulty or topic)."""
        category_stats = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0, 'errors': 0, 'time': 0})
        
        for result in results:
            cat_value = result.get(category, 'unknown')
            category_stats[cat_value]['total'] += 1
            category_stats[cat_value]['time'] += result.get('compilation_time_ms', 0)
            
            status = result.get('status', 'unknown')
            if status == 'success':
                category_stats[cat_value]['passed'] += 1
            elif status == 'failure':
                category_stats[cat_value]['failed'] += 1
            elif status == 'error':
                category_stats[cat_value]['errors'] += 1
        
        if category_stats:
            print(f"\nBreakdown by {category.upper()}:")
            print("-" * 70)
            for cat_value, stats in sorted(category_stats.items()):
                pass_rate = self._percentage(stats['passed'], stats['total'])
                avg_time = stats['time'] / stats['total'] if stats['total'] > 0 else 0
                print(f"{cat_value:15} | Total: {stats['total']:2} | Passed: {stats['passed']:2} ({pass_rate:5.1f}%) | "
                      f"Failed: {stats['failed']:2} | Errors: {stats['errors']:2} | Avg Time: {avg_time:7.2f}ms")
    
    def _print_individual_results(self, results: List[Dict]):
        """Print individual benchmark results."""
        print("\nIndividual Results:")
        print("-" * 70)
        
        for result in results:
            status_symbol = self._get_status_symbol(result['status'])
            print(f"{status_symbol} {result['benchmark_id']:25} | {result['difficulty']:6} | "
                  f"{result['topic']:12} | {result['compilation_time_ms']:7.2f}ms | "
                  f"{result['memory_usage_mb']:6.2f}MB")
            
            if result.get('error_message'):
                print(f"  Error: {result['error_message']}")
    
    def compare_results(self):
        """Compare multiple result files."""
        if len(self.results_data) < 2:
            print("Need at least 2 result files for comparison")
            return
        
        print("\n" + "="*70)
        print("RESULTS COMPARISON")
        print("="*70)
        
        # Compare metadata
        print("\nRun Metadata:")
        print(f"{'Metric':<20} | " + " | ".join([f"Run {i+1:2}" for i in range(len(self.results_data))]))
        print("-" * 70)
        
        metrics = ['total_benchmarks', 'total_passed', 'total_failed', 'total_errors', 
                   'total_time_ms', 'wall_time_seconds', 'total_memory_mb']
        
        for metric in metrics:
            values = [str(data['run_metadata'].get(metric, 'N/A')) for data in self.results_data]
            print(f"{metric:<20} | " + " | ".join([f"{v:>6}" for v in values]))
        
        # Track improvements
        self._print_improvements()
    
    def _print_improvements(self):
        """Print improvements between runs."""
        if len(self.results_data) < 2:
            return
        
        print("\nImprovements (Latest vs First):")
        print("-" * 70)
        
        first = self.results_data[0]['run_metadata']
        latest = self.results_data[-1]['run_metadata']
        
        # Pass rate change
        first_pass_rate = self._percentage(first['total_passed'], first['total_benchmarks'])
        latest_pass_rate = self._percentage(latest['total_passed'], latest['total_benchmarks'])
        pass_rate_diff = latest_pass_rate - first_pass_rate
        
        print(f"Pass Rate:     {first_pass_rate:.1f}% → {latest_pass_rate:.1f}% ({pass_rate_diff:+.1f}%)")
        
        # Time change
        if first['total_benchmarks'] > 0 and latest['total_benchmarks'] > 0:
            first_avg_time = first['total_time_ms'] / first['total_benchmarks']
            latest_avg_time = latest['total_time_ms'] / latest['total_benchmarks']
            time_diff = ((latest_avg_time - first_avg_time) / first_avg_time * 100) if first_avg_time > 0 else 0
            
            print(f"Avg Time:      {first_avg_time:.2f}ms → {latest_avg_time:.2f}ms ({time_diff:+.1f}%)")
    
    def generate_performance_report(self):
        """Generate detailed performance report."""
        if not self.results_data:
            print("No results to analyze")
            return
        
        latest = self.results_data[-1]
        results = latest['results']
        
        print("\n" + "="*70)
        print("PERFORMANCE REPORT")
        print("="*70)
        
        # Time statistics
        times = [r['compilation_time_ms'] for r in results if r.get('compilation_time_ms')]
        if times:
            print(f"\nCompilation Time Statistics:")
            print(f"  Min:    {min(times):.2f}ms")
            print(f"  Max:    {max(times):.2f}ms")
            print(f"  Mean:   {sum(times)/len(times):.2f}ms")
            print(f"  Median: {sorted(times)[len(times)//2]:.2f}ms")
        
        # Memory statistics
        memory = [r['memory_usage_mb'] for r in results if r.get('memory_usage_mb')]
        if memory:
            print(f"\nMemory Usage Statistics:")
            print(f"  Min:    {min(memory):.2f}MB")
            print(f"  Max:    {max(memory):.2f}MB")
            print(f"  Mean:   {sum(memory)/len(memory):.2f}MB")
            print(f"  Median: {sorted(memory)[len(memory)//2]:.2f}MB")
        
        # Slowest benchmarks
        slowest = sorted(results, key=lambda x: x.get('compilation_time_ms', 0), reverse=True)[:5]
        print(f"\nSlowest Benchmarks:")
        for i, r in enumerate(slowest, 1):
            print(f"  {i}. {r['benchmark_id']:30} {r['compilation_time_ms']:7.2f}ms")
        
        # Most memory intensive
        memory_intensive = sorted(results, key=lambda x: x.get('memory_usage_mb', 0), reverse=True)[:5]
        print(f"\nMost Memory Intensive:")
        for i, r in enumerate(memory_intensive, 1):
            print(f"  {i}. {r['benchmark_id']:30} {r['memory_usage_mb']:7.2f}MB")
    
    @staticmethod
    def _percentage(part: int, total: int) -> float:
        """Calculate percentage."""
        return (part / total * 100) if total > 0 else 0.0
    
    @staticmethod
    def _get_status_symbol(status: str) -> str:
        """Get symbol for status."""
        symbols = {
            'success': '✓',
            'failure': '✗',
            'error': '⚠'
        }
        return symbols.get(status, '?')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze and summarize benchmark test results"
    )
    parser.add_argument(
        '--pattern',
        default='results_*.json',
        help='Pattern to match result files (default: results_*.json)'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare multiple result files'
    )
    parser.add_argument(
        '--report',
        choices=['summary', 'performance'],
        default='summary',
        help='Type of report to generate'
    )
    
    args = parser.parse_args()
    
    evaluator = ResultsEvaluator()
    evaluator.load_results(args.pattern)
    
    if args.compare:
        evaluator.compare_results()
    elif args.report == 'performance':
        evaluator.generate_performance_report()
    else:
        evaluator.print_latest_summary()


if __name__ == "__main__":
    main()
