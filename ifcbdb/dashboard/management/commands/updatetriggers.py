from dashboard.models import Bin, bin_query
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
import csv
import os

from glob import glob
from collections import deque
import re
import sys

class Command(BaseCommand):

    help = 'update triggers'

    def add_arguments(self, parser):
        parser.add_argument('-i','--input', type=str, help='Path to csv of mapping of of bin ID and trigger count')
        parser.add_argument('-d', '--dataset', type=str, help='Name of dataset to process(Optional)')

    def last_line(self, filename):
        d = deque(open(filename), 1)
        try:
            return d.pop()
        except IndexError:
            return None


    def n_triggers(self, line):
        if line is None:
            return 0
        return re.match(r'^(\d+)', line).group(0)


    def get_all_bins(self, dataset=None):

        all = bin_query(dataset_name=dataset)
        for bin in all:
            # res = Bin.objects.filter(pid=bin.pid).update(n_triggers=bin._get_bin().n_triggers)
            if not os.path.exists(bin.adc_path()):
                print("Error: Bin, " + bin.pid + " adc file not found! Continuing ...")
                continue
            updated_trigger = self.n_triggers(self.last_line(bin.adc_path()))
            res = Bin.objects.filter(pid=bin.pid).update(n_triggers=updated_trigger)
            if res == 0:
                print("Error: Bin, " + bin.pid + " not updated! Continuing ...")

    def parse_input_csv(self, input_csv):
        if not os.path.exists(input_csv):
            raise CommandError('specified file does not exist')
        with open(input_csv,'r') as csvin:
            reader = csv.reader(csvin)
            row = next(reader)
            with transaction.atomic():
                for row in reader:
                    res = 0
                    res = Bin.objects.filter(pid=row[0]).update(n_triggers=row[1])
                    if res == 0:
                        print("Error: Bin, " + bin.pid + " not updated! Continuing ...")

    def handle(self, *args, **options):

        # handle arguments
        input_csv = options['input']
        dataset_name = options.get('dataset')
        
        # validate arguments
        if not input_csv:
            self.get_all_bins(dataset=dataset_name)
        else:
            self.parse_input_csv(input_csv)
        print("Done.")
        

    
