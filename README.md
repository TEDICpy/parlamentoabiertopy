Requirements
---------------
python 2.7
BeautifulSoup4
SQLAlchemy-0.9.9
Selemium
PhantomJS

Installation
----------------
1. Create python and activate virtual environment
virtualenv /<path to dir>/venv
source /<path to dir>/venv/bin/activate

2. Install dependencies
pip install beautifulsoup4
pip install SQLAlchemy-0.9.9
pip install selenium

2.1 Install PhantomJS
Follow the instructions from:
    https://gist.github.com/julionc/7476620#file-install_phantomjs-sh


Running
-----------------
1. Load a virtual Frame Buffer
sudo Xvfb :10 -ac

2. Activate virtualenv
source /<path to dir>/venv/bin/activate

3. Run scrapper
python scrape.py
