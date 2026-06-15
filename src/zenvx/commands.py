from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Optional

from .logger import logger
from .utils import MOCK


@dataclass
class CommandResult:
    argv: List[str]
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


class CommandRunner:
    def run(
        self,
        argv: List[str],
        *,
        env: Optional[Dict[str, str]] = None,
        cwd: Optional[str] = None,
        timeout_s: int = 120,
        allow_sudo: bool = False,
        runtime: str = "core",
        app_id: str = "",
    ) -> CommandResult:
        if not argv:
            raise ValueError("argv empty")

        if MOCK:
            logger.info(runtime, app_id, f"[MOCK] Would run: {shlex.join(argv)}")
            return CommandResult(argv=argv, returncode=0, stdout="", stderr="")

        if argv[0] == "sudo" and not allow_sudo:
            raise PermissionError("Refusing to run sudo without allow_sudo=True")

        merged_env = os.environ.copy()
        if env:
            merged_env.update(env)

        logger.info(runtime, app_id, f"Running: {shlex.join(argv)}")
        try:
            cp = subprocess.run(
                argv,
                env=merged_env,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout_s,
            )
            if cp.stdout:
                logger.debug(runtime, app_id, f"stdout: {cp.stdout[-4000:]}")
            if cp.stderr:
                logger.debug(runtime, app_id, f"stderr: {cp.stderr[-4000:]}")
            return CommandResult(argv=argv, returncode=cp.returncode, stdout=cp.stdout, stderr=cp.stderr)
        except subprocess.TimeoutExpired as e:
            logger.error(runtime, app_id, f"Timed out: {shlex.join(argv)}")
            return CommandResult(argv=argv, returncode=124, stdout=e.stdout or "", stderr=e.stderr or "", timed_out=True)


runner = CommandRunner()
