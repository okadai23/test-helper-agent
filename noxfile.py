"""Nox configuration for the project."""

import pathlib
import platform
import sys
from pathlib import Path

import nox
from nox.sessions import Session

# nox usage example
# @nox.session(python=["3.13"], venv_backend="uv", tags=["example"])
# def example(session: Session) -> None:
#     session.install("-c", constraints(session).as_posix(), ".[AAA]")  # noqa: ERA001
#     session.run("EXAMPLE_COMMAND")    # noqa: ERA001

nox.options.default_venv_backend = "uv"
nox.options.reuse_existing_virtualenvs = True

# Coverage threshold
COVER_MIN = 60


def has_test_targets() -> bool:
    """Check if there are any Python files in the src directory to test.

    Returns:
        bool: True if test target files exist, False otherwise.

    """
    src_path = pathlib.Path("src")
    if not src_path.exists():
        return False

    # Return True if any .py files exist in src directory (recursive search)
    return any(src_path.glob("**/*.py"))


def constraints(session: Session) -> Path:
    """Generate constraints file path for the session."""
    # Automatically create constraints file name
    filename = f"python{session.python}-{sys.platform}-{platform.machine()}.txt"
    return Path("constraints", filename)


@nox.session(python=["3.13"], venv_backend="uv")
def lock(session: Session) -> None:
    """Lock dependencies."""
    filename = constraints(session)
    filename.parent.mkdir(exist_ok=True)
    session.run(
        "uv",
        "pip",
        "compile",
        "pyproject.toml",
        "--upgrade",
        "--quiet",
        "--all-extras",
        f"--output-file={filename}",
    )


@nox.session(python=["3.13"], tags=["lint"])
def lint(session: Session) -> None:
    """Run linting with Ruff."""
    # Install project with all dev dependencies to ensure consistent environment
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    session.run("ruff", "check", "--fix")


@nox.session(python=["3.13"], tags=["format"])
def format_code(session: Session) -> None:
    """Format code with Ruff."""
    # Install project with all dev dependencies to ensure consistent environment
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    session.run("ruff", "format")


@nox.session(python=["3.13"], tags=["sort"])
def sort(session: Session) -> None:
    """Sort imports with Ruff."""
    # Install project with all dev dependencies to ensure consistent environment
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    session.run("ruff", "check", "--select", "I", "--fix")


@nox.session(python=["3.13"], tags=["typing"])
def typing(session: Session) -> None:
    """Run type checking with Pyright."""
    # Install project with all dev dependencies to ensure consistent environment
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    session.run("pyright")


@nox.session(python=["3.13"], tags=["test"])
def test(session: Session) -> None:
    """Run pytest if test target files exist in src directory.

    Skip otherwise.
    """
    if not has_test_targets():
        session.skip("No test targets found in src directory")

    # Install project with all dev dependencies to ensure consistent environment
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    # Ensure Playwright browser is available for e2e_web tests collected by default
    try:
        session.run("python", "-m", "playwright", "install", "chromium", external=True)
    except Exception:
        session.log(
            "playwright install chromium failed; proceeding if already installed"
        )
    session.run("pytest", "--cov=src/test_helper", f"--cov-fail-under={COVER_MIN}")


@nox.session(python=["3.13"], tags=["security"])
def security(session: Session) -> None:
    """Run security checks: pip-audit."""
    # Install project with all dev dependencies to ensure consistent environment
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    session.run("pip-audit")


@nox.session(python=["3.13"], tags=["docs"])
def docs(session: Session) -> None:
    """Build documentation with MkDocs."""
    session.install("-c", constraints(session).as_posix(), ".[docs]")
    session.run("mkdocs", "build", "--strict")


@nox.session(python=["3.13"], tags=["docs"])
def docs_sphinx(session: Session) -> None:
    """Build API documentation with Sphinx."""
    session.install("-c", constraints(session).as_posix(), ".[docs]")
    session.cd("docs")
    session.run(
        "sphinx-build",
        "-b",
        "html",
        "source",
        "build/html",
        "-W",
        "--keep-going",
    )
    session.log("Sphinx documentation built in docs/build/html/")


@nox.session(python=["3.13"], tags=["docs"])
def docs_serve(session: Session) -> None:
    """Serve MkDocs documentation locally."""
    session.install("-c", constraints(session).as_posix(), ".[docs]")
    session.run("mkdocs", "serve")


