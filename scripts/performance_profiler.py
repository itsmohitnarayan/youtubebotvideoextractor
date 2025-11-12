"""
Performance Profiling Script
Measures and reports application performance metrics

Metrics Tracked:
1. Startup time (target: <3s)
2. Memory usage (target: <150MB idle)
3. CPU usage (target: <5% idle, <40% active)
4. Database query performance
5. GUI responsiveness
"""

import sys
import os
import time
import psutil
import json
import tracemalloc
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import threading
import statistics

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import DatabaseManager
from src.core.config import ConfigManager
from src.core.events import EventBus
from src.core.queue_manager import VideoProcessingQueue


class PerformanceProfiler:
    """Measures and reports application performance metrics"""
    
    def __init__(self, output_dir: str = "performance_reports"):
        """
        Initialize performance profiler
        
        Args:
            output_dir: Directory to save performance reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.process = psutil.Process()
        self.results: Dict[str, Any] = {
            'timestamp': datetime.now().isoformat(),
            'metrics': {}
        }
        
    def measure_startup_time(self, iterations: int = 5) -> Dict[str, float]:
        """
        Measure application startup time
        
        Args:
            iterations: Number of measurements to average
            
        Returns:
            Dictionary with startup metrics
        """
        print(f"\n📊 Measuring Startup Time ({iterations} iterations)...")
        
        startup_times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            # Simulate startup components
            # 1. Load configuration
            config = ConfigManager("config.example.json")
            
            # 2. Initialize database
            db = DatabaseManager(":memory:")
            
            # 3. Create event bus
            event_bus = EventBus()
            
            # 4. Create queue manager
            queue = VideoProcessingQueue()
            
            # Cleanup
            db.close()
            
            elapsed = time.time() - start_time
            startup_times.append(elapsed)
            print(f"  Iteration {i+1}: {elapsed:.3f}s")
        
        avg_time = statistics.mean(startup_times)
        min_time = min(startup_times)
        max_time = max(startup_times)
        
        result = {
            'average': avg_time,
            'min': min_time,
            'max': max_time,
            'target': 3.0,
            'passes': avg_time < 3.0,
            'iterations': startup_times
        }
        
        print(f"\n  Average: {avg_time:.3f}s (Target: <3.0s) {'✅' if result['passes'] else '❌'}")
        print(f"  Min: {min_time:.3f}s, Max: {max_time:.3f}s")
        
        self.results['metrics']['startup_time'] = result
        return result
    
    def measure_memory_usage(self, duration: int = 10) -> Dict[str, float]:
        """
        Measure memory usage over time
        
        Args:
            duration: How long to monitor (seconds)
            
        Returns:
            Dictionary with memory metrics (in MB)
        """
        print(f"\n📊 Measuring Memory Usage (idle for {duration}s)...")
        
        # Start memory tracking
        tracemalloc.start()
        
        # Initialize components
        config = ConfigManager("config.example.json")
        db = DatabaseManager(":memory:")
        event_bus = EventBus()
        queue = VideoProcessingQueue()
        
        # Measure initial memory
        mem_info = self.process.memory_info()
        initial_mb = mem_info.rss / 1024 / 1024
        
        memory_samples = []
        start_time = time.time()
        
        # Sample memory every second
        while time.time() - start_time < duration:
            mem_info = self.process.memory_info()
            current_mb = mem_info.rss / 1024 / 1024
            memory_samples.append(current_mb)
            time.sleep(1)
        
        # Get tracemalloc statistics
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Calculate metrics
        avg_memory = statistics.mean(memory_samples)
        max_memory = max(memory_samples)
        min_memory = min(memory_samples)
        
        # Cleanup
        db.close()
        
        result = {
            'initial_mb': initial_mb,
            'average_mb': avg_memory,
            'min_mb': min_memory,
            'max_mb': max_memory,
            'peak_traced_mb': peak / 1024 / 1024,
            'target_idle_mb': 150.0,
            'passes': avg_memory < 150.0,
            'samples': memory_samples
        }
        
        print(f"\n  Initial: {initial_mb:.2f} MB")
        print(f"  Average: {avg_memory:.2f} MB (Target: <150 MB) {'✅' if result['passes'] else '❌'}")
        print(f"  Min: {min_memory:.2f} MB, Max: {max_memory:.2f} MB")
        print(f"  Peak Traced: {result['peak_traced_mb']:.2f} MB")
        
        self.results['metrics']['memory_usage'] = result
        return result
    
    def measure_cpu_usage(self, duration: int = 10) -> Dict[str, float]:
        """
        Measure CPU usage (idle state)
        
        Args:
            duration: How long to monitor (seconds)
            
        Returns:
            Dictionary with CPU metrics (percentage)
        """
        print(f"\n📊 Measuring CPU Usage (idle for {duration}s)...")
        
        # Initialize components
        config = ConfigManager("config.example.json")
        db = DatabaseManager(":memory:")
        event_bus = EventBus()
        queue = VideoProcessingQueue()
        
        cpu_samples = []
        start_time = time.time()
        
        # Sample CPU every 0.5 seconds
        while time.time() - start_time < duration:
            cpu_percent = self.process.cpu_percent(interval=0.5)
            cpu_samples.append(cpu_percent)
        
        # Calculate metrics
        avg_cpu = statistics.mean(cpu_samples)
        max_cpu = max(cpu_samples)
        min_cpu = min(cpu_samples)
        
        # Cleanup
        db.close()
        
        result = {
            'average_percent': avg_cpu,
            'min_percent': min_cpu,
            'max_percent': max_cpu,
            'target_idle_percent': 5.0,
            'passes': avg_cpu < 5.0,
            'samples': cpu_samples
        }
        
        print(f"\n  Average: {avg_cpu:.2f}% (Target: <5%) {'✅' if result['passes'] else '❌'}")
        print(f"  Min: {min_cpu:.2f}%, Max: {max_cpu:.2f}%")
        
        self.results['metrics']['cpu_usage_idle'] = result
        return result
    
    def measure_database_performance(self, num_operations: int = 1000) -> Dict[str, Any]:
        """
        Measure database query performance
        
        Args:
            num_operations: Number of operations to perform
            
        Returns:
            Dictionary with database performance metrics
        """
        print(f"\n📊 Measuring Database Performance ({num_operations} operations)...")
        
        db = DatabaseManager(":memory:")
        
        # Measure INSERT performance
        insert_times = []
        for i in range(num_operations):
            start = time.perf_counter()
            db.add_video({
                'video_id': f'test_video_{i}',
                'title': f'Test Video {i}',
                'description': 'Test description',
                'url': f'https://youtube.com/watch?v=test_{i}',
                'status': 'pending'
            })
            elapsed = time.perf_counter() - start
            insert_times.append(elapsed * 1000)  # Convert to ms
        
        # Measure SELECT performance
        select_times = []
        for i in range(min(100, num_operations)):  # Sample 100 reads
            video_id = f'test_video_{i}'
            start = time.perf_counter()
            db.get_video(video_id)
            elapsed = time.perf_counter() - start
            select_times.append(elapsed * 1000)
        
        # Measure UPDATE performance
        update_times = []
        for i in range(min(100, num_operations)):
            video_id = f'test_video_{i}'
            start = time.perf_counter()
            db.update_video_status(video_id, 'completed')
            elapsed = time.perf_counter() - start
            update_times.append(elapsed * 1000)
        
        # Measure bulk SELECT
        start = time.perf_counter()
        all_videos = db.get_all_videos()
        bulk_select_time = (time.perf_counter() - start) * 1000
        
        db.close()
        
        result = {
            'insert': {
                'average_ms': statistics.mean(insert_times),
                'min_ms': min(insert_times),
                'max_ms': max(insert_times),
                'operations': num_operations
            },
            'select': {
                'average_ms': statistics.mean(select_times),
                'min_ms': min(select_times),
                'max_ms': max(select_times),
                'operations': len(select_times)
            },
            'update': {
                'average_ms': statistics.mean(update_times),
                'min_ms': min(update_times),
                'max_ms': max(update_times),
                'operations': len(update_times)
            },
            'bulk_select': {
                'time_ms': bulk_select_time,
                'records': len(all_videos)
            }
        }
        
        print(f"\n  INSERT: {result['insert']['average_ms']:.3f}ms avg (n={num_operations})")
        print(f"  SELECT: {result['select']['average_ms']:.3f}ms avg (n={len(select_times)})")
        print(f"  UPDATE: {result['update']['average_ms']:.3f}ms avg (n={len(update_times)})")
        print(f"  BULK SELECT: {bulk_select_time:.2f}ms ({len(all_videos)} records)")
        
        self.results['metrics']['database_performance'] = result
        return result
    
    def measure_event_bus_performance(self, num_events: int = 10000) -> Dict[str, Any]:
        """
        Measure event bus performance
        
        Args:
            num_events: Number of events to publish
            
        Returns:
            Dictionary with event bus metrics
        """
        print(f"\n📊 Measuring Event Bus Performance ({num_events} events)...")
        
        from src.core.events import EventType
        
        event_bus = EventBus()
        
        # Add subscribers
        def dummy_handler(event):
            pass
        
        for event_type in [EventType.VIDEO_DETECTED, EventType.DOWNLOAD_STARTED, EventType.UPLOAD_COMPLETED]:
            for _ in range(5):  # 5 subscribers per event
                event_bus.subscribe(event_type, dummy_handler)
        
        # Measure publish performance
        publish_times = []
        for i in range(num_events):
            start = time.perf_counter()
            event_bus.publish(EventType.VIDEO_DETECTED, {'video_id': f'test_{i}'})
            elapsed = time.perf_counter() - start
            publish_times.append(elapsed * 1000000)  # Convert to microseconds
        
        result = {
            'average_us': statistics.mean(publish_times),
            'min_us': min(publish_times),
            'max_us': max(publish_times),
            'operations': num_events,
            'subscribers_per_event': 5
        }
        
        print(f"\n  Average: {result['average_us']:.2f}μs per event")
        print(f"  Min: {result['min_us']:.2f}μs, Max: {result['max_us']:.2f}μs")
        print(f"  Total: {num_events} events with 5 subscribers each")
        
        self.results['metrics']['event_bus_performance'] = result
        return result
    
    def measure_queue_performance(self, num_tasks: int = 1000) -> Dict[str, Any]:
        """
        Measure queue manager performance
        
        Args:
            num_tasks: Number of tasks to process
            
        Returns:
            Dictionary with queue metrics
        """
        print(f"\n📊 Measuring Queue Performance ({num_tasks} tasks)...")
        
        from src.core.queue_manager import VideoPriority
        
        queue = VideoProcessingQueue(max_concurrent=3)
        
        # Measure add_task performance
        add_times = []
        for i in range(num_tasks):
            video_info = {
                'video_id': f'test_video_{i}',
                'title': f'Test Video {i}',
                'url': f'https://youtube.com/watch?v=test_{i}'
            }
            start = time.perf_counter()
            queue.add_task(video_info, VideoPriority.NORMAL)
            elapsed = time.perf_counter() - start
            add_times.append(elapsed * 1000000)  # microseconds
        
        # Measure get_next_task performance
        get_times = []
        completed_times = []
        
        for i in range(min(100, num_tasks)):
            # Get task
            start = time.perf_counter()
            task = queue.get_next_task()
            elapsed = time.perf_counter() - start
            get_times.append(elapsed * 1000000)
            
            # Mark completed
            if task:
                start = time.perf_counter()
                queue.mark_completed(task.video_id)
                elapsed = time.perf_counter() - start
                completed_times.append(elapsed * 1000000)
        
        result = {
            'add_task': {
                'average_us': statistics.mean(add_times),
                'min_us': min(add_times),
                'max_us': max(add_times),
                'operations': num_tasks
            },
            'get_task': {
                'average_us': statistics.mean(get_times),
                'min_us': min(get_times),
                'max_us': max(get_times),
                'operations': len(get_times)
            },
            'mark_completed': {
                'average_us': statistics.mean(completed_times),
                'min_us': min(completed_times),
                'max_us': max(completed_times),
                'operations': len(completed_times)
            }
        }
        
        print(f"\n  Add Task: {result['add_task']['average_us']:.2f}μs avg")
        print(f"  Get Task: {result['get_task']['average_us']:.2f}μs avg")
        print(f"  Mark Completed: {result['mark_completed']['average_us']:.2f}μs avg")
        
        self.results['metrics']['queue_performance'] = result
        return result
    
    def generate_report(self) -> str:
        """
        Generate performance report
        
        Returns:
            Path to generated report
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.output_dir / f"performance_report_{timestamp}.json"
        
        # Add summary
        self.results['summary'] = {
            'startup_time_passes': self.results['metrics'].get('startup_time', {}).get('passes', False),
            'memory_usage_passes': self.results['metrics'].get('memory_usage', {}).get('passes', False),
            'cpu_usage_passes': self.results['metrics'].get('cpu_usage_idle', {}).get('passes', False),
            'all_targets_met': all([
                self.results['metrics'].get('startup_time', {}).get('passes', False),
                self.results['metrics'].get('memory_usage', {}).get('passes', False),
                self.results['metrics'].get('cpu_usage_idle', {}).get('passes', False)
            ])
        }
        
        # Save JSON report
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate markdown report
        md_report = self._generate_markdown_report()
        md_path = self.output_dir / f"performance_report_{timestamp}.md"
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_report)
        
        print(f"\n📄 Report saved to: {report_path}")
        print(f"📄 Markdown report: {md_path}")
        
        return str(report_path)
    
    def _generate_markdown_report(self) -> str:
        """Generate markdown formatted report"""
        metrics = self.results['metrics']
        summary = self.results['summary']
        
        report = f"""# Performance Profile Report
Generated: {self.results['timestamp']}

## Summary

{'✅ All performance targets met!' if summary['all_targets_met'] else '⚠️ Some targets not met'}

- Startup Time: {'✅ PASS' if summary['startup_time_passes'] else '❌ FAIL'}
- Memory Usage: {'✅ PASS' if summary['memory_usage_passes'] else '❌ FAIL'}
- CPU Usage: {'✅ PASS' if summary['cpu_usage_passes'] else '❌ FAIL'}

## Startup Time

Target: <3.0s
- Average: {metrics.get('startup_time', {}).get('average', 0):.3f}s
- Min: {metrics.get('startup_time', {}).get('min', 0):.3f}s
- Max: {metrics.get('startup_time', {}).get('max', 0):.3f}s

## Memory Usage (Idle)

Target: <150 MB
- Initial: {metrics.get('memory_usage', {}).get('initial_mb', 0):.2f} MB
- Average: {metrics.get('memory_usage', {}).get('average_mb', 0):.2f} MB
- Peak: {metrics.get('memory_usage', {}).get('max_mb', 0):.2f} MB

## CPU Usage (Idle)

Target: <5%
- Average: {metrics.get('cpu_usage_idle', {}).get('average_percent', 0):.2f}%
- Min: {metrics.get('cpu_usage_idle', {}).get('min_percent', 0):.2f}%
- Max: {metrics.get('cpu_usage_idle', {}).get('max_percent', 0):.2f}%

## Database Performance

### INSERT Operations
- Average: {metrics.get('database_performance', {}).get('insert', {}).get('average_ms', 0):.3f}ms
- Operations: {metrics.get('database_performance', {}).get('insert', {}).get('operations', 0)}

### SELECT Operations
- Average: {metrics.get('database_performance', {}).get('select', {}).get('average_ms', 0):.3f}ms
- Operations: {metrics.get('database_performance', {}).get('select', {}).get('operations', 0)}

### UPDATE Operations
- Average: {metrics.get('database_performance', {}).get('update', {}).get('average_ms', 0):.3f}ms
- Operations: {metrics.get('database_performance', {}).get('update', {}).get('operations', 0)}

## Event Bus Performance

- Average: {metrics.get('event_bus_performance', {}).get('average_us', 0):.2f}μs per event
- Events: {metrics.get('event_bus_performance', {}).get('operations', 0)}
- Subscribers per event: {metrics.get('event_bus_performance', {}).get('subscribers_per_event', 0)}

## Queue Performance

- Add Task: {metrics.get('queue_performance', {}).get('add_task', {}).get('average_us', 0):.2f}μs
- Get Task: {metrics.get('queue_performance', {}).get('get_task', {}).get('average_us', 0):.2f}μs
- Mark Completed: {metrics.get('queue_performance', {}).get('mark_completed', {}).get('average_us', 0):.2f}μs

---
*Performance profiling completed successfully*
"""
        return report
    
    def run_full_profile(self):
        """Run all performance measurements"""
        print("=" * 60)
        print("🚀 PERFORMANCE PROFILER")
        print("=" * 60)
        
        self.measure_startup_time(iterations=5)
        self.measure_memory_usage(duration=10)
        self.measure_cpu_usage(duration=10)
        self.measure_database_performance(num_operations=1000)
        self.measure_event_bus_performance(num_events=10000)
        self.measure_queue_performance(num_tasks=1000)
        
        report_path = self.generate_report()
        
        print("\n" + "=" * 60)
        print("✅ Performance profiling complete!")
        print("=" * 60)
        
        return self.results


def main():
    """Main entry point"""
    profiler = PerformanceProfiler()
    results = profiler.run_full_profile()
    
    # Print final summary
    summary = results['summary']
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"All Targets Met: {'✅ YES' if summary['all_targets_met'] else '❌ NO'}")
    print(f"  - Startup Time: {'✅' if summary['startup_time_passes'] else '❌'}")
    print(f"  - Memory Usage: {'✅' if summary['memory_usage_passes'] else '❌'}")
    print(f"  - CPU Usage: {'✅' if summary['cpu_usage_passes'] else '❌'}")
    print("=" * 60)


if __name__ == '__main__':
    main()
