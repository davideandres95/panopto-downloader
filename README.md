# TUM Panopto Downloader
You will need a token which can be found by login into tum.cloud.panopto.eu and opening the developer pannel. Then go to Application, Cookies and copy the .ASPXAUTH token.

## Usage
```sh
python3 -m venv .
source bin/activate
pip install -r requirements.txt
python3 panopto_dl.py # you must have added your personal token and desired folder structure
```

