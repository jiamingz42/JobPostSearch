#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scraper

def glassdoor():
    sp = scraper.GlassdoorScraper()
    sp.setPageGenerator(1,2)
    sp.siteWalker(0)

glassdoor()