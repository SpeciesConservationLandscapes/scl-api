import os
import shlex
import subprocess
import traceback
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from google.cloud import storage
from google.oauth2 import service_account


class Command(BaseCommand):
    help = "Restore primary django database from GCP bucket"

    def __init__(self):
        super(Command, self).__init__()
        self.restore = os.environ.get("RESTORE", "false").lower()
        self.env = os.environ.get("ENV", "none").lower()
        print("ENV: %s" % self.env)
        self.restore = self.env
        self.local_restore_dir = os.path.join(os.path.sep, "tmp", "scl")
        try:
            os.mkdir(self.local_restore_dir)
        except OSError:
            pass  # Means it already exists.
        key = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY)
        credentials = service_account.Credentials.from_service_account_info(key)
        self.client = storage.Client(
            project=settings.GCP_PROJECT_ID, credentials=credentials
        )

    def add_arguments(self, parser):
        parser.add_argument("restore", nargs="?", type=str)
        parser.add_argument(
            "-f", action="store_true", dest="force", default=False, help="Force restore"
        ),
        parser.add_argument(
            "-n",
            action="store_true",
            dest="no_download",
            default=False,
            help="Do not download dumped " "data from S3",
        )

    def handle(self, *args, **options):
        # Override backup with command line arg value
        restore_name = options.get("restore")
        if restore_name:
            if not isinstance(restore_name, str):
                print("Incorrect argument type")
                return None
            self.restore = restore_name

        if self.env == "prod" and options.get("force") is not True:
            raise Exception("Restoring production database needs to be forced.")

        if options.get("no_download", False) is True:
            file_name = None
            tmpdir = os.path.join(os.path.sep, self.local_restore_dir)

            for f in os.listdir(tmpdir):
                localfile = os.path.join(tmpdir, f)
                if os.path.isfile(localfile) and self.restore in localfile:
                    if file_name is None or os.path.getmtime(
                        localfile
                    ) > os.path.getmtime(file_name):
                        file_name = localfile

            if file_name is None:
                raise ValueError("No local files for {} found".format(self.env))
            print(file_name)

        else:
            bucket_file_list = self.client.list_blobs(settings.GCP_BUCKET_BACKUP)

            # Get key with oldest timestamp, use self.restore to identify which backup
            print("Retrieving latest backup")
            latest_blob = None
            for obj in bucket_file_list:
                if self.restore not in obj.name:
                    continue
                if latest_blob is None or obj.updated > latest_blob.updated:
                    latest_blob = obj
                    print("Latest object: {}".format(latest_blob.name))

            if latest_blob is None:
                raise ValueError("File not found")

            file_name = os.path.join(
                os.path.sep, self.local_restore_dir, latest_blob.name.replace("/", "_")
            )

            # If the file doesn't exist locally, then download
            if not os.path.isfile(file_name):
                print("Downloading {} to {} ".format(latest_blob.name, file_name))
                latest_blob.download_to_filename(file_name)
                if not os.path.isfile(file_name):
                    raise ValueError("File did not download")

        try:
            self._init_db()
            self._psql_restore_db(file_name)
            print("Restore Complete")
        except Exception as e:
            print(traceback.print_exc())
            print("Restore FAILED!")

        if options.get("no_download", False) is False:
            os.remove(file_name)

    def _init_db(self):

        params = {
            "db_user": settings.DATABASES["default"]["USER"],
            "db_host": settings.DATABASES["default"]["HOST"],
            "db_name": settings.DATABASES["default"]["NAME"],
        }

        init_db_commands = [
            """SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = $${db_name}$$;""",
            "DROP DATABASE {db_name};",
            "CREATE DATABASE {db_name} OWNER {db_user};",
            "ALTER PROCEDURAL LANGUAGE plpgsql OWNER TO {db_user};",
        ]

        cmd = "psql -a -h {db_host} -d postgres -U {db_user}".format(**params)
        for q in init_db_commands:
            query = "-c '%s'" % q
            psql_command = "%s %s" % (cmd, query.format(**params))
            print(psql_command)
            command = shlex.split(psql_command)
            self._run(command)

        print("Init Complete!")

    def _psql_restore_db(self, file_name):

        params = {
            "sql_loc": file_name,
            "db_user": settings.DATABASES["default"]["USER"],
            "db_host": settings.DATABASES["default"]["HOST"],
            "db_name": settings.DATABASES["default"]["NAME"],
        }

        cmd_str = "psql -U {db_user} -h {db_host} -d {db_name} -q -f {sql_loc}".format(
            **params
        )
        print("$> %s" % cmd_str)

        command = shlex.split(cmd_str)

        self._run(command, to_file="/tmp/scl/stdout.log")

    def _run(self, command, std_input=None, to_file=None):
        try:
            proc = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except Exception as e:
            print(command)
            raise e

        data, err = proc.communicate(input=std_input)

        if to_file is not None:
            with open(to_file, "w") as f:
                f.write("DATA: \n")
                f.write(str(data))
                f.write("ERR: \n")
                f.write(str(err))
        else:
            print(data)
            print(err)
