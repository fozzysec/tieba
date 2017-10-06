#!/usr/bin/env python3
import json
import sys
import re
from binascii import crc32
from glob import glob

def json_time(record_json):
    try:
        date = record_json['date']
        date = re.sub('[-:\s]', '', date)
        return int(date)
    except KeyError:
        return 0

records = []
for filename in glob('{}/*.jl'.format(sys.argv[1])):
    with open(filename, 'r') as f:
        for line in f.readlines():
            records.append(json.loads(line))

hash_table = []
uniq_records = []
for record in records:
    checksum = crc32(record['preview'].encode('utf8'))
    if checksum in hash_table:
        print(record['preview'])
        continue
    else:
        hash_table.append(checksum)
        uniq_records.append(record)

uniq_records.sort(key=json_time, reverse=True)
with open(sys.argv[2], 'w', encoding='utf8') as f:
    for record in uniq_records:
        record = json.dumps(record)
        f.write(record)
        f.write("\n")
