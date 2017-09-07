# -*- coding: utf-8 -*-
import re
import pydash


class LimeSurveyRc2PhpSourceParser(object):
    """
    Parser for the PHP file of the RC2 API methods.
    """

    # RE to extract doc, function name, and parameters
    RE_DOC_PUBLIC_FUNCTION_PARAM = re.compile("""
        /\*\*(.+?)(?=\*/)\*/ # doc comment - will also match preceeding docs
        \s*
        public\ function\ ([^(]+)  # function name
        \((.+?)\)$                   # parameters
        """, re.MULTILINE | re.VERBOSE | re.DOTALL)

    # simpler RE without doc string for validation purposes
    RE_PUBLIC_FUNCTION_PARAM = re.compile("""
        public\ function\ ([^(]+)  # function name
        \(([^)]+)\)                # parameters
        """, re.MULTILINE | re.VERBOSE)

    # RE to match PHP signature
    RE_SIGNATURE_PARAMETER = re.compile("([^=]+)\s*(=\s*(.+))?")

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
        if re.findall("protected", match_doc):
            pass
            # print("\n\nFUNCTION %s\n" % match_name)
            # print(clean_doc(match_doc))
            # print(match_signature)

        doc = cls.clean_doc(match_doc)

        return {
            "name": match_name,
            # doc is provided to extract parameters to determine the type
            # based on the documentation (if no hungarian type notation is
            # given)
            "parameters": cls.extract_parameters(match_signature, doc),
            "doc": doc
        }

    @classmethod
    def extract_parameters(cls, php_signature, doc=""):
        """
        converts a PHP signature, e.g.
        "$sSessionKey, $iSurveyID,  $docType='pdf'
        to a list of dicts
        [{
          "name": "$sSessionKey",
          "py_name": "session_key",
          "type": "s"
        },{
          "name": "$iSurveyID",
          "py_name": "survey_id",
          "type": "i"
        },{
          "name": "$docType",
          "py_name": "doc_type",
          "default": "pdf"
        }
        :param php_signature: PHP signature
        :param doc: PHP documentation
        :return: list of dicts as described
        """
        php_parameters = [p.strip() for p in php_signature.split(",")]
        result = []
        for php_parameter in php_parameters:
            m = cls.RE_SIGNATURE_PARAMETER.match(php_parameter)
            if not m:
                raise ValueError(
                    "Parameter '%s' has not the expected structure "
                    "of a PHP function parameter." % php_parameter)
            php_name, default = m[1].strip(), m[3]
            details = cls.get_details_from_php_variable(php_name, doc)
            if default is not None:
                details['default'] = cls.get_py_default_from_php_default(
                    default, details.get("type", None))
            result.append(details)
        return result

    @classmethod
    def get_details_from_php_variable(cls, php_variable, doc=""):
        """
        Takes a php_variable from a PHP function signature and returns an info
        dict.

        :param php_variable: e.g. $sSessionKey
        :param doc: PHP documentation
        :return: e.g. {
          "name": "$sSessionKey",
          "type": "s"
        }
        """
        php_variable_stripped = \
            php_variable[1:] if php_variable[0] == "$" else php_variable
        # See, if we have some $iRowCount or similar PHP variable name
        hungarian_match = re.match('([a-z])([A-Z].+)', php_variable_stripped)
        if hungarian_match:
            typ = hungarian_match.group(1)
            name = hungarian_match.group(2)
            return {
                "name": php_variable,
                "py_name": cls.get_py_name_from_php_name_stripped(name),
                "type": typ
            }
        else:
            doc_match = re.search(
                "@param (\S*) " + php_variable.replace("$", "\\$"), doc)
            php_doc_type2char = {
                "string": "s",
                "int": "i",
                "integer": "i",
                "bool": "b",
                "array": "a"
            }
            return {
                "name": php_variable,
                "py_name": cls.get_py_name_from_php_name_stripped(
                    php_variable_stripped),
                "type": php_doc_type2char.get(doc_match and doc_match[1])
            }

    @staticmethod
    def get_py_name_from_php_name_stripped(php_name_stripped):
        # Prior to snake_casing the name, we have to handle some special cases:

        # Missing uppercase letter in sformat
        if php_name_stripped == "sformat":
            return "format"

        # bad CamelCase for IDS:
        # groupIDs would be converted to "group_i_ds"
        name = php_name_stripped.replace("IDs", "Ids")
        return pydash.snake_case(name)

    @staticmethod
    def get_py_default_from_php_default(php_default, typ=None):
        php_default_map = {
            "NULL": None,
            "null": None,
            "true": True,
            "false": False,
            "FALSE": False,
            "array()": {},
            "Array()": {}
        }
        if php_default in php_default_map:
            return php_default_map[php_default]

        # Do we have type information?
        if typ:
            if typ == 'i':
                return int(php_default)
            elif typ == 's':
                return php_default.strip("'")
            else:
                print("typ = %s: How to handle?" % typ)

        # TODO: improve this TDD - align with above code
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
            except ValueError:
                pass  # this wasn't an integer
            return value  # return string value
        # catch all case
        print("Unexpected php_default variant: type='%s', php_default='%s'" %
              (typ, php_default))
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
