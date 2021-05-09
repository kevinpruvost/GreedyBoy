#!/usr/bin/env python
##
## GraphViewerDataMachine.py
##

__author__      = "Kevin Pruvost"
__copyright__   = "Copyright 2021, GreedyBoy"
__credits__     = ["Kevin Pruvost", "Hugo Mathieu-Steinbach"]
__license__     = "Proprietary"
__version__     = "1.0.0"
__maintainer__  = "Kevin Pruvost"
__email__       = "pruvostkevin0@gmail.com"
__status__      = "Test"

import csv
import os
import tempfile
import time
import pandas as pd
from github import Github

class GraphViewerDataMachine:

    def retrieveDataFromGithub(self):
        for i, dataPath in enumerate(self.githubDataPaths):
            try:
                githubFile = self.greedyBoyRepo.get_contents(dataPath, self.branchName)
                githubFileContent = githubFile.decoded_content.decode('ascii')
                empty = not csv.Sniffer().has_header(githubFileContent)
                if not empty:
                    try: os.makedirs(os.path.dirname(self.dataPath))
                    except: 0
                    dataFile = open(self.dataPath, "w")
                    dataFile.write(githubFileContent)
                    dataFile.close()
                    self.priceData.append(pd.read_csv(self.dataPath))
            except:
                print("Couldn't get data from " + dataPath)

    def __init__(self, githubToken, repoName, dataBranchName, currency):
        """
        :param githubToken: Github token
        :type githubToken: str
        :param repoName: Github repo name
        :type repoName: str
        :param dataBranchName: Github branch name
        :type dataBranchName: str
        """
        self.currencyInitial = currency
        self.priceData = []
        self.dataPath = tempfile.gettempdir() + "/GreedyBoy/graphViewer/" + self.currencyInitial + ".csv"
        self.githubDataFilenames = [time.strftime('%d-%m-%Y', time.localtime(time.time() - 24 * 60 * 60)) + ".csv",
                                    time.strftime('%d-%m-%Y', time.localtime(time.time())) + ".csv"]
        self.githubDataPaths = ["./price_history/" + self.currencyInitial + "/" + githubDataFilename for githubDataFilename in self.githubDataFilenames]
        self.githubToken, self.branchName = githubToken, dataBranchName

        # Github repo
        g = Github(githubToken)
        self.greedyBoyRepo = g.get_repo(repoName)

        self.retrieveDataFromGithub()

    def getData(self):
        return self.priceData