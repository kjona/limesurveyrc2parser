# -*- coding: utf-8 -*-
import json
from .context import limesurveyrc2parser as pkg

Parser = pkg.LimeSurveyRc2PhpSourceParser


class TestPhpParser(object):

    def test_match_php_function_re_array_default(self):
        """
        Apply RegEx to determine documentation, function name, and
        function signature. The signature contains a closing bracket.
        :return:
        """
        re = Parser.RE_DOC_PUBLIC_FUNCTION_PARAM
        match = re.findall("""/**
* doc
*/
public function fct_name($overrideAll=Array(), $p2=1)
{
    ...
}""")
        assert len(match) == 1
        assert match[0][0] == "\n* doc\n"
        assert match[0][1] == "fct_name"
        assert match[0][2] == "$overrideAll=Array(), $p2=1"

    def test_match_php_function_re_two_functions(self):
        """
        Apply RegEx to determine documentation, function name, and
        function signature for two functions
        :return:
        """
        re = Parser.RE_DOC_PUBLIC_FUNCTION_PARAM
        match = re.findall("""<?php
class remotecontrol_handle
{
    /**
    * fct1doc
    */
    public function fct1($parameter='foo', $overrideAll=Array(), $p2=1)
    {
        ...
    }

    /**
    * fct2doc
    */
    public function fct2($iStart=1)
    {
        ...
    }
}""")
        assert len(match) == 2
        assert match[0][1] == "fct1"
        assert match[0][2] == "$parameter='foo', $overrideAll=Array(), $p2=1"
        assert match[1][1] == "fct2"
        assert match[1][2] == "$iStart=1"

    def test_parse(self):
        """
        Full parse test
        :return:
        """
        php_source = """<?php
class remotecontrol_handle
{
    /**
    * protected method - should be skipped
    */
    protected $controller;

    /**
    * Constructor method - should be skipped
    */
    public function __construct(AdminController $controller)
    {
        ...
    }

    /**
    * A method
    * * remark 1 with slash /
    * @return string
    */
    public function function_name($parameter='foo', $overrideAll=Array(), $p2=1)
    {
        ...
    }
}"""
        r = Parser.parse(php_source)
        assert len(r) == 1
        parsed_function_description = r[0]
        assert parsed_function_description["name"] == "function_name"
        assert len(parsed_function_description["parameters"]) == 3
        parsed_function_parameter = parsed_function_description["parameters"][0]
        assert parsed_function_parameter["name"] == "$parameter"
        assert parsed_function_parameter["default"] == "foo"
        # print(json.dumps(r))

    def test_extract_parameter_int_default(self):
        r = Parser.extract_parameters("$iStart = 0")
        assert r[0]['name'] == '$iStart'
        assert r[0]['py_name'] == 'start'
        assert r[0]['type'] == 'i'
        assert r[0]['default'] == 0

    def test_extract_parameter_array_default(self):
        r = Parser.extract_parameters(
            "$overrideAllConditions=Array(), $iEnd=10")
        assert len(r) == 2
        assert r[0]['name'] == '$overrideAllConditions'
        assert r[0]['py_name'] == 'override_all_conditions'
        assert 'type' not in r[0]
        assert type(r[0]['default']) == dict
        assert r[1]['name'] == '$iEnd'

    def test_extract_parameters(self):
        p1 = "$sSessionKey, $sImportData, $sImportDataType, " \
             "$sNewSurveyName=NULL, $DestSurveyID=NULL"

        r = Parser.extract_parameters(p1)
        assert len(r) == 5
        assert "default" not in r[0]
        assert r[0]['name'] == '$sSessionKey'
        assert r[0]['py_name'] == 'session_key'
        assert r[0]['type'] == 's'
        assert r[1]['name'] == '$sImportData'
        assert r[1]['py_name'] == 'import_data'
        assert r[1]['type'] == 's'
        assert r[3]['default'] is None
        assert r[4]['default'] is None

        p2 = "$sSessionKey, $iSurveyID,  $docType='pdf', $sLanguage=null, " \
             "$graph='0', $groupIDs=null"
        r = Parser.extract_parameters(p2)
        assert len(r) == 6

        assert r[2]['default'] == 'pdf'
        assert r[4]['default'] == 0
        assert r[5]['default'] == None

    def test_get_details_from_php_variable(self):
        php_variable = "$sSessionKey"
        r = Parser.get_details_from_php_variable(php_variable)
        assert type(r) == dict
        assert r["name"] == php_variable
        assert r["type"] == "s"
        php_variable = "$iSurveyID"
        r = Parser.get_details_from_php_variable(php_variable)
        assert type(r) == dict
        assert r["name"] == php_variable
        assert r["py_name"] == 'survey_id'
        assert r["type"] == 'i'

    def test_clean_doc(self):
        doc = "\n    * Create and return a session key.\n    *\n    * Using this function you can create a new XML-RPC/JSON-RPC session key.\n    * This is mandatory for all following LSRC2 function calls.\n    * \n    * * In case of success : Return the session key in string\n    * * In case of error:\n    *     * for protocol-level errors (invalid format etc), an error message.\n    *     * For invalid username and password, returns a null error and the result body contains a 'status' name-value pair with the error message.\n    * \n    * @access public\n    * @param string $username\n    * @param string $password\n    * @return string|array\n    "
        expected = "Create and return a session key.\n\nUsing this function you can create a new XML-RPC/JSON-RPC session key.\nThis is mandatory for all following LSRC2 function calls.\n\n* In case of success : Return the session key in string\n* In case of error:\n    * for protocol-level errors (invalid format etc), an error message.\n    * For invalid username and password, returns a null error and the result body contains a 'status' name-value pair with the error message.\n\n@access public\n@param string $username\n@param string $password\n@return string|array"
        clean = Parser.clean_doc(doc)
        assert (clean == expected)
