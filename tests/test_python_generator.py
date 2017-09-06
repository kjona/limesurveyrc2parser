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
