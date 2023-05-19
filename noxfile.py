from noxopt import NoxOpt, Session

group = NoxOpt(auto_tag=True)


@group.session
def fix_lint(session: Session) -> None:
    session.install(
        "black[jupyter]",
        "flake8-pyproject",
        "flake8",
        "isort",
    )
    session.run("black", ".")
    session.run("isort", ".")

    session.run("npm", "run", "fix:lint", external=True)


@group.session
def check_python(session: Session) -> None:
    session.install(
        "black[jupyter]",
        "flake8-pyproject",
        "flake8",
        "isort",
    )
    session.run("flake8", "reactpy_jupyter", "setup.py", "noxfile.py")
    session.run("black", "--check", ".")
    session.run("isort", "--check-only", ".")


@group.session(python=False)
def check_javascript(session: Session) -> None:
    session.run("npm", "ci", external=True)
    session.run("npm", "run", "lint", external=True)


@group.session
def publish(session: Session) -> None:
    session.install("twine", "build", "wheel")
    session.run("python", "-m", "build", "--sdist", "--wheel", "--outdir", "dist/")
    session.run("twine", "upload", "dist/*")
