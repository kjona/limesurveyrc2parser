# -*- coding: utf-8 -*-
import requests
import limesurveyrc2parser as pkg


def download():
    print("Download the PHP source for the remote control API.")
    url = "https://raw.githubusercontent.com/LimeSurvey/LimeSurvey/master/" \
          "application/helpers/remotecontrol/remotecontrol_handle.php"
    print("Download from %s" % url)
    r = requests.get(url)

    print("Save as lsrc2source.php")
    with open('lsrc2source.php', mode='w') as f:
        f.write(r.text)
    print("Done")


def generate_python_code():
    print("Generate Python client code")
    print("Read lsrc2source.php from current directory")
    with open('lsrc2source.php') as f:
        php_source = f.read()
    print("Parse lsrc2source.php")
    parse_result = pkg.LimeSurveyRc2PhpSourceParser.parse(php_source)
    print("  - contains %d function definitions." % len(parse_result))
    print("Generating Python code and writing it to lsrc2client.py")
    py_source = pkg.LimeSurveyRc2PythonSourceGenerator.generate(parse_result)
    with open('lsrc2client.py', mode='w') as f:
        f.write(py_source)
    print("Done")
