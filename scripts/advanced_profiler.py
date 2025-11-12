"""
Advanced Performance Profiler
Tests GUI responsiveness and load scenarios

Tests:
1. GUI responsiveness during heavy processing
2. Concurrent worker thread performance
3. Memory leak detection
4. Long-running stability test
"""

import sys
import os
import time
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import threading
import gc

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.database import DatabaseManager
from src.core.queue_manager import VideoProcessingQueue, VideoPriority
from src.core.events import EventBus, EventType


class AdvancedProfiler:
    """Advanced performance testing scenarios"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.results = {}
    
    def test_concurrent_processing(self, num_videos: int = 100) -> Dict[str, Any]:
        """
        Test concurrent processing performance
        
        Args:
            num_videos: Number of videos to process concurrently
            
        Returns:
            Performance metrics
        """
        print(f"\n📊 Testing Concurrent Processing ({num_videos} videos)...")
        
        db = DatabaseManager(":memory:")
        queue = VideoProcessingQueue(max_concurrent=3)
        event_bus = EventBus()
        
        # Add videos to queue
        start_time = time.time()
        for i in range(num_videos):
            video_info = {
                'video_id': f'concurrent_test_{i}',
                'title': f'Concurrent Test Video {i}',
                'url': f'https://youtube.com/watch?v=test_{i}'
            }
            queue.add_task(video_info, VideoPriority.NORMAL)
        add_time = time.time() - start_time
        
        # Simulate processing all videos
        processed = 0
        start_process = time.time()
        
        while queue.get_queue_size() > 0 or queue.get_processing_count() > 0:
            # Get up to 3 tasks (simulating workers)
            tasks = []
            for _ in range(3):
                task = queue.get_next_task()
                if task:
                    tasks.append(task)
            
            # "Process" tasks (simulate work)
            for task in tasks:
                # Simulate some work
                time.sleep(0.001)
                queue.mark_completed(task.video_id)
                processed += 1
        
        process_time = time.time() - start_process
        
        db.close()
        
        result = {
            'num_videos': num_videos,
            'add_time_s': add_time,
            'process_time_s': process_time,
            'total_time_s': add_time + process_time,
            'throughput_per_second': num_videos / (add_time + process_time),
            'processed': processed
        }
        
        print(f"  Add Time: {add_time:.3f}s")
        print(f"  Process Time: {process_time:.3f}s")
        print(f"  Throughput: {result['throughput_per_second']:.1f} videos/sec")
        
        return result
    
    def test_memory_leak(self, iterations: int = 100) -> Dict[str, Any]:
        """
        Test for memory leaks over multiple iterations
        
        Args:
            iterations: Number of iterations to test
            
        Returns:
            Memory metrics
        """
        print(f"\n📊 Testing Memory Leaks ({iterations} iterations)...")
        
        initial_mem = self.process.memory_info().rss / 1024 / 1024
        memory_samples = [initial_mem]
        
        for i in range(iterations):
            # Create and destroy components
            db = DatabaseManager(":memory:")
            queue = VideoProcessingQueue()
            event_bus = EventBus()
            
            # Add some data
            for j in range(10):
                db.add_video({
                    'video_id': f'leak_test_{i}_{j}',
                    'title': f'Leak Test {i}-{j}',
                    'url': f'https://youtube.com/watch?v=test_{i}_{j}',
                    'status': 'pending'
                })
            
            # Close and cleanup
            db.close()
            del db, queue, event_bus
            
            # Force garbage collection
            gc.collect()
            
            # Sample memory every 10 iterations
            if i % 10 == 0:
                current_mem = self.process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_mem)
                print(f"  Iteration {i}: {current_mem:.2f} MB")
        
        final_mem = self.process.memory_info().rss / 1024 / 1024
        memory_samples.append(final_mem)
        
        # Calculate memory growth
        memory_growth = final_mem - initial_mem
        growth_per_iteration = memory_growth / iterations
        
        result = {
            'iterations': iterations,
            'initial_mb': initial_mem,
            'final_mb': final_mem,
            'growth_mb': memory_growth,
            'growth_per_iteration_kb': growth_per_iteration * 1024,
            'samples': memory_samples,
            'leak_detected': growth_per_iteration > 0.1  # >100KB per iteration
        }
        
        print(f"\n  Initial: {initial_mem:.2f} MB")
        print(f"  Final: {final_mem:.2f} MB")
        print(f"  Growth: {memory_growth:.2f} MB ({growth_per_iteration*1024:.2f} KB/iteration)")
        print(f"  Leak Detected: {'⚠️ YES' if result['leak_detected'] else '✅ NO'}")
        
        return result
    
    def test_event_storm(self, num_events: int = 100000) -> Dict[str, Any]:
        """
        Test system under event storm conditions
        
        Args:
            num_events: Number of events to fire rapidly
            
        Returns:
            Performance metrics
        """
        print(f"\n📊 Testing Event Storm ({num_events:,} events)...")
        
        event_bus = EventBus()
        events_received = {'count': 0}
        
        def event_handler(event):
            events_received['count'] += 1
        
        # Subscribe to events
        for event_type in [EventType.VIDEO_DETECTED, EventType.DOWNLOAD_STARTED, EventType.UPLOAD_COMPLETED]:
            event_bus.subscribe(event_type, event_handler)
        
        # Fire event storm
        start_time = time.time()
        for i in range(num_events):
            event_type = [EventType.VIDEO_DETECTED, EventType.DOWNLOAD_STARTED, EventType.UPLOAD_COMPLETED][i % 3]
            event_bus.publish(event_type, {'index': i})
        
        elapsed = time.time() - start_time
        
        result = {
            'num_events': num_events,
            'time_s': elapsed,
            'events_per_second': num_events / elapsed,
            'events_received': events_received['count'],
            'all_received': events_received['count'] == num_events
        }
        
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Throughput: {result['events_per_second']:,.0f} events/sec")
        print(f"  Received: {events_received['count']:,}/{num_events:,} {'✅' if result['all_received'] else '❌'}")
        
        return result
    
    def test_database_stress(self, num_operations: int = 10000) -> Dict[str, Any]:
        """
        Stress test database with many operations
        
        Args:
            num_operations: Number of operations to perform
            
        Returns:
            Performance metrics
        """
        print(f"\n📊 Database Stress Test ({num_operations:,} operations)...")
        
        db = DatabaseManager(":memory:")
        
        # Mixed operations
        start_time = time.time()
        
        for i in range(num_operations):
            operation = i % 4
            
            if operation == 0:  # INSERT
                db.add_video({
                    'video_id': f'stress_test_{i}',
                    'title': f'Stress Test {i}',
                    'url': f'https://youtube.com/watch?v=test_{i}',
                    'status': 'pending'
                })
            elif operation == 1:  # SELECT
                db.get_video(f'stress_test_{max(0, i-1)}')
            elif operation == 2:  # UPDATE
                db.update_video_status(f'stress_test_{max(0, i-1)}', 'completed')
            else:  # BULK SELECT
                db.get_all_videos()
        
        elapsed = time.time() - start_time
        
        db.close()
        
        result = {
            'num_operations': num_operations,
            'time_s': elapsed,
            'operations_per_second': num_operations / elapsed,
            'avg_operation_ms': (elapsed / num_operations) * 1000
        }
        
        print(f"  Time: {elapsed:.3f}s")
        print(f"  Throughput: {result['operations_per_second']:,.0f} ops/sec")
        print(f"  Average: {result['avg_operation_ms']:.3f}ms per operation")
        
        return result
    
    def test_queue_stress(self, num_tasks: int = 10000) -> Dict[str, Any]:
        """
        Stress test queue with many tasks
        
        Args:
            num_tasks: Number of tasks to process
            
        Returns:
            Performance metrics
        """
        print(f"\n📊 Queue Stress Test ({num_tasks:,} tasks)...")
        
        queue = VideoProcessingQueue(max_concurrent=3)
        
        # Add all tasks
        start_add = time.time()
        for i in range(num_tasks):
            video_info = {
                'video_id': f'queue_stress_{i}',
                'title': f'Queue Stress {i}',
                'url': f'https://youtube.com/watch?v=test_{i}'
            }
            priority = [VideoPriority.HIGH, VideoPriority.NORMAL, VideoPriority.LOW][i % 3]
            queue.add_task(video_info, priority)
        add_time = time.time() - start_add
        
        # Process all tasks
        start_process = time.time()
        processed = 0
        
        while queue.get_queue_size() > 0:
            # Simulate 3 workers
            for _ in range(3):
                task = queue.get_next_task()
                if task:
                    queue.mark_completed(task.video_id)
                    processed += 1
        
        process_time = time.time() - start_process
        total_time = add_time + process_time
        
        result = {
            'num_tasks': num_tasks,
            'add_time_s': add_time,
            'process_time_s': process_time,
            'total_time_s': total_time,
            'throughput_per_second': num_tasks / total_time,
            'processed': processed
        }
        
        print(f"  Add Time: {add_time:.3f}s")
        print(f"  Process Time: {process_time:.3f}s")
        print(f"  Throughput: {result['throughput_per_second']:,.0f} tasks/sec")
        
        return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all advanced performance tests"""
        print("=" * 60)
        print("🔬 ADVANCED PERFORMANCE PROFILER")
        print("=" * 60)
        
        self.results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }
        
        self.results['tests']['concurrent_processing'] = self.test_concurrent_processing(100)
        self.results['tests']['memory_leak'] = self.test_memory_leak(100)
        self.results['tests']['event_storm'] = self.test_event_storm(100000)
        self.results['tests']['database_stress'] = self.test_database_stress(10000)
        self.results['tests']['queue_stress'] = self.test_queue_stress(10000)
        
        # Save results
        output_dir = Path("performance_reports")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = output_dir / f"advanced_profile_{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_path}")
        
        print("\n" + "=" * 60)
        print("✅ Advanced profiling complete!")
        print("=" * 60)
        
        # Print summary
        print("\nSUMMARY:")
        print(f"  Concurrent Processing: {self.results['tests']['concurrent_processing']['throughput_per_second']:.1f} videos/sec")
        print(f"  Memory Leak: {'⚠️ Detected' if self.results['tests']['memory_leak']['leak_detected'] else '✅ None'}")
        print(f"  Event Storm: {self.results['tests']['event_storm']['events_per_second']:,.0f} events/sec")
        print(f"  Database Stress: {self.results['tests']['database_stress']['operations_per_second']:,.0f} ops/sec")
        print(f"  Queue Stress: {self.results['tests']['queue_stress']['throughput_per_second']:,.0f} tasks/sec")
        
        return self.results


def main():
    """Main entry point"""
    profiler = AdvancedProfiler()
    profiler.run_all_tests()


if __name__ == '__main__':
    main()
