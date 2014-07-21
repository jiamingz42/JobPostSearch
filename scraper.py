#!/usr/bin/env python
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from linkedin import linkedin
from oauthlib import *
import mechanize, time, re, json

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
        # return soup as None if HTTP 500 error
        if self.soupURL == url: 
            return self.soup
        else:
            # skip HTTP 500 error
            try:
                resp = self.open(url)
                html = resp.get_data()
                self.soup = BeautifulSoup(html)
            except mechanize.HTTPError, e:
                if int(e.code) == 500:
                    return None
                else:
                    raise e
            return self.soup

    def getSoup(self):
        return self.soup

    def writeSoup(self, output):
        if self.soup == None: return 
        fh = open(output,"w")
        content = self.soup.prettify()
        fh.write(unicode(content).encode("utf-8"))
        fh.close()

    def submit(self):
        resp = mechanize.Browser.submit(self)
        html = resp.get_data()
        self.soup = BeautifulSoup(html)
        return self.soup

    def stringToNum(self,strNum):
        return int(strNum.replace(",",""))

    def writeCSV(self, data, outfile):
        output = open(outfile, "w")
        for record in data:
            output.write("%s\n" % self._toString(record))
        output.close()

    def _toString(self, record):
        # record as tuple/list
        record = map(lambda str: unicode(str).encode("utf-8"),record)
        string = "\t".join(record)
        return string

    def _getDictValue(self, mydict, keychain):
        """ return the value in a nested dictionary using a order-list 
        where the former element represent a higher level key """
        res = mydict
        for key in keychain:
            if res.get(key) != None:
                res = res[key]        
            else:
                return None
        return res

class GlassdoorScraper(ExtendedBrowser):
    def __init__(self):
        ExtendedBrowser.__init__(self)

        # init instance variable
        self.start = self.end = 1

    def siteWalker(self, timeInterval):
        for (pageNum, pageURL) in self.pageGenerator():
            result = self.pageWalker(pageURL) 
            if result != None: 
                self.writeCSV(result, "name/name%05d" % pageNum)
                print pageNum
                time.sleep(timeInterval)   

    def pageWalker(self, url):
        soup = self.openSoup(url)
        if soup != None:
            result = []
            result.append(self._getName(soup))
            result.append(self._getReviewCount(soup))
            return zip(*result)
        else:
            return None

    def _getName(self, soup):
        names = []
        for company in soup.find_all("div", class_="companyData"):
            name = company.find("tt").string
            names.append(name)
        return names

    def _getReviewCount(self, soup):
        counts = []
        for company in soup.find_all("div", class_="companyData"):
            match = company.find("a", class_="noWrap").strong
            if match != None:
                # only 1 review: contain Full Reivew
                oneReview = (len(re.compile("Full Review").findall(str(match))) == 1)
                if oneReview:
                    counts.append(1) 
                else:
                    count = match.find("tt").string
                    count = self.stringToNum(count)
                    counts.append(count)
            else:
                # failed to obtain the count
                counts.append(-1)
        return counts

    def pageGenerator(self):
        template = "http://www.glassdoor.com/Reviews/company-reviews-SRCH_IP%d.htm"

        for pageNum in xrange(self.start,self.end):
            pageURL = template % pageNum
            yield pageNum, pageURL

    def setPageGenerator(self, start, end):
        self.start = start
        self.end = end

class IndeedScraper(ExtendedBrowser):
    def __init__(self):
        ExtendedBrowser.__init__(self)

    def activeJobs(self, company):
        company = company.replace(" ","+")
        template = 'http://www.indeed.com/jobs?q=company%%3A"%s"&l='
        soup = self.openSoup(template % company)
        
        # if there is result
        match = soup.find("div",id="searchCount")
        if match != None:
            pattern = re.compile("[0-9,]*$")
            jobCountString = match.string
            jobCount = pattern.findall(jobCountString).pop(0)
            return self.stringToNum(jobCount)
        else:
            return 0 
    
class LinkedinScraper(ExtendedBrowser):
    def __init__(self):
        ExtendedBrowser.__init__(self)
        self.detail = True
        self.hasLogin = False
        self.api = None

    def connectAPI(self):
        self.api_key = '75v8fr40jdwaqe'     
        self.api_secret = 'VwPaJfq3boxUjlKf' 

        self.user_token = 'ac7ee0c8-5b1e-44b7-9270-b574cec55701'  
        self.user_secret = 'fb8d1e01-052b-438d-a07c-ccb50cbcfdb8' 
        self.return_url = 'http://localhost:8000'

        config = [self.api_key, self.api_secret, 
                  self.user_token, self.user_secret,
                  self.return_url, linkedin.PERMISSIONS.enums.values()]

        authentication = linkedin.LinkedInDeveloperAuthentication(*config)

        self.api = linkedin.LinkedInApplication(authentication)

    def getCompanyInfo(self, company):
        if self.api == None: self.connectAPI()
        attr = ['id','name','industry']
        result = self.api.search_company(selectors=[{'companies': attr}], 
                                         params={'keywords': company})
        return result['companies']['values']


    def login(self, user, password):
        url = "http://www.linkedin.com/"
        self.open(url)
        
        self.select_form(nr = 0)
        self.form['session_key'] = user 
        self.form['session_password'] = password
        self.submit()

        if "Welcome!" in self.title():
            self.login = True
            if self.detail: 
                print "Login As %s (Title: %s)" % (user, self.title())
        else:
            raise Exception("Failed to Login")

    def setDetail(self, detail):
        # if self.detail is set to True, the scraper will print details
        self.detail = detail

    def searchJob(self, keyword):
        initURL = "http://www.linkedin.com/job/"
        self.openSoup(initURL)
        self.select_form("search")
        self["keywords"] = keyword
        self.submit()
        return self.soup

    def activeJobs(self, company):
        # check if log in
        companyid = self._companyid(company)
        
        template = "https://www.linkedin.com/vsearch/j?f_C=%s"
        url = template % companyid
        self.openSoup(url)

        return self._getResultCount()


    def _companyid(self, company):
        # string
        return 1512 # Apple's ID

    def _getResultCount(self):
        codeBlock = self.soup.code.string
        code = json.loads(codeBlock)
        keychain = ["content",
                    "page",
                    "voltron_unified_search_json",
                    "search",
                    "baseData",
                    "resultCount"]
        resultCount = self._getDictValue(code, keychain)
        return resultCount

    


