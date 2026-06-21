"""Executor to run shell commands and python code safely (with basic sandboxing)."""
import subprocess
import tempfile
import sys
import os

class Executor:
    def __init__(self, workdir=None):
        self.workdir = workdir or os.getcwd()

    def run_shell(self, cmd, timeout=120):
        """Run a shell command and return (stdout, stderr, exitcode)"""
        try:
            p = subprocess.run(cmd, shell=True, cwd=self.workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout, text=True)
            return p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            return "", f"Timeout: {e}", -1
        except Exception as e:
            return "", str(e), -2

    def run_python(self, code: str, timeout=60):
        """Run python code in a temporary file to capture stdout/stderr."""
        try:
            with tempfile.NamedTemporaryFile('w', suffix='.py', delete=False) as f:
                f.write(code)
                fname = f.name
            p = subprocess.run([sys.executable, fname], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=self.workdir, timeout=timeout, text=True)
            os.unlink(fname)
            return p.stdout, p.stderr, p.returncode
        except subprocess.TimeoutExpired as e:
            return "", f"Timeout: {e}", -1
        except Exception as e:
            return "", str(e), -2
