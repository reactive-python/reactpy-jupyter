from noxopt import NoxOpt, Session

group = NoxOpt(auto_tag=True)


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
