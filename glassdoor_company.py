#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import mechanize

def main():
    sp = GlassdoorScraper()
    sp.setPageGenerator(1,200)
    sp.siteWalker()

class ExtendedBrowser(mechanize.Browser):
    def __init__(self):
        mechanize.Browser.__init__(self)
        
        # init browser setting
        self.set_handle_robots(False)
        self.addheaders = [('User-agent', 'Firefox')]

        # init data
        self.soup = None
        self.soupURL = None
    
    def openSoup(self, url):
        if self.soupURL == url: 
            return self.soup
        else:
            resp = self.open(url)
            html = resp.get_data()
            self.soup = BeautifulSoup(html)
            return self.soup

    def getSoup(self):
        return self.soup

    def writeSoup(self, output):
        if self.soup == None: return 
        fh = open(output,"w")
        content = self.soup.prettify()
        fh.write(unicode(content).encode("utf-8"))
        fh.close()

class GlassdoorScraper(ExtendedBrowser):
    def __init__(self):
        ExtendedBrowser.__init__(self)

        # init instance variable
        self.start = self.end = 1

    def siteWalker(self):
        for page in self.pageGenerator(self.start,self.end):
            print self.pageWalker(page)    

    def pageWalker(self, url):
        soup = self.openSoup(url)

        result = []
        for company in soup.find_all("div", class_="companyData"):
            companyName = company.find("tt").string
            result.append(companyName)

        return result

    def _getName(self, soup):
        return soup

    def pageGenerator(self, start, end):
        template = "http://www.glassdoor.com/Reviews/company-reviews-SRCH_SDOR_IP%d.htm"

        for i in xrange(start,end):
            pageURL = template % i
            yield pageURL

    def setPageGenerator(self, start, end):
        self.start = start
        self.end = end



main()


