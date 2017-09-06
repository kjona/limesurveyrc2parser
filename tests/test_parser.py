# -*- coding: utf-8 -*-
import json
from .context import limesurveyrc2parser as pkg

Parser = pkg.LimeSurveyRc2PhpSourceParser


class TestParse(object):
    def test_parse(self):
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
    public function function_name($parameter='foo')
    {
        ...
    }
}"""
        r = Parser.parse(php_source)
        assert len(r) == 1
        parsed_function_description = r[0]
        assert parsed_function_description["name"] == "function_name"
        assert len(parsed_function_description["parameters"]) == 1
        parsed_function_parameter = parsed_function_description["parameters"][0]
        assert parsed_function_parameter["name"] == "$parameter"
        assert parsed_function_parameter["default"] == "foo"
        # print(json.dumps(r))

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
