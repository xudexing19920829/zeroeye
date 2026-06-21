#!/usr/bin/env python3
"""
Terraform Import Resource Name Validator.

This script validates Terraform resource names to ensure they follow
naming conventions and best practices.
"""

import os
import sys
import re
import json
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ValidationResult:
    """Validation result for a resource name."""
    resource_name: str
    resource_type: str
    is_valid: bool
    issues: List[str]
    suggestions: List[str]


class TerraformNameValidator:
    """Validate Terraform resource names."""
    
    def __init__(self):
        self.patterns = {
            "aws_instance": r"^i-[0-9a-f]{17}$",
            "aws_s3_bucket": r"^[a-z0-9][a-z0-9.-]{1,61}[a-z0-9]$",
            "aws_security_group": r"^sg-[0-9a-f]{17}$",
            "aws_vpc": r"^vpc-[0-9a-f]{17}$",
            "aws_subnet": r"^subnet-[0-9a-f]{17}$",
        }
        
        self.naming_conventions = {
            "lowercase": r"^[a-z][a-z0-9-]*[a-z0-9]$",
            "no_underscores": r"^[^-]*$",
            "max_length": 64,
        }
    
    def validate_resource_name(self, resource_type: str, resource_name: str) -> ValidationResult:
        """Validate a Terraform resource name."""
        issues = []
        suggestions = []
        
        # Check if resource type is known
        if resource_type not in self.patterns:
            issues.append(f"Unknown resource type: {resource_type}")
            suggestions.append(f"Add pattern for {resource_type}")
        
        # Check naming conventions
        if not re.match(self.naming_conventions["lowercase"], resource_name):
            issues.append("Resource name should be lowercase")
            suggestions.append(f"Convert to lowercase: {resource_name.lower()}")
        
        if "_" in resource_name:
            issues.append("Resource name contains underscores")
            suggestions.append(f"Replace underscores with hyphens: {resource_name.replace('_', '-')}")
        
        if len(resource_name) > self.naming_conventions["max_length"]:
            issues.append(f"Resource name too long ({len(resource_name)} > {self.naming_conventions['max_length']})")
            suggestions.append("Shorten resource name")
        
        # Check resource-specific pattern
        if resource_type in self.patterns:
            pattern = self.patterns[resource_type]
            if not re.match(pattern, resource_name):
                issues.append(f"Resource name doesn't match pattern for {resource_type}")
                suggestions.append(f"Expected pattern: {pattern}")
        
        is_valid = len(issues) == 0
        
        return ValidationResult(
            resource_name=resource_name,
            resource_type=resource_type,
            is_valid=is_valid,
            issues=issues,
            suggestions=suggestions
        )
    
    def validate_import_block(self, import_block: Dict) -> ValidationResult:
        """Validate a Terraform import block."""
        resource_type = import_block.get("type", "")
        resource_name = import_block.get("name", "")
        
        return self.validate_resource_name(resource_type, resource_name)
    
    def validate_import_file(self, file_path: str) -> List[ValidationResult]:
        """Validate all import blocks in a file."""
        results = []
        
        try:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Parse import blocks (simplified)
            import_pattern = r'import\s*\{[^}]*\}'
            imports = re.findall(import_pattern, content, re.DOTALL)
            
            for import_block in imports:
                # Extract type and name (simplified)
                type_match = re.search(r'type\s*=\s*"([^"]+)"', import_block)
                name_match = re.search(r'name\s*=\s*"([^"]+)"', import_block)
                
                if type_match and name_match:
                    resource_type = type_match.group(1)
                    resource_name = name_match.group(1)
                    
                    result = self.validate_resource_name(resource_type, resource_name)
                    results.append(result)
        
        except Exception as e:
            print(f"Error reading file: {e}")
        
        return results
    
    def generate_report(self, results: List[ValidationResult]) -> str:
        """Generate validation report."""
        lines = [
            "Terraform Import Validation Report",
            "=" * 40,
            f"Total resources: {len(results)}",
            f"Valid: {sum(1 for r in results if r.is_valid)}",
            f"Invalid: {sum(1 for r in results if not r.is_valid)}",
            "",
            "Details:",
            "-" * 40
        ]
        
        for result in results:
            status = "✅" if result.is_valid else "❌"
            lines.append(f"{status} {result.resource_type}.{result.resource_name}")
            
            if result.issues:
                for issue in result.issues:
                    lines.append(f"   ⚠️  {issue}")
            
            if result.suggestions:
                for suggestion in result.suggestions:
                    lines.append(f"   💡 {suggestion}")
        
        return "\n".join(lines)


def main():
    """Main function."""
    validator = TerraformNameValidator()
    
    # Example validation
    test_cases = [
        {"type": "aws_instance", "name": "i-1234567890abcdef0"},
        {"type": "aws_s3_bucket", "name": "my-bucket-123"},
        {"type": "aws_security_group", "name": "sg-1234567890abcdef0"},
        {"type": "aws_instance", "name": "INVALID_NAME"},
        {"type": "aws_s3_bucket", "name": "My_Bucket"},
    ]
    
    results = []
    for test_case in test_cases:
        result = validator.validate_import_block(test_case)
        results.append(result)
    
    # Generate report
    report = validator.generate_report(results)
    print(report)
    
    # Save results
    output_file = "terraform_validation_report.json"
    with open(output_file, "w") as f:
        json.dump([asdict(r) for r in results], f, indent=2)
    
    print(f"\nDetailed report saved to: {output_file}")
    
    # Exit with status
    invalid_count = sum(1 for r in results if not r.is_valid)
    if invalid_count > 0:
        print(f"\n⚠️  Found {invalid_count} invalid resource names!")
        sys.exit(1)
    else:
        print(f"\n✅ All {len(results)} resource names are valid!")
        sys.exit(0)


if __name__ == "__main__":
    main()
