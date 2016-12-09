import os
import subprocess
from uranium import task_requires, rule
from uranium.rules import Once


ROOT = os.path.dirname(os.path.realpath("__file__"))


def main(build):
    build.packages.install(".", develop=True)


@rule(Once())
@task_requires("main")
def build(build):
    build.packages.install("gunicorn")


@task_requires("main")
def test(build):
    build.packages.install("pytest")
    build.packages.install("pytest-cov")
    build.packages.install("pytest-asyncio")
    build.packages.install("radon")
    build.packages.install("flake8")
    build.executables.run([
        "pytest", "./tests",
        "--cov", "aio_graphite_web",
        "--cov-report", "term-missing",
    ] + build.options.args)
    build.executables.run([
        "flake8", "aio_graphite_web", "tests"
    ])


@task_requires("main")
def dev(build):
    build.executables.run([
        "{0}/bin/gunicorn".format(ROOT),
        "aio_graphite_web.main:app",
        "-c",
        "{0}/config/gunicorn_prod.py".format(ROOT)
    ])


def distribute(build):
    """ distribute the uranium package """
    build.packages.install("wheel")
    build.executables.run([
        "python", "setup.py",
        "sdist", "bdist_wheel", "--universal", "upload"
    ])


@task_requires("main")
def build_docs(build):
    build.packages.install("sphinx")
    build.packages.install("sphinx_rtd_theme")
    return subprocess.call(
        ["make", "html"], cwd=os.path.join(build.root, "docs")
    )
