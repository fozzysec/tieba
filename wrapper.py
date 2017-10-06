#!/usr/bin/env python3

import os
import sys
import time
from lxml import etree
from concurrent.futures import ProcessPoolExecutor, wait

def main(processes):
    workers = ProcessPoolExecutor(max_workers=int(processes))
    path = os.getcwd()
    tmpdir = '/tmp/row_tmp'
    summarydir = '/tmp/summary'
    dedup = 'dedup.py'
    generator = 'generator.rb'
    #COUNTER_MAX = 2
    COUNTER_MAX = 48

    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    if not os.path.exists(summarydir):
        os.makedirs(summarydir)

    config_file = '{}/row_generate.xml'.format(path)
    with open(config_file, 'r', encoding='utf8') as conf:
        doc = etree.parse(conf)
    counter = 0
    while(counter < COUNTER_MAX):
        counter += 1
        futures = []
        for node in doc.xpath('/xml/fuzz/record'):
            fuzz_keywords = node.xpath('./parent::fuzz/@keyword')[0]
            keyword_id = node.xpath('./@id')[0]
            keywords = node.xpath('./keyword/text()')[0]
            emails = node.xpath('./email/text()')
            if not os.path.exists('{}/{}/{}'.format(tmpdir, fuzz_keywords, keyword_id)):
                os.makedirs('{}/{}/{}'.format(tmpdir, fuzz_keywords, keyword_id))
            target_file = '{}/{}/{}/{}.jl'
            futures.append(workers.submit(os.system, "cd {}&&scrapy crawl tieba -s FILENAME={} -a fuzz_keywords='{}' -a keywords='{}'".format(path, target_file.format(tmpdir, fuzz_keywords, keyword_id, counter), fuzz_keywords, keywords)))
        time.sleep(30*60)
        wait(futures)
    for node in doc.xpath('/xml/fuzz/record'):
        fuzz_keywords = node.xpath('./parent::fuzz/@keyword')[0]
        keyword_id = node.xpath('./@id')[0]
        keywords = node.xpath('./keyword/text()')[0]
        emails = node.xpath('./email/text()')
        os.system('{}/{} {}/{}/{} {}/{}-{}.jl'.format(path, dedup, tmpdir, fuzz_keywords, keyword_id, summarydir, fuzz_keywords, keyword_id))
        os.system('{}/{} {}/{}-{}.jl > {}/{}-{}.html'.format(path, generator, summarydir, fuzz_keywords, keyword_id, summarydir, fuzz_keywords, keyword_id))
        for email in emails:
            sendmail = os.popen("mutt -e 'set content_type=text/html' -s '{}' {}".format(fuzz_keywords, email), 'w')
            with open('{}/{}-{}.html'.format(summarydir, fuzz_keywords, keyword_id), 'r', encoding='utf8') as f:
                for line in f.readlines():
                    sendmail.write(line)
            sendmail.close()

if __name__ == '__main__':
    main(sys.argv[1])
