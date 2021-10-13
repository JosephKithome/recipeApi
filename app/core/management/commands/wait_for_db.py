import time
from django.db import connections # test if db connections is available
from django.db.utils import OperationalError # used by django to throw error if db is not available
from django.core.management import BaseCommand  # Class used to build on inorder to create custom command 


class Command(BaseCommand):
    """Django command to pause execution until db is available"""
    def handle(self, *args, **options):
        self.stdout.write("Waiting for a database...")

        db_con = None
        while not db_con:
            try:
                db_con = connections['default']
            except OperationalError:
                self.stdout.write("Database unavailable, waiting 1 second...")
                time.sleep(1)  
            self.stdout.write(self.style.SUCCESS("You're now connected to db"))      

