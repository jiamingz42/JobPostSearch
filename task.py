#!/usr/bin/env python
# -*- coding: utf-8 -*-
import scraper
from scraper import *
import os 


def main():
    # glassdoor()
    # indeedActiveJobs()

    sp = LinkedinScraper()
    soup = sp.openSoup("https://www.linkedin.com/company/ibm/careers")

    base = "http:/www.linkedin.com"
    url = soup.find("a", class_="see-all")["href"]

    soup = sp.openSoup("http:/www.linkedin.com/job/c-ibm-jobs?trk=biz_careers_jobslite_pub")
    print base + url

    rep = urllib2.Request("http:/www.linkedin.com/job/c-ibm-jobs?trk=biz_careers_jobslite_pub")
    f = urllib2.urlopen(req)


   
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





def glassdoor():
    sp = scraper.GlassdoorScraper()
    sp.setPageGenerator(11684,14243)
    sp.siteWalker(0)


main()


