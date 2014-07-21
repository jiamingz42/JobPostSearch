#!/usr/bin/env python
# -*- coding: utf-8 -*-

from linkedin import linkedin, server
import scraper, json

def main():
    sp = scraper.LinkedinScraper()
    # sp.login("student23@163.com", "jz4kFZRBi4")
    print json.dumps(sp.getCompanyInfo("Bank of America"), indent=2)
    

    # print sp._companyid("Microsoft")

main()

