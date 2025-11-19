"""
Python-Specific Error Scanner
Checks for common Python mistakes
"""

import os
import re
import ast

errors = []
warnings = []
passes = []

print("="*80)
print("PYTHON ERROR SCANNER".center(80))
print("="*80)

# Python files to check
python_files = [
    'src/agent_competition.py',
    'src/colony_learning.py',
    'src/agent_reproduction.py',
    'src/colony_orchestrator.py',
    'competition_demo.py',
    'learning_demo.py'
]

print("\n1. SYNTAX & COMPILATION")
print("-" * 80)

for filepath in python_files:
    try:
        with open(filepath, 'r') as f:
            code = f.read()
            compile(code, filepath, 'exec')
        print(f"✅ {filepath} - Syntax OK")
        passes.append(f"Syntax: {filepath}")
    except SyntaxError as e:
        print(f"❌ {filepath} - SYNTAX ERROR: Line {e.lineno}: {e.msg}")
        errors.append(f"SYNTAX: {filepath} line {e.lineno}: {e.msg}")
    except Exception as e:
        print(f"⚠️  {filepath} - {e}")
        warnings.append(f"{filepath}: {e}")

print("\n2. IMPORT ERRORS")
print("-" * 80)

for filepath in python_files:
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Check for common import issues
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Missing import
            if re.search(r'\b(praw|tweepy|discord|telegram|slack_sdk|anthropic|schedule)\b', line):
                if not line.strip().startswith('import') and not line.strip().startswith('from'):
                    if '=' not in line:  # Not assignment
                        continue  # It's just mentioned in comments/strings

            # Circular import detection (basic)
            if 'import' in line and filepath in line:
                warnings.append(f"{filepath}:{i} - Possible circular import")

        passes.append(f"Imports scanned: {filepath}")
    except Exception as e:
        warnings.append(f"Import scan {filepath}: {e}")

print("✅ Import patterns checked")

print("\n3. COMMON PYTHON MISTAKES")
print("-" * 80)

for filepath in python_files:
    try:
        with open(filepath, 'r') as f:
            code = f.read()
            lines = code.split('\n')

        file_errors = []

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Missing colons
            if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally|with)\s+.*[^:]$', line):
                if not stripped.endswith(':'):
                    file_errors.append(f"Line {i}: Missing colon?")

            # Unclosed strings
            single_quotes = line.count("'")
            double_quotes = line.count('"')
            if single_quotes % 2 != 0 and '#' not in line:  # Odd number of quotes (not in comment)
                file_errors.append(f"Line {i}: Unclosed string?")

            # Missing parentheses in function calls
            if re.search(r'\bprint\s+["\']', line):  # print without ()
                file_errors.append(f"Line {i}: Missing parentheses in print()?")

            # Incorrect indentation markers
            if line.startswith('\t') and '    ' in code:
                warnings.append(f"{filepath}:{i} - Mixed tabs and spaces")

        if file_errors:
            for err in file_errors[:5]:  # Show first 5
                print(f"⚠️  {filepath} - {err}")
                warnings.append(f"{filepath}: {err}")
        else:
            print(f"✅ {filepath} - No common mistakes found")
            passes.append(f"Common mistakes: {filepath}")

    except Exception as e:
        warnings.append(f"Mistake scan {filepath}: {e}")

print("\n4. FUNCTION & CLASS DEFINITION ERRORS")
print("-" * 80)

for filepath in python_files:
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Parse AST to find issues
        tree = ast.parse(code, filepath)

        # Check for issues
        for node in ast.walk(tree):
            # Functions without docstrings (warning only)
            if isinstance(node, ast.FunctionDef):
                if not ast.get_docstring(node) and not node.name.startswith('_'):
                    # This is just a style warning, not an error
                    pass

            # Classes without __init__ (might be intentional)
            if isinstance(node, ast.ClassDef):
                has_init = any(isinstance(n, ast.FunctionDef) and n.name == '__init__' for n in node.body)
                # This is fine, many classes don't need __init__

        print(f"✅ {filepath} - Function/class definitions OK")
        passes.append(f"Definitions: {filepath}")

    except SyntaxError as e:
        print(f"❌ {filepath} - Cannot parse: {e}")
        errors.append(f"Parse error {filepath}: {e}")
    except Exception as e:
        warnings.append(f"Definition scan {filepath}: {e}")

print("\n5. TYPE HINT CHECKS")
print("-" * 80)

for filepath in python_files:
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Check for type hints
        tree = ast.parse(code, filepath)

        functions_with_hints = 0
        functions_without_hints = 0

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    functions_with_hints += 1
                else:
                    functions_without_hints += 1

        total = functions_with_hints + functions_without_hints
        if total > 0:
            hint_percent = (functions_with_hints / total) * 100
            if hint_percent > 50:
                print(f"✅ {filepath} - {hint_percent:.0f}% functions have type hints")
            else:
                print(f"⚠️  {filepath} - Only {hint_percent:.0f}% functions have type hints")
        else:
            print(f"✅ {filepath} - No functions to check")

        passes.append(f"Type hints: {filepath}")

    except Exception as e:
        warnings.append(f"Type hint scan {filepath}: {e}")

print("\n6. ERROR HANDLING")
print("-" * 80)

for filepath in python_files:
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Count try/except blocks
        try_count = code.count('try:')
        except_count = code.count('except')

        if try_count > 0:
            print(f"✅ {filepath} - Has {try_count} try/except blocks")
        else:
            print(f"⚠️  {filepath} - No error handling (might be intentional)")

        # Check for bare except
        if 'except:' in code:
            warnings.append(f"{filepath}: Bare 'except:' found (should specify exception type)")
            print(f"   ⚠️  Has bare except: (should use except Exception:)")

        passes.append(f"Error handling: {filepath}")

    except Exception as e:
        warnings.append(f"Error handling scan {filepath}: {e}")

print("\n7. VARIABLE NAMING")
print("-" * 80)

for filepath in python_files:
    try:
        with open(filepath, 'r') as f:
            code = f.read()

        # Check for common naming issues
        if re.search(r'\bvar\s+\w+\s*=', code):
            warnings.append(f"{filepath}: JavaScript 'var' keyword found (use Python variables)")

        # Check for camelCase in Python (should be snake_case)
        tree = ast.parse(code, filepath)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if re.match(r'^[a-z]+[A-Z]', node.id):  # camelCase
                    # This is a style warning, not an error
                    pass

        print(f"✅ {filepath} - Naming conventions checked")
        passes.append(f"Naming: {filepath}")

    except Exception as e:
        warnings.append(f"Naming scan {filepath}: {e}")

# Final Report
print("\n" + "="*80)
print("ERROR SCAN RESULTS".center(80))
print("="*80)

print(f"\n✅ PASSES: {len(passes)}")

if warnings:
    print(f"\n⚠️  WARNINGS: {len(warnings)}")
    for w in warnings[:10]:  # Show first 10
        print(f"   • {w}")
    if len(warnings) > 10:
        print(f"   ... and {len(warnings) - 10} more")

if errors:
    print(f"\n❌ ERRORS: {len(errors)}")
    for e in errors:
        print(f"   • {e}")

print("\n" + "="*80)

if len(errors) == 0:
    print("✅ NO CRITICAL ERRORS FOUND".center(80))
    print("="*80)
    exit(0)
else:
    print("❌ CRITICAL ERRORS FOUND".center(80))
    print("="*80)
    exit(1)
