# -*- coding: utf-8 -*-
from .context import limesurveyrc2parser as pkg

SourceGenerator = pkg.LimeSurveyRc2PythonSourceGenerator


class TestPythonGenerate(object):
    def test_generate(self):
        parse_result = [
            {"name": "function_name",
             "parameters": [
                 {"name": "$parameter", "py_name": "parameter",
                  "default": "foo"}],
             "doc": "A method\n* remark 1 with slash /\n@return string"}
        ]

        SourceGenerator.generate(parse_result)

    def test_generate_real(self):
        with open('resource/lsrc2source.php') as f:
            php_source = f.read()
        parse_result = pkg.LimeSurveyRc2PhpSourceParser.parse(php_source)
        py_source = SourceGenerator.generate(parse_result)
        print(py_source)

    def test_get_fct_doc(self):
        SourceGenerator.get_fct_doc(doc='')
