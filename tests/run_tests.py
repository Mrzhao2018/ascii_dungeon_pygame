#!/usr/bin/env python3
"""
Test runner for the game unit tests
"""
import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def discover_and_run_tests():
    """Discover and run all unit tests"""
    print("Running Game Unit Tests")
    print("=" * 50)
    
    # Discover tests in the tests directory
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    # Load all test modules
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.splitlines()[-1]}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.splitlines()[-1]}")
    
    # Return success/failure
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall result: {'PASS' if success else 'FAIL'}")
    
    return success


def run_specific_test(test_module):
    """Run a specific test module"""
    print(f"Running tests from {test_module}")
    print("=" * 50)
    
    try:
        # Import the test module
        module = __import__(f'tests.{test_module}', fromlist=[''])
        
        # Load tests from module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(module)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0
    
    except ImportError as e:
        print(f"Error importing test module {test_module}: {e}")
        return False


def run_coverage_report():
    """Run tests with coverage reporting if available"""
    try:
        import coverage
        
        # Start coverage
        cov = coverage.Coverage()
        cov.start()
        
        # Run tests
        success = discover_and_run_tests()
        
        # Stop coverage and generate report
        cov.stop()
        cov.save()
        
        print("\n" + "=" * 50)
        print("Coverage Report:")
        print("=" * 50)
        cov.report(show_missing=True)
        
        return success
        
    except ImportError:
        print("Coverage module not available. Install with: pip install coverage")
        return discover_and_run_tests()


def main():
    """Main test runner"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == '--coverage':
            success = run_coverage_report()
        elif command == '--help':
            print("Game Test Runner")
            print("Usage:")
            print("  python run_tests.py              # Run all tests")
            print("  python run_tests.py --coverage   # Run with coverage")
            print("  python run_tests.py test_config  # Run specific test")
            print("  python run_tests.py --help       # Show this help")
            return True
        else:
            # Run specific test module
            test_name = command.replace('test_', '').replace('.py', '')
            success = run_specific_test(f'test_{test_name}')
    else:
        success = discover_and_run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()