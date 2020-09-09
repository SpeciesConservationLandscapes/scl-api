import os
import shlex
import subprocess
import json
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from google.cloud import storage
from google.oauth2 import service_account

BACKUP_EXTENSION = "sql"


class Command(BaseCommand):
    help = "Backup primary django database to GCP bucket"

    def __init__(self):
        super(Command, self).__init__()
        self.env = os.environ.get("ENV", "none").lower()
        print("ENV: %s" % self.env)
        self.backup = self.env
        self.local_backup_dir = os.path.join(os.path.sep, "tmp", "scl")
        try:
            os.mkdir(self.local_backup_dir)
        except OSError:
            pass  # Means it already exists.
        key = json.loads(settings.GCP_SERVICE_ACCOUNT_KEY)
        credentials = service_account.Credentials.from_service_account_info(key)
        self.client = storage.Client(
            project=settings.GCP_PROJECT_ID, credentials=credentials
        )

    def add_arguments(self, parser):
        parser.add_argument("backup", nargs="?", type=str)
        parser.add_argument(
            "-n",
            action="store_true",
            dest="no_upload",
            default=False,
            help="Do not upload dumped data to GCP",
        )

    def handle(self, *args, **options):
        # Override backup with command line arg value
        backup_name = options.get("backup")

        if backup_name:
            if not isinstance(backup_name, str):
                print("Incorrect argument type")
                return None
            self.backup = backup_name

        now = datetime.utcnow().strftime("%Y-%m-%d-%H%M%S")
        blob_name = "{}/sclbackup-{}.{}".format(self.backup, now, BACKUP_EXTENSION)
        file_name = "{}_sclbackup-{}.{}".format(self.backup, now, BACKUP_EXTENSION)
        new_backup_path = os.path.join(self.local_backup_dir, file_name)
        self._pg_dump(new_backup_path)

        if options.get("no_upload", False) is False:
            print(
                "Uploading {} to GCP bucket {}".format(
                    blob_name, settings.GCP_BUCKET_BACKUP
                )
            )
            bucket = self.client.get_bucket(settings.GCP_BUCKET_BACKUP)
            blob = bucket.blob(blob_name)
            blob.upload_from_filename(new_backup_path)
            print("Backup Complete")

    def _pg_dump(self, filename):
        params = {
            "db_user": settings.DATABASES["default"]["USER"],
            "db_host": settings.DATABASES["default"]["HOST"],
            "db_name": settings.DATABASES["default"]["NAME"],
            "dump_file": filename,
        }

        dump_command_str = (
            "pg_dump -U {db_user} -h {db_host} -d {db_name} -f {dump_file} -v"
        )
        dump_command = shlex.split(dump_command_str.format(**params))
        self._run(dump_command, to_file="/tmp/scl/std_out_backup.log")
        print("Dump Complete!")

    def _run(self, command, std_input=None, to_file=None):
        if to_file is not None:
            out_handler = open(to_file, "w")
        else:
            out_handler = subprocess.PIPE

        proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=out_handler, stderr=out_handler
        )
        data = proc.communicate(input=std_input)[0]

        if to_file is None:
            print(data)
