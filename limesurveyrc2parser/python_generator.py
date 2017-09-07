# -*- coding: utf-8 -*-
import os


class LimeSurveyRc2PythonSourceGenerator(object):
    """
    Generates Python client for the RC2 API methods.
    """

    @classmethod
    def generate(cls, parse_result):
        """
        Generates Python client.

        :param parse_result: result of the parser invocation
        :return: String of Python Code
        """
        template = cls.load_template()

        methods = ""
        for function_description in parse_result:
            methods += cls.get_fct(function_description)

        return template.replace("#METHODSPLACEHOLDER",
                                methods)

    @classmethod
    def load_template(cls):
        with open(os.path.join(os.path.dirname(__file__),
                               'template/python_client.py')) as f:
            return f.read()

    @classmethod
    def get_fct(cls, fct_desc):
        template = """
    def {function_name}(self, {function_signature}):
{function_doc}
        params = OrderedDict([
{function_payload}
        ])
        return self.query('{function_name}', params)
"""
        return template.format(
            function_name=fct_desc["name"],
            function_signature=cls.get_fct_signature(fct_desc["parameters"]),
            function_doc=cls.get_fct_doc(fct_desc["doc"],
                                         fct_desc["parameters"]),
            function_payload=cls.get_fct_payload(fct_desc["parameters"])
        )

    @classmethod
    def get_fct_signature(cls, parameters):
        """
        Construct the function signature (string)
        :param parameters:
        :return:
        """
        py_parameters = []
        for parameter in parameters:
            py_parameter = parameter['py_name']

            if 'default' in parameter:
                py_default = parameter['default']
                # Depending of the type of py_default, we have to create the
                # source code representation differently.
                if py_default is None:
                    py_default_string = 'None'
                elif type(py_default) == str:
                    py_default_string = '"%s"' % py_default
                # TODO: Add handling of {}. As this is mutable, we should set it
                # in the code.
                else:
                    py_default_string = str(py_default)
                py_parameter += "=" + py_default_string

            py_parameters.append(py_parameter)

        return ", ".join(py_parameters)

    @classmethod
    def get_fct_doc(cls, doc, parameters=None, indent=8):
        """
        Get the python docstring with a given indent based on the documenation
        that was parsed.
        :param doc: parsed documentation
        :param parameters: list of parameter information
        :param indent: number of characters to indent
        :return: python docstring
        """
        lines = ['"""'] + doc.split("\n") + ['"""']
        # Add indent
        lines = [" " * indent + l for l in lines]
        py_doc = "\n".join(lines)
        # Remove scope
        py_doc = py_doc.replace(" " * indent + "@access public\n", "")
        py_doc = py_doc.replace(" " * indent + "@return",
                                " " * indent + ":return:")
        # Substitute parameters
        if parameters:
            for p in parameters:
                # 1. reformat parameter spec to sphinx/reST
                if p.get("type"):
                    type2php_type_str = {
                        "i": ["integer", "int"],
                        "b": ["bool"],
                        "s": ["string", "string|null"],
                        "a": ["array", "struct", "array|null", "array|struct"],
                        "d": ["string"]
                    }
                    type2py_type_str = {
                        "i": "Integer",
                        "b": "Boolean",
                        "s": "String",
                        "a": "OrderedDict",
                        "d": "Date(as String ?)"
                    }
                    if p["type"] in type2php_type_str:
                        py_type_str = type2py_type_str[p["type"]]
                        for php_type_str in type2php_type_str[p["type"]]:
                            search = "@param %s %s" % (php_type_str, p["name"])
                            rep = \
                                ":type %s: %s" % (p["py_name"], py_type_str) + \
                                "\n" + \
                                " " * indent + ":param %s:" % p["py_name"]
                            py_doc = py_doc.replace(search, rep)

                # last: replace it with the python name
                py_doc = py_doc.replace(p["name"], p["py_name"])
        return py_doc

    @classmethod
    def get_fct_payload(cls, parameters, indent=12):
        """
        :param parameters:
        :return: payload, e.g.
            ('sSessionKey', self.session_key),
            ('sUsername', username or self.username)
        """
        lines = [
            "('{name}', {py_name})".format(name=p['name'], py_name=p['py_name'])
            for p in parameters]
        # Add indent
        lines = [" " * indent + l for l in lines]

        return ",\n".join(lines)
