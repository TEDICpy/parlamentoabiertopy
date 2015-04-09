Requirements
---------------
python 2.7
BeautifulSoup4
SQLAlchemy-0.9.9
Selemium

Installation
----------------
1. Create python and activate virtual environment
virtualenv /<path to dir>/venv
source /<path to dir>/venv/bin/activate

2. Install dependencies
pip install beautifulsoup4
pip install SQLAlchemy-0.9.9
pip install selenium



Running
-----------------
1. Load a virtual Frame Buffer
sudo Xvfb :10 -ac

2. Activate virtualenv
source /<path to dir>/venv/bin/activate

3. Run scrapper
python scrape.py
