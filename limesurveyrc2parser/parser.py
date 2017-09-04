# -*- coding: utf-8 -*-
import requests
import pydash
import re


class LimeSurveyRc2PhpSourceParser(object):
    """
    Parser for the PHP file of the RC2 API methods.
    """

    # RE to extract doc, function name, and parameters
    RE_DOC_PUBLIC_FUNCTION_PARAM = re.compile("""
        /\*\*(.+?)(?=\*/)\*/ # doc comment - will also match preceeding docs
        \s*
        public\ function\ ([^(]+)  # function name
        \(([^)]+)\)                # parameters
        """, re.MULTILINE | re.VERBOSE | re.DOTALL)

    # simpler RE without doc string for validation purposes
    RE_PUBLIC_FUNCTION_PARAM = re.compile("""
        public\ function\ ([^(]+)  # function name
        \(([^)]+)\)                # parameters
        """, re.MULTILINE | re.VERBOSE)

    # RE to match PHP signature
    RE_SIGNATURE_PARAMETER = re.compile("([^=]+)(=(.+))?")

    @classmethod
    def parse(cls, php_source):
        """
        Extracts public functions with JS doc text and signature
        :param php_source: php sources
        :return: List of dicts with keys: "name", "doc", "parameters" with
           parameters being dicts with keys "name", "type", "default" (optional)
        """
        # Extract function names and parameters
        func_params = cls.RE_PUBLIC_FUNCTION_PARAM.findall(php_source)
        # Extract extended version with additional doc
        doc_func_params = cls.RE_DOC_PUBLIC_FUNCTION_PARAM.findall(php_source)

        # Check if there is a doc found for every function name/params
        if len(func_params) > len(doc_func_params):
            function_names_with_doc = [t[1] for t in doc_func_params]
            for f in func_params:
                if f[0] not in function_names_with_doc:
                    print("Missing function in doc: %s" % f[0])

        return [LimeSurveyRc2PhpSourceParser.get_function_description(f) for f
                in doc_func_params
                if f[1] != "__construct"]
        # with comments 39 results -> because / in comment

    @classmethod
    def get_function_description(cls, doc_func_param_match_result):
        match_doc, match_name, match_signature = doc_func_param_match_result
        # print(match_signature)
        if (re.findall("protected", match_doc)):
            pass
            # print("\n\nFUNCTION %s\n" % match_name)
            # print(clean_doc(match_doc))
            # print(match_signature)

        return {
            "name": match_name,
            "parameters": cls.extract_parameters(match_signature),
            "doc": cls.clean_doc(match_doc)
        }

    @classmethod
    def extract_parameters(cls, php_signature):
        """
        converts a PHP signature, e.g.
        "$sSessionKey, $iSurveyID,  $docType='pdf'
        to a list of dicts
        [{
          "name": "$sSessionKey"
        },{
          "name": "$iSurveyID"
        },{
          "name": "$docType"
          "default": "pdf"
        }
        :param php_signature: PHP signature
        :return: list of dicts as described
        """
        php_parameters = [p.strip() for p in php_signature.split(",")]
        result = []
        for php_parameter in php_parameters:
            match = cls.RE_SIGNATURE_PARAMETER.match(php_parameter)
            if not match:
                raise ValueError(
                    "Parameter '%s' has not the expected structure "
                    "of a PHP function parameter." % php_parameter)
            php_name, default = match[1].strip(), match[3]
            details = cls.get_details_from_php_variable(php_name)
            if default:
                details['default'] = cls.get_py_default_from_php_default(
                    default, details.get("typ", None))
            result.append(details)
        return result

    @classmethod
    def get_details_from_php_variable(cls, php_variable):
        """
        Takes a php_variable from a PHP function signature and returns an info
        dict.

        :param php_variable: e.g. $sSessionKey
        :return: e.g. {
          "name": "$sSessionKey",
          "type": "s"
        }
        """
        # See, if we have some $iRowCount or similar PHP variable name
        hungarian_match = re.match('\$([a-z])([A-Z].+)', php_variable)
        if hungarian_match:
            typ = hungarian_match.group(1)
            return {
                "name": php_variable,
                "typ": typ
            }
        else:
            return {
                "name": php_variable
            }

    @staticmethod
    def get_py_default_from_php_default(php_default, typ=None):
        php_default_map = {
            "NULL": None,
            "null": None
        }
        if php_default in php_default_map:
            return php_default_map[php_default]
        # Handle strings
        if php_default[0] == "'" and php_default[-1] == "'":
            value = php_default[1:-1]
            # Look at the type
            type_to_return_function = {
                's': str,
                'i': int
            }
            if typ:
                if typ in type_to_return_function:
                    return type_to_return_function[typ](value)
                print("WARN: Unhandled type found: '%s'" % typ)
            # Test if we have an parseable integer -
            try:
                value = int(value)
                return value
            except ValueError as e:
                pass  # Upps, this wasn't an integer
            return value  # return string value
        # catch all case
        return php_default

    @staticmethod
    def clean_doc(doc):
        # strip additional comments/non-public functions
        if "/**" in doc:
            doc = doc.split("/**")[-1]
        # strip
        doc = doc.strip()
        lines = [l.strip() for l in doc.split("\n")]
        lines = [re.sub("^\*\s?", "", l) for l in lines]
        doc = "\n".join(lines)
        #
        # TODO: remove '^\s**'. Example?
        # match_doc = re.sub("^\s+\*.?", "", match_doc, 0)
        return doc
