Requirements
---------------
python 2.7
BeautifulSoup4
SQLAlchemy-0.9.9
Selemium

Firefox Running Headless
http://www.installationpage.com/selenium/how-to-run-selenium-headless-firefox-in-ubuntu/

Installation
----------------
1. Create python and activate virtual environment
virtualenv /<path to dir>/venv
source /<path to dir>/venv/bin/activate

2. Install dependencies
pip install beautifulsoup4
pip install SQLAlchemy-0.9.9
pip install selenium

sudo apt-get install firefox
sudo apt-get install xvfb



Running
-----------------
1. Load a virtual Frame Buffer
sudo Xvfb :10 -ac

2. Activate virtualenv
source /<path to dir>/venv/bin/activate

3. Run scrapper
python scrape.py
