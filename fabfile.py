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
def down(c):
    local("docker-compose down")


@task
def runserver(c):
    local(_api_cmd("python manage.py runserver 0.0.0.0:8181"))


@task
def runserverplus(c):
    local(_api_cmd("gunicorn --reload -c runserverplus.conf app.wsgi:application"))


@task
def dbshell(c):
    local(_api_cmd("python manage.py dbshell"))


@task
def shellplus(c):
    local(_api_cmd("python manage.py shell_plus"))


@task
def shell(c):
    local(_api_cmd("/bin/bash"))


@task
def test(c):
    local(_api_cmd("pytest --numprocesses=2 --cov-report=html --cov=api --verbose"))


@task
def dbbackup(c, key_name="local"):
    local(_api_cmd("python manage.py dbbackup {}".format(key_name)))


@task
def dbrestore(c, key_name="local"):
    local(_api_cmd("python manage.py dbrestore {}".format(key_name)))


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
    up(c)

    time.sleep(10)
    dbrestore(c, key_name)
    migrate(c)