@nox.session(python=["3.13"], tags=["ci"])
def ci(session: Session) -> None:
    """Run all CI checks: lint, format, typing, test, security."""
    session.notify("lint")
    session.notify("sort")
    session.notify("format_code")
    session.notify("typing")
    session.notify("test")
    session.notify("security")


@nox.session(python=["3.13"], tags=["all"])
def all_checks(session: Session) -> None:
    """Run all quality checks.

    ci, docs.
    """
    session.notify("ci")
    session.notify("docs")


@nox.session(python=["3.13"], tags=["e2e", "test"])
def e2e_web(session: Session) -> None:
    """Run Playwright E2E tests against test_sites/."""
    # Install project with dev deps so pytest/playwright are available
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    # Ensure chromium browser is installed (best-effort)
    try:
        session.run("python", "-m", "playwright", "install", "chromium", external=True)
    except Exception:
        session.log(
            "playwright install chromium failed; proceeding if already installed",
        )
    # Run tests
    targets = session.posargs or ["tests/e2e_web"]
    session.run("pytest", "-q", *targets)


@nox.session(python=["3.13"], tags=["e2e", "test"])
def e2e_web_headed(session: Session) -> None:
    """Run Playwright E2E in headed mode with slow motion for debugging."""
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    try:
        session.run("python", "-m", "playwright", "install", "chromium", external=True)
    except Exception:
        session.log(
            "playwright install chromium failed; proceeding if already installed",
        )
    env = {
        "E2E_HEADED": "1",
        "E2E_SLOWMO": "200",
        **session.env,
    }
    targets = session.posargs or ["tests/e2e_web"]
    session.run("pytest", *targets, env=env)


@nox.session(python=["3.13"], tags=["e2e", "test"])
def e2e_web_shop_debug(session: Session) -> None:
    """Run Shop debug-mode tests that toggle SW debug API (force401)."""
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    try:
        session.run("python", "-m", "playwright", "install", "chromium", external=True)
    except Exception:
        session.log(
            "playwright install chromium failed; proceeding if already installed",
        )
    targets = session.posargs or ["tests/e2e_web/test_shop_debug_playwright.py"]
    session.run("pytest", "-q", *targets)


@nox.session(python=["3.13"], tags=["e2e", "artifacts"])
def e2e_web_trace(session: Session) -> None:
    """Run E2E with Playwright tracing enabled; artifacts under artifacts/playwright/traces."""
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    try:
        session.run("python", "-m", "playwright", "install", "chromium", external=True)
    except Exception:
        session.log(
            "playwright install chromium failed; proceeding if already installed",
        )
    env = {"E2E_TRACE": "1", **session.env}
    targets = session.posargs or ["tests/e2e_web"]
    session.run("pytest", "-q", *targets, env=env)


@nox.session(python=["3.13"], tags=["e2e", "artifacts"])
def e2e_web_video(session: Session) -> None:
    """Run E2E with video recording enabled; artifacts under artifacts/playwright/videos."""
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    try:
        session.run("python", "-m", "playwright", "install", "chromium", external=True)
    except Exception:
        session.log(
            "playwright install chromium failed; proceeding if already installed",
        )
    env = {"E2E_VIDEO": "1", **session.env}
    targets = session.posargs or ["tests/e2e_web"]
    session.run("pytest", "-q", *targets, env=env)


@nox.session(python=["3.13"], tags=["e2e", "artifacts"])
def e2e_web_video_shop(session: Session) -> None:
    """Record video for Shop tests only (lighter artifact size). Accepts extra args to narrow further."""
    session.install("-c", constraints(session).as_posix(), ".[dev,agents]")
    try:
        session.run("python", "-m", "playwright", "install", "chromium", external=True)
    except Exception:
        session.log(
            "playwright install chromium failed; proceeding if already installed",
        )
    env = {"E2E_VIDEO": "1", **session.env}
    default_targets = [
        "tests/e2e_web/test_shop_playwright.py",
        "tests/e2e_web/test_shop_debug_playwright.py",
        "tests/e2e_web/test_shop_network_playwright.py",
        "tests/e2e_web/test_shop_fail_checkout_playwright.py",
    ]
    targets = session.posargs or default_targets
    session.run("pytest", "-q", *targets, env=env)
