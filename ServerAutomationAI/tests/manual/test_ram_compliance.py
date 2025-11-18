"""
Manual RAM Compliance Testing for QA/Test Agent

This script tests RAM usage during QA analysis to ensure compliance
with the 3.5 GB limit.

Run with: python tests/manual/test_ram_compliance.py
"""

import asyncio
import tempfile
import shutil
from pathlib import Path
import psutil
import time
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dev_platform.agents.qa_test_agent import QATestAgent
from dev_platform.tools.async_qa_manager import AsyncQATaskManager
from dev_platform.agents.schemas import QAToolType


def get_current_ram_mb():
    """Get current RAM usage in MB"""
    process = psutil.Process()
    return process.memory_info().rss / (1024 * 1024)


def create_large_test_directory(base_dir: Path, num_files: int = 50) -> Path:
    """Create a directory with many Python files for testing"""
    test_dir = base_dir / "large_test_project"
    test_dir.mkdir(exist_ok=True)
    
    # Sample Python file with various issues
    sample_code = """
import pickle
import subprocess
import os

class DataProcessor:
    def __init__(self, config):
        self.config = config
        self.data = []
    
    def process_data(self, input_data, verbose=False, debug=False, sanitize=True, validate=True):
        # Very long function with high complexity
        if validate:
            if sanitize:
                if debug:
                    if verbose:
                        if input_data is not None:
                            if len(input_data) > 0:
                                if isinstance(input_data, list):
                                    for item in input_data:
                                        if item:
                                            self.data.append(item)
                                        else:
                                            continue
                                else:
                                    self.data.append(input_data)
                            else:
                                return None
                        else:
                            return None
                    else:
                        self.data.extend(input_data)
                else:
                    self.data = input_data
            else:
                return None
        else:
            return None
        
        return self.data
    
    def load_from_pickle(self, filepath):
        # Security issue: unsafe deserialization
        with open(filepath, 'rb') as f:
            return pickle.load(f)
    
    def execute_command(self, cmd):
        # Security issue: shell injection vulnerability
        return subprocess.call(cmd, shell=True)
    
    def get_files(self, directory):
        # Missing error handling
        return os.listdir(directory)

def unused_function_one():
    pass

def unused_function_two():
    pass

def unused_function_three():
    pass
"""
    
    # Create many files
    for i in range(num_files):
        file_path = test_dir / f"module_{i}.py"
        file_path.write_text(sample_code)
    
    return test_dir


async def test_ram_single_file():
    """Test RAM usage for single file analysis"""
    print("\n" + "="*60)
    print("TEST 1: Single File Analysis")
    print("="*60)
    
    # Create temporary file
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text("""
def complex_function(a, b, c, d, e):
    if a > b:
        if c > d:
            if e > 0:
                return a + b
    return 0
""")
    
    try:
        # Baseline RAM
        baseline_ram = get_current_ram_mb()
        print(f"📊 Baseline RAM: {baseline_ram:.2f} MB")
        
        # Run QA analysis
        manager = AsyncQATaskManager()
        start_time = time.time()
        
        report = await manager.analyze_code_quality_async(
            file_path=str(test_file),
            tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON],
            options={}
        )
        
        duration = time.time() - start_time
        
        # Check RAM metrics
        peak_ram = manager.peak_memory_mb
        current_ram = get_current_ram_mb()
        
        print(f"✓ Analysis completed in {duration:.2f}s")
        print(f"📊 Peak RAM: {peak_ram:.2f} MB")
        print(f"📊 Current RAM: {current_ram:.2f} MB")
        print(f"📊 RAM Increase: {(peak_ram - baseline_ram):.2f} MB")
        
        # Check compliance
        ram_limit_mb = 3584  # 3.5 GB
        if peak_ram < ram_limit_mb:
            print(f"✅ PASS: RAM usage {peak_ram:.2f} MB < {ram_limit_mb} MB limit")
        else:
            print(f"❌ FAIL: RAM usage {peak_ram:.2f} MB >= {ram_limit_mb} MB limit")
        
        return peak_ram < ram_limit_mb
        
    finally:
        shutil.rmtree(temp_dir)


