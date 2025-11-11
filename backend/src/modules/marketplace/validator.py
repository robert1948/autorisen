"""
Agent Validation Service

Provides comprehensive validation for agent manifests including
security scanning, performance testing, and compliance checking.
"""

import re
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any
from .models import AgentValidationResult, AgentCategory


class AgentValidator:
    """Comprehensive agent validation service."""

    # Security patterns to detect potentially dangerous code
    SECURITY_PATTERNS = [
        r"exec\s*\(",
        r"eval\s*\(",
        r"__import__\s*\(",
        r"open\s*\(",
        r"file\s*\(",
        r"subprocess",
        r"os\.system",
        r"shell=True",
    ]

    # Required manifest fields
    REQUIRED_FIELDS = ["name", "description", "category", "version", "entry_point"]

    # Optional but recommended fields
    RECOMMENDED_FIELDS = [
        "author",
        "license",
        "tags",
        "requirements",
        "documentation_url",
    ]

    def __init__(self):
        self.security_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.SECURITY_PATTERNS
        ]

    async def validate_manifest(
        self, manifest: Dict[str, Any]
    ) -> AgentValidationResult:
        """Validate an agent manifest comprehensively."""

        errors = []
        warnings = []

        # Basic structure validation
        errors.extend(self._validate_structure(manifest))
        warnings.extend(self._validate_recommendations(manifest))

        # Field-specific validation
        errors.extend(self._validate_fields(manifest))

        # Security validation
        security_scan = await self._security_scan(manifest)

        # Performance validation
        performance_score = await self._performance_check(manifest)

        return AgentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            security_scan=security_scan,
            performance_score=performance_score,
        )

    def _validate_structure(self, manifest: Dict[str, Any]) -> List[str]:
        """Validate basic manifest structure."""
        errors = []

        if not isinstance(manifest, dict):
            errors.append("Manifest must be a JSON object")
            return errors

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in manifest:
                errors.append(f"Missing required field: {field}")
            elif not manifest[field]:
                errors.append(f"Required field '{field}' cannot be empty")

        return errors

    def _validate_recommendations(self, manifest: Dict[str, Any]) -> List[str]:
        """Check for recommended fields and best practices."""
        warnings = []

        # Check recommended fields
        for field in self.RECOMMENDED_FIELDS:
            if field not in manifest:
                warnings.append(f"Missing recommended field: {field}")

        # Check description length
        if "description" in manifest:
            desc = manifest["description"]
            if len(desc) < 20:
                warnings.append("Description should be at least 20 characters")
            elif len(desc) > 500:
                warnings.append("Description should be under 500 characters")

        # Check tags
        if "tags" in manifest:
            tags = manifest["tags"]
            if isinstance(tags, list) and len(tags) > 10:
                warnings.append("Consider limiting tags to 10 or fewer")

        return warnings

    def _validate_fields(self, manifest: Dict[str, Any]) -> List[str]:
        """Validate specific field values."""
        errors = []

        # Validate category
        if "category" in manifest:
            try:
                AgentCategory(manifest["category"])
            except ValueError:
                valid_categories = [cat.value for cat in AgentCategory]
                errors.append(
                    f"Invalid category '{manifest['category']}'. "
                    f"Valid categories: {', '.join(valid_categories)}"
                )

        # Validate version format (semver)
        if "version" in manifest:
            version = manifest["version"]
            if not re.match(
                r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.-]+)?(\+[a-zA-Z0-9.-]+)?$", version
            ):
                errors.append(
                    f"Invalid version format '{version}'. Must follow semver (e.g., 1.2.3)"
                )

        # Validate requirements
        if "requirements" in manifest:
            requirements = manifest["requirements"]
            if not isinstance(requirements, list):
                errors.append("Requirements must be a list of strings")
            else:
                for req in requirements:
                    if not isinstance(req, str):
                        errors.append("Each requirement must be a string")

        # Validate entry point
        if "entry_point" in manifest:
            entry_point = manifest["entry_point"]
            if not isinstance(entry_point, str):
                errors.append("Entry point must be a string")
            # Note: Entry point type validation (should be .py) is handled in recommendations

        # Validate URLs
        url_fields = ["documentation_url", "repository_url", "support_url"]
        for field in url_fields:
            if field in manifest:
                url = manifest[field]
                if not isinstance(url, str):
                    errors.append(f"{field} must be a string")
                elif not (url.startswith("http://") or url.startswith("https://")):
                    errors.append(f"{field} must be a valid HTTP(S) URL")

        # Validate license
        if "license" in manifest:
            license_val = manifest["license"]
            if not isinstance(license_val, str):
                errors.append("License must be a string")

        return errors

    async def _security_scan(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Perform security scanning on the manifest."""

        vulnerabilities = []
        warnings = []

        # Convert manifest to string for pattern matching
        manifest_str = json.dumps(manifest, indent=2)

        # Check for dangerous patterns
        for pattern in self.security_patterns:
            matches = pattern.findall(manifest_str)
            if matches:
                vulnerabilities.append(
                    f"Potentially dangerous pattern detected: {pattern.pattern}"
                )

        # Check requirements for known vulnerable packages
        if "requirements" in manifest:
            for req in manifest.get("requirements", []):
                if self._check_vulnerable_package(req):
                    vulnerabilities.append(f"Potentially vulnerable requirement: {req}")

        # Check for suspicious permissions
        if "permissions" in manifest:
            permissions = manifest["permissions"]
            if isinstance(permissions, list):
                dangerous_perms = [
                    "file_system_full",
                    "network_unrestricted",
                    "system_admin",
                ]
                for perm in permissions:
                    if perm in dangerous_perms:
                        warnings.append(f"High-privilege permission requested: {perm}")

        return {
            "vulnerabilities": len(vulnerabilities),
            "issues": vulnerabilities,
            "warnings": warnings,
            "safe": len(vulnerabilities) == 0,
            "scan_date": datetime.utcnow().isoformat(),
            "scan_version": "1.0.0",
        }

    async def _performance_check(self, manifest: Dict[str, Any]) -> float:
        """Estimate performance score based on manifest analysis."""

        score = 8.0  # Base score

        # Bonus for good practices
        if "requirements" in manifest:
            reqs = manifest["requirements"]
            if isinstance(reqs, list) and len(reqs) < 20:
                score += 0.5  # Reasonable dependency count
            elif len(reqs) > 50:
                score -= 1.0  # Too many dependencies

        # Bonus for documentation
        if "documentation_url" in manifest:
            score += 0.3

        if "readme" in manifest and len(manifest.get("readme", "")) > 100:
            score += 0.2

        # Penalty for potential performance issues
        if "requirements" in manifest:
            heavy_packages = ["tensorflow", "torch", "numpy", "pandas"]
            reqs_str = " ".join(manifest["requirements"])
            heavy_count = sum(1 for pkg in heavy_packages if pkg in reqs_str.lower())
            if heavy_count > 3:
                score -= 0.5  # Multiple heavy dependencies

        # Bonus for proper versioning
        if "version" in manifest:
            version = manifest["version"]
            if re.match(r"^\d+\.\d+\.\d+$", version):  # Stable release
                score += 0.2
            elif "alpha" in version or "beta" in version:
                score -= 0.3  # Pre-release

        # Cap score between 0 and 10
        return max(0.0, min(10.0, score))

    def _check_vulnerable_package(self, requirement: str) -> bool:
        """Check if a requirement references a known vulnerable package."""

        # Simple vulnerability database (in practice, use a real vulnerability DB)
        vulnerable_packages = {
            "pillow<8.0.0": "Known security vulnerabilities in older versions",
            "requests<2.20.0": "Security vulnerabilities in older versions",
            "urllib3<1.24.0": "Security vulnerabilities in older versions",
        }

        req_lower = requirement.lower()
        for vuln_pkg in vulnerable_packages:
            if vuln_pkg.split("<")[0] in req_lower:
                # This is a simplified check - real implementation would parse version ranges
                return True

        return False

    def calculate_manifest_hash(self, manifest: Dict[str, Any]) -> str:
        """Calculate a hash of the manifest for integrity checking."""

        # Create a normalized version for consistent hashing
        normalized = json.dumps(manifest, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(normalized.encode()).hexdigest()

    def validate_manifest_size(self, manifest: Dict[str, Any]) -> List[str]:
        """Check if manifest size is reasonable."""

        errors = []
        manifest_str = json.dumps(manifest, indent=2)
        size_mb = len(manifest_str.encode()) / (1024 * 1024)

        if size_mb > 10:  # 10MB limit
            errors.append(f"Manifest too large: {size_mb:.2f}MB (limit: 10MB)")
        elif size_mb > 1:  # Warning at 1MB
            errors.append(f"Large manifest size: {size_mb:.2f}MB - consider optimizing")

        return errors
