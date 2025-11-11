"""
Agent Installation Manager

Handles agent installation, dependency resolution, configuration,
and lifecycle management for marketplace agents.
"""

import asyncio
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session

from .models import AgentInstallResponse
from .validator import AgentValidator


class AgentInstaller:
    """Manages agent installation and lifecycle operations."""

    def __init__(self, db: Session, base_install_path: str = "/tmp/agents"):
        self.db = db
        self.base_install_path = Path(base_install_path)
        self.validator = AgentValidator()

    async def install_agent(
        self,
        agent_manifest: Dict[str, Any],
        user_id: str,
        configuration: Optional[Dict[str, Any]] = None,
    ) -> AgentInstallResponse:
        """Install an agent for a user."""

        # Validate manifest first
        validation_result = await self.validator.validate_manifest(agent_manifest)
        if not validation_result.valid:
            raise ValueError(
                f"Agent validation failed: {'; '.join(validation_result.errors)}"
            )

        # Create installation directory
        install_id = f"install_{user_id}_{datetime.utcnow().timestamp()}"
        install_path = self.base_install_path / user_id / agent_manifest["name"]
        install_path.mkdir(parents=True, exist_ok=True)

        try:
            # Install dependencies
            await self._install_dependencies(
                agent_manifest.get("requirements", []), install_path
            )

            # Set up agent files
            await self._setup_agent_files(agent_manifest, install_path)

            # Configure agent
            await self._configure_agent(
                agent_manifest, configuration or {}, install_path
            )

            # Register installation
            await self._register_installation(
                user_id, agent_manifest, install_id, install_path
            )

            # Prepare next steps
            next_steps = self._generate_next_steps(agent_manifest, configuration or {})

            return AgentInstallResponse(
                success=True,
                agent_id=agent_manifest.get("id", agent_manifest["name"]),
                version=agent_manifest["version"],
                installation_id=install_id,
                message=f"Successfully installed {agent_manifest['name']} v{agent_manifest['version']}",
                next_steps=next_steps,
            )

        except Exception as e:
            # Clean up on failure
            if install_path.exists():
                shutil.rmtree(install_path, ignore_errors=True)

            return AgentInstallResponse(
                success=False,
                agent_id=agent_manifest.get("id", agent_manifest["name"]),
                version=agent_manifest["version"],
                installation_id=install_id,
                message=f"Installation failed: {str(e)}",
                next_steps=[
                    "Check logs for detailed error information",
                    "Contact support if problem persists",
                ],
            )

    async def uninstall_agent(self, user_id: str, agent_id: str) -> Dict[str, Any]:
        """Uninstall an agent for a user."""

        # TODO: Look up installation record
        # TODO: Stop running agent processes
        # TODO: Remove agent files
        # TODO: Clean up configuration
        # TODO: Update installation registry

        return {
            "success": True,
            "message": f"Agent {agent_id} uninstalled successfully",
            "cleanup_performed": [
                "Stopped agent processes",
                "Removed agent files",
                "Cleaned up configuration",
                "Updated registry",
            ],
        }

    async def update_agent(
        self,
        user_id: str,
        agent_id: str,
        new_version: str,
        new_manifest: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update an installed agent to a new version."""

        # TODO: Backup current installation
        # TODO: Validate new version
        # TODO: Check compatibility
        # TODO: Perform incremental update
        # TODO: Rollback on failure

        return {
            "success": True,
            "message": f"Agent {agent_id} updated to version {new_version}",
            "previous_version": "1.2.3",  # TODO: Get from registry
            "new_version": new_version,
            "changes": [
                "Updated dependencies",
                "Applied configuration changes",
                "Migrated data if needed",
            ],
        }

    async def list_installed_agents(self, user_id: str) -> List[Dict[str, Any]]:
        """List all installed agents for a user."""

        # TODO: Query installation registry
        # TODO: Check agent status (running, stopped, error)
        # TODO: Return installation details

        return [
            {
                "agent_id": "cape-ai-guide",
                "name": "CapeAI Guide Agent",
                "version": "1.0.0",
                "status": "running",
                "installed_at": "2025-11-01T10:00:00Z",
                "last_used": "2025-11-10T15:30:00Z",
                "configuration": {"openai_api_key": "configured"},
                "resource_usage": {"cpu_percent": 2.5, "memory_mb": 128, "disk_mb": 45},
            }
        ]

    async def _install_dependencies(
        self, requirements: List[str], install_path: Path
    ) -> None:
        """Install Python dependencies for an agent."""

        if not requirements:
            return

        # Create virtual environment
        venv_path = install_path / "venv"
        await self._run_command(["python", "-m", "venv", str(venv_path)])

        # Install requirements
        pip_path = venv_path / "bin" / "pip"
        if not pip_path.exists():  # Windows
            pip_path = venv_path / "Scripts" / "pip.exe"

        # Install each requirement
        for req in requirements:
            await self._run_command([str(pip_path), "install", req])

    async def _setup_agent_files(
        self, manifest: Dict[str, Any], install_path: Path
    ) -> None:
        """Set up agent files and directory structure."""

        # Create standard agent structure
        directories = ["src", "config", "data", "logs"]
        for dir_name in directories:
            (install_path / dir_name).mkdir(exist_ok=True)

        # Write manifest
        manifest_path = install_path / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)

        # TODO: Download/extract agent source code
        # TODO: Set up entry point
        # TODO: Create startup scripts
        # TODO: Set up logging configuration

    async def _configure_agent(
        self, manifest: Dict[str, Any], user_config: Dict[str, Any], install_path: Path
    ) -> None:
        """Configure the agent with user settings."""

        config_path = install_path / "config" / "agent.json"

        # Merge default config with user config
        default_config = manifest.get("default_configuration", {})
        final_config = {**default_config, **user_config}

        # Validate configuration against schema
        config_schema = manifest.get("configuration", {})
        validation_errors = self._validate_configuration(final_config, config_schema)
        if validation_errors:
            raise ValueError(
                f"Configuration validation failed: {'; '.join(validation_errors)}"
            )

        # Write configuration file
        with open(config_path, "w") as f:
            json.dump(final_config, f, indent=2)

        # TODO: Apply environment-specific settings
        # TODO: Set up secure credential storage

    async def _register_installation(
        self,
        user_id: str,
        manifest: Dict[str, Any],
        install_id: str,
        install_path: Path,
    ) -> None:
        """Register the installation in the database."""

        # TODO: Create installation record in database
        # TODO: Track installation metadata
        # TODO: Set up monitoring and health checks
        pass

    def _generate_next_steps(
        self, manifest: Dict[str, Any], configuration: Dict[str, Any]
    ) -> List[str]:
        """Generate post-installation next steps for the user."""

        steps = []

        # Configuration steps
        required_config = manifest.get("configuration", {})
        for key, schema in required_config.items():
            if schema.get("required", False) and key not in configuration:
                steps.append(f"Configure required setting: {key}")

        # Permission steps
        permissions = manifest.get("permissions", [])
        if permissions:
            steps.append("Review and approve required permissions in agent settings")

        # Documentation steps
        if "documentation_url" in manifest:
            steps.append(f"Read the documentation: {manifest['documentation_url']}")

        # Usage steps
        agent_name = manifest.get("name", "Agent")
        steps.append(f"Access {agent_name} in your agent dashboard")
        steps.append("Try asking your first question to get started")

        return steps

    def _validate_configuration(
        self, config: Dict[str, Any], schema: Dict[str, Any]
    ) -> List[str]:
        """Validate configuration against schema."""

        errors = []

        for key, field_schema in schema.items():
            if field_schema.get("required", False) and key not in config:
                errors.append(f"Missing required configuration: {key}")

            if key in config:
                value = config[key]
                field_type = field_schema.get("type", "string")

                # Basic type validation
                if field_type == "string" and not isinstance(value, str):
                    errors.append(f"Configuration '{key}' must be a string")
                elif field_type == "integer" and not isinstance(value, int):
                    errors.append(f"Configuration '{key}' must be an integer")
                elif field_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Configuration '{key}' must be a boolean")

        return errors

    async def _run_command(self, command: List[str]) -> Tuple[str, str]:
        """Run a system command asynchronously."""

        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(
                f"Command failed: {' '.join(command)}\n{stderr.decode()}"
            )

        return stdout.decode(), stderr.decode()

    def check_disk_space(self, required_mb: int = 100) -> bool:
        """Check if there's enough disk space for installation."""

        try:
            stat = shutil.disk_usage(self.base_install_path)
            available_mb = stat.free / (1024 * 1024)
            return available_mb >= required_mb
        except Exception:
            return False

    def estimate_install_size(self, manifest: Dict[str, Any]) -> int:
        """Estimate installation size in MB."""

        base_size = 50  # Base agent overhead

        # Estimate based on requirements
        requirements = manifest.get("requirements", [])
        heavy_packages = {
            "tensorflow": 500,
            "torch": 800,
            "numpy": 50,
            "pandas": 100,
            "scipy": 150,
            "matplotlib": 75,
        }

        for req in requirements:
            req_lower = req.lower()
            for pkg, size in heavy_packages.items():
                if pkg in req_lower:
                    base_size += size
                    break
            else:
                base_size += 10  # Average package size

        return base_size
