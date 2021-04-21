# GreedyBoy
Automated Trading Bot coded in Python, hosted on AWS Lambda.

## Requirements

|Software        |Link                                                        |
|----------------|------------------------------------------------------------|
|Python 3.7      |https://www.python.org/downloads/release/python-370/        |
|numpy           |`pip install numpy`                                         |
|websocket-client|Import in your project's folder manually from the repository|
|PyGithub        |Import in your project's folder manually from the repository|

## Configuration

### config.csv

```csv
apiKey,apiPrivateKey,githubToken,repoName,dataBranchName
$KRAKEN_API_KEY,$KRAKEN_API_PRIVATE_KEY,$GITHUB_PERSONAL_ACCESS_TOKEN,$REPOSITORY_NAME_FOR_DATA,$DATA_BRANCH_NAME
```
