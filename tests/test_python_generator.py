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
        """
        Documentation generation:
        - Remove @access information
        - Rename @return
        :return:
        """
        doc = """@access public
@param string $sSessionKey Auth credentials
@param integer $iSurveyID ID of the Survey where a token table will be created for
@param array $aAttributeFields  An array of integer describing any additional attribute fields
@return array Status=>OK when successful, otherwise the error description"""
        parameters = [
            {
                "name": "$sSessionKey",
                "py_name": "session_key",
                "type": "s"
            }, {
                "name": "$iSurveyID",
                "py_name": "survey_id",
                "type": "i"
            }, {
                "name": "$aAttributeFields",
                "py_name": "attribute_fields",
                "type": "a"
            }
        ]
        result = SourceGenerator.get_fct_doc(doc=doc,
                                             parameters=parameters,
                                             indent=1)
        expected = """ \"\"\"
 :type session_key: String
 :param session_key: Auth credentials
 :type survey_id: Integer
 :param survey_id: ID of the Survey where a token table will be created for
 :type attribute_fields: OrderedDict
 :param attribute_fields:  An array of integer describing any additional attribute fields
 :return: array Status=>OK when successful, otherwise the error description
 \"\"\""""
        assert expected == result