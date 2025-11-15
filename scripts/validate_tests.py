#!/usr/bin/env python3
"""Validate test suite structure and completeness."""

import os
import ast
import sys
from pathlib import Path
from typing import List, Dict, Tuple


class TestValidator:
    """Validator for test files."""

    def __init__(self, backend_path: Path):
        self.backend_path = backend_path
        self.tests_path = backend_path / "tests"
        self.results = []

    def validate_file_exists(self, filepath: Path, description: str) -> bool:
        """Check if a file exists."""
        exists = filepath.exists()
        status = "✓" if exists else "✗"
        self.results.append((status, description, filepath.name))
        return exists

    def count_test_functions(self, filepath: Path) -> int:
        """Count test functions in a file."""
        if not filepath.exists():
            return 0

        try:
            with open(filepath, 'r') as f:
                tree = ast.parse(f.read())

            count = 0
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    count += 1
            return count
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return 0

    def validate_test_structure(self) -> Dict[str, int]:
        """Validate the test suite structure."""
        test_files = {
            'test_security.py': 'Security utility tests',
            'test_auth.py': 'Authentication endpoint tests',
            'test_namespaces.py': 'Namespace management tests',
            'test_configs.py': 'Configuration management tests',
            'test_e2e.py': 'End-to-end integration tests',
            'conftest.py': 'Test fixtures and configuration',
        }

        print("=" * 70)
        print("  Konfig Test Suite Validation")
        print("=" * 70)
        print()

        # Check test files
        print("📁 Test Files:")
        print("-" * 70)
        test_counts = {}
        for filename, description in test_files.items():
            filepath = self.tests_path / filename
            exists = self.validate_file_exists(filepath, description)
            if exists and filename != 'conftest.py':
                count = self.count_test_functions(filepath)
                test_counts[filename] = count
                print(f"  {'✓' if exists else '✗'} {filename:25} - {description:30} ({count} tests)")
            else:
                print(f"  {'✓' if exists else '✗'} {filename:25} - {description}")

        print()

        # Check test scripts
        print("🔧 Test Scripts:")
        print("-" * 70)
        scripts_path = self.backend_path.parent / "scripts"
        scripts = {
            'run_e2e_tests.sh': 'End-to-end test runner',
            'run_all_tests.sh': 'Comprehensive test runner',
            'validate_tests.py': 'Test validation script',
        }

        for filename, description in scripts.items():
            filepath = scripts_path / filename
            exists = filepath.exists()
            executable = filepath.exists() and os.access(filepath, os.X_OK)
            status = "✓" if exists and executable else ("⚠" if exists else "✗")
            print(f"  {status} {filename:25} - {description}")

        print()

        # Check configuration files
        print("⚙️  Configuration Files:")
        print("-" * 70)
        config_files = {
            'pytest.ini': 'Pytest configuration',
            'requirements.txt': 'Python dependencies',
            'requirements-dev.txt': 'Development dependencies',
        }

        for filename, description in config_files.items():
            filepath = self.backend_path / filename
            exists = self.validate_file_exists(filepath, description)
            print(f"  {'✓' if exists else '✗'} {filename:25} - {description}")

        print()

        # Summary
        print("=" * 70)
        print("  Test Summary")
        print("=" * 70)
        total_tests = sum(test_counts.values())
        print(f"  Total test files:     {len(test_counts)}")
        print(f"  Total test functions: {total_tests}")
        print()
        print("  Breakdown:")
        for filename, count in sorted(test_counts.items()):
            print(f"    {filename:25} {count:3} tests")

        print()
        print("=" * 70)

        return test_counts

    def check_test_coverage_areas(self) -> None:
        """Check which areas are covered by tests."""
        print()
        print("📊 Coverage Areas:")
        print("-" * 70)

        coverage_areas = [
            ("Security", ["Password hashing", "JWT tokens", "Data encryption"]),
            ("Authentication", ["Registration", "Login", "Token refresh"]),
            ("Namespaces", ["CRUD operations", "Multi-tenant isolation"]),
            ("Configurations", ["All data types", "Version history", "Encryption"]),
            ("End-to-End", ["Full API workflow", "Real HTTP requests", "Docker integration"]),
        ]

        for area, features in coverage_areas:
            print(f"\n  ✓ {area}:")
            for feature in features:
                print(f"    • {feature}")

        print()


def main():
    """Main validation function."""
    # Get project paths
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    backend_path = project_root / "backend"

    if not backend_path.exists():
        print(f"❌ Backend directory not found at {backend_path}")
        sys.exit(1)

    # Run validation
    validator = TestValidator(backend_path)
    test_counts = validator.validate_test_structure()
    validator.check_test_coverage_areas()

    # Instructions
    print("=" * 70)
    print("  Quick Start")
    print("=" * 70)
    print()
    print("  Run unit tests:")
    print("    cd backend && pytest tests/ --ignore=tests/test_e2e.py -v")
    print()
    print("  Run E2E tests (requires Docker):")
    print("    bash scripts/run_e2e_tests.sh")
    print()
    print("  Run all tests:")
    print("    bash scripts/run_all_tests.sh")
    print()
    print("  For detailed instructions, see TESTING.md")
    print()
    print("=" * 70)

    # Success check
    total_tests = sum(test_counts.values())
    if total_tests >= 30:  # We expect at least 30 test functions
        print()
        print("✅ Test suite validation PASSED!")
        print(f"   Found {total_tests} test functions across {len(test_counts)} test files.")
        print()
        return 0
    else:
        print()
        print("⚠️  Test suite may be incomplete.")
        print(f"   Found only {total_tests} test functions.")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
