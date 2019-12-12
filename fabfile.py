import os
import time
from fabric import task
from invoke import run


### HELPER FUNCTIONS ###
def _api_cmd(cmd):
    """Prefix the container command with the docker cmd"""
    return "docker exec -it api_service %s" % cmd


def local(command):
    run(command, pty=True)


@task
def build(c):
    local("docker-compose build")


@task
def buildnocache(c):
    local("docker-compose build --no-cache")


@task
def up(c):
    local("docker-compose up -d")


@task
def winup(c):
    path = os.path.dirname(os.path.realpath(__file__))
    local("docker-share mount -t %s/src" % path)
    up()


@task
def down(c):
    local("docker-compose down")


@task
def runserver(c):
    local(_api_cmd("python manage.py runserver 0.0.0.0:8181"))


@task
def dbshell(c):
    local(_api_cmd("python manage.py dbshell"))


@task
def shell(c):
    local(_api_cmd("/bin/bash"))


@task
def test(c):
    local(_api_cmd("pytest --numprocesses=2 --cov-report=html --cov=api --verbose"))


@task
def migrate(c):
    local(_api_cmd("python manage.py migrate"))


@task
def createdatabase(c):
    local(
        _api_cmd(
            """psql "postgresql://postgres:postgres@api_db" -c "CREATE DATABASE scl;" """
        )
    )


@task(aliases=["fresh-install"])
def freshinstall(c, key_name="local"):
    down(c)
    buildnocache(c)
    if os.name == "nt":
        winup(c)
    else:
        up(c)

    time.sleep(20)
    createdatabase(c)
    migrate(c)
    # db_restore(key_name)
    # migrate()