async def test_ram_large_directory():
    """Test RAM usage for large directory analysis"""
    print("\n" + "="*60)
    print("TEST 2: Large Directory Analysis (50 files)")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Create large test directory
        print("📁 Creating 50 Python files...")
        test_dir = create_large_test_directory(Path(temp_dir), num_files=50)
        
        # Baseline RAM
        baseline_ram = get_current_ram_mb()
        print(f"📊 Baseline RAM: {baseline_ram:.2f} MB")
        
        # Run QA analysis on entire directory
        manager = AsyncQATaskManager()
        start_time = time.time()
        
        # Analyze directory (will analyze all files sequentially)
        report = await manager.analyze_code_quality_async(
            file_path=str(test_dir),
            tools=[QAToolType.FLAKE8, QAToolType.BANDIT, QAToolType.RADON],
            options={}
        )
        
        duration = time.time() - start_time
        
        # Check RAM metrics
        peak_ram = manager.peak_memory_mb
        current_ram = get_current_ram_mb()
        
        print(f"✓ Analysis completed in {duration:.2f}s")
        print(f"📊 Peak RAM: {peak_ram:.2f} MB")
        print(f"📊 Current RAM: {current_ram:.2f} MB")
        print(f"📊 RAM Increase: {(peak_ram - baseline_ram):.2f} MB")
        
        # Check compliance
        ram_limit_mb = 3584  # 3.5 GB
        if peak_ram < ram_limit_mb:
            print(f"✅ PASS: RAM usage {peak_ram:.2f} MB < {ram_limit_mb} MB limit")
        else:
            print(f"❌ FAIL: RAM usage {peak_ram:.2f} MB >= {ram_limit_mb} MB limit")
        
        return peak_ram < ram_limit_mb
        
    finally:
        shutil.rmtree(temp_dir)


async def test_ram_sequential_analyses():
    """Test RAM usage for multiple sequential analyses"""
    print("\n" + "="*60)
    print("TEST 3: Sequential Analyses (10 iterations)")
    print("="*60)
    
    temp_dir = tempfile.mkdtemp()
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text("""
def sample_function(x, y):
    if x > y:
        return x
    return y
""")
    
    try:
        # Baseline RAM
        baseline_ram = get_current_ram_mb()
        print(f"📊 Baseline RAM: {baseline_ram:.2f} MB")
        
        peak_rams = []
        
        # Run 10 sequential analyses
        for i in range(10):
            manager = AsyncQATaskManager()
            
            report = await manager.analyze_code_quality_async(
                file_path=str(test_file),
                tools=[QAToolType.FLAKE8, QAToolType.RADON],
                options={}
            )
            
            peak_rams.append(manager.peak_memory_mb)
        
        # Check metrics
        max_peak = max(peak_rams)
        avg_peak = sum(peak_rams) / len(peak_rams)
        current_ram = get_current_ram_mb()
        
        print(f"✓ Completed 10 sequential analyses")
        print(f"📊 Max Peak RAM: {max_peak:.2f} MB")
        print(f"📊 Avg Peak RAM: {avg_peak:.2f} MB")
        print(f"📊 Current RAM: {current_ram:.2f} MB")
        print(f"📊 RAM Increase: {(max_peak - baseline_ram):.2f} MB")
        
        # Check compliance
        ram_limit_mb = 3584  # 3.5 GB
        if max_peak < ram_limit_mb:
            print(f"✅ PASS: Max RAM usage {max_peak:.2f} MB < {ram_limit_mb} MB limit")
        else:
            print(f"❌ FAIL: Max RAM usage {max_peak:.2f} MB >= {ram_limit_mb} MB limit")
        
        # Check for memory leaks (current RAM should be close to baseline)
        ram_delta = current_ram - baseline_ram
        if ram_delta < 100:  # Allow 100 MB variance
            print(f"✅ PASS: No significant memory leak detected ({ram_delta:.2f} MB increase)")
        else:
            print(f"⚠️  WARNING: Possible memory leak ({ram_delta:.2f} MB increase)")
        
        return max_peak < ram_limit_mb
        
    finally:
        shutil.rmtree(temp_dir)


async def main():
    """Run all RAM compliance tests"""
    print("\n" + "="*60)
    print("RAM COMPLIANCE TESTING FOR QA/TEST AGENT")
    print("Target: < 3.5 GB (3584 MB)")
    print("="*60)
    
    # Get system info
    print(f"\n💻 System Info:")
    print(f"   Total RAM: {psutil.virtual_memory().total / (1024**3):.2f} GB")
    print(f"   Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB")
    
    results = []
    
    # Run tests
    results.append(("Single File", await test_ram_single_file()))
    results.append(("Large Directory", await test_ram_large_directory()))
    results.append(("Sequential Analyses", await test_ram_sequential_analyses()))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED - RAM compliance verified!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - RAM compliance NOT verified")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
