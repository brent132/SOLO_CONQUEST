#!/usr/bin/env python3
"""
Script to remove all print statements from Python files in the codebase
"""
import os
import re
import sys

def remove_print_statements(file_path):
    """Remove print statements from a Python file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Pattern to match print statements
        # This pattern matches print(...) including multiline prints
        print_pattern = r'print\([^)]*(?:\([^)]*\)[^)]*)*\)'
        
        # Find all print statements
        matches = list(re.finditer(print_pattern, content, re.MULTILINE | re.DOTALL))
        
        if not matches:
            return False, "No print statements found"
        
        # Replace from end to beginning to preserve line numbers
        modified_content = content
        for match in reversed(matches):
            start, end = match.span()
            # Find the line containing the print statement
            lines_before = content[:start].count('\n')
            line_start = content.rfind('\n', 0, start) + 1
            line_end = content.find('\n', end)
            if line_end == -1:
                line_end = len(content)
            
            # Get the indentation of the line
            line_content = content[line_start:line_end]
            indent_match = re.match(r'^(\s*)', line_content)
            indent = indent_match.group(1) if indent_match else ''
            
            # Replace with pass statement
            replacement = f"{indent}pass  # Print statement removed"
            modified_content = modified_content[:line_start] + replacement + modified_content[line_end:]
        
        # Write back the modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        return True, f"Removed {len(matches)} print statements"
    
    except Exception as e:
        return False, f"Error processing {file_path}: {e}"

def main():
    """Main function to process all Python files"""
    # Get all Python files with print statements
    python_files = []
    
    for root, dirs, files in os.walk('.'):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                python_files.append(file_path)
    
    print(f"Found {len(python_files)} Python files")
    
    processed = 0
    modified = 0
    
    for file_path in python_files:
        success, message = remove_print_statements(file_path)
        if success:
            modified += 1
            print(f"✓ {file_path}: {message}")
        else:
            if "No print statements found" not in message:
                print(f"✗ {file_path}: {message}")
        processed += 1
    
    print(f"\nProcessed {processed} files, modified {modified} files")

if __name__ == "__main__":
    main()
