# limesurveyrc2parser
Parser for the LimeSurvey Remote Control API version 2.0

## Usage
After installation, just run
* `lsrc2download` (download the PHP source code to 
   the current dir)
* `lsrc2generatepy` (reads the downloaded PHP source code
   and generates a `lsrc2client.py` file)

Now, you are ready to go:
```
Python 3.6.2 (v3.6.2:5fd33b5, Jul  8 2017, 04:14:34) [MSC v.1900 32 bit (Intel)] on win32
>>> import lsrc2client
>>> client = lsrc2client.LimeSurveyClient(url="https://myserver.org/ls/index.php/admin/remotecontrol")
>>> client.get_session_key("admin", "secretpassword")
'5km5r9eabuns6bst5jp4kdmrnif35hcz'
>>> session_key = '5km5r9eabuns6bst5jp4kdmrnif35hcz'
>>> client.list_surveys(session_key)
{'status': 'No surveys found'}
```

## Credentials
The template for generating the python client code is based on the LS RC2 API 
client by Lindsay Stevens[https://github.com/lindsay-stevens/limesurveyrc2api](https://github.com/lindsay-stevens/limesurveyrc2api)