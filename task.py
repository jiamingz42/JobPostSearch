#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scraper
from scraper import *
import os, time


def main():
    # glassdoor()
    # indeedActiveJobs()

    sp = scraper.LinkedinScraper()
    sp.login("student23@163.com","jz4kFZRBi4")
    
    fh = open("sample","w")
    count = 0
    for (filename, company, review) in fileGenerator("./name"):
        review = int(review)
        if review >= 200: fh.write("%s\n" % company)
        
        #     count += 1
        #     if count > 1015:
        #         print company
        #         guess_id, guess_name, jobCount = sp.activeJobs(company)
        #         record = '"%s",%s,%s,%s\n' % (company, guess_id, unicode(guess_name).encode("utf-8"), jobCount)
        #         print record.strip()
        #         fh.write(record)
        #         time.sleep(5)
    
    fh.close()
        
        

   
def indeedActiveJobs():
    fh = open("indeed","a")

    sp = scraper.IndeedScraper()
    
    for filename, company, review in fileGenerator("./name"):
        review = int(review)
        if review >= 200:
            indeed = sp.activeJobs(company)
            record =  "%s, %d, %d\n" % (company, review, indeed)
            fh.write(record)   
    fh.close()
    
    
def fileGenerator(path):
    for filename in os.listdir(path):
        fullpath = "%s/%s" % (path,filename)
        if os.path.isfile(fullpath):
            infile = open(fullpath,"r")
            records = [record.strip() for record in infile.readlines()]
            for record in records: 
                yield [filename] + record.split("\t")








main()


