# GreedyBoy

<p align="center">
  <img src="https://github.com/kevinpruvost/GreedyBoy/blob/main/logo/eye.png"/><br/>
  <img src="https://github.com/kevinpruvost/GreedyBoy/blob/main/logo/title.png"/><br/><br/>
Automated Trading Bot coded in Python, hosted on AWS Lambda.
</p>


## Requirements

|Software        |How to get it                                               |
|----------------|------------------------------------------------------------|
|Python 3.7      |https://www.python.org/downloads/release/python-370/        |
|numpy           |`pip install numpy`                                         |
|mpl_finance     |`pip install mpl_finance`     |
|mplcursors      |`pip install mplcursors`      |
|pandas          |`pip install pandas`          |
|sphinx          |`pip install sphinx`          |
|sphinx theme    |https://bashtage.github.io/sphinx-material/#getting-started|
|rinohtype       |`pip install rinohtype`|
|sphinx emoji    |`pip install sphinxemoji`| 

If you are exporting the project to your AWS Lambda repository, DO NOT FORGET to take the libraries folders with it.

Here's the list :

| Libraries | |
|-----------|-|
| certifi | jwt |
| requests | urllib |
| websocket | wrapt |
| chardet | deprecated |
| github | idna |

## Documentation

### [GreedyBoy Documentation](https://kevinpruvost.github.io/GreedyBoy/)

<p align="center">
  <a href="https://kevinpruvost.github.io/GreedyBoy/" target="_blank">
    <img src="https://github.com/kevinpruvost/GreedyBoy/blob/main/docsrc/_static/doc_screenshot.png" href="https://kevinpruvost.github.io/GreedyBoy/"/><br/>
  </a>
</p>

### Libraries Documentation

|Software|Link                         |
|--------|-----------------------------|
|Plotly  |https://plotly.com/python/candlestick-charts/|
|MatPlotLib Finance  | https://saralgyaan.com/posts/python-candlestick-chart-matplotlib-tutorial-chapter-11/ |
|Numba | https://numba.pydata.org/numba-doc/latest/index.html|

## Configuration

### config.csv

```csv
apiKey,apiPrivateKey,githubToken,repoName,dataBranchName
$KRAKEN_API_KEY,$KRAKEN_API_PRIVATE_KEY,$GITHUB_PERSONAL_ACCESS_TOKEN,$REPOSITORY_NAME_FOR_DATA,$DATA_BRANCH_NAME
```
