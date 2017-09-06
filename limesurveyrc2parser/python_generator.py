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
    def {function_name} (self, {function_signature}):
{function_doc}
        params = OrderedDict([
{function_payload}
        ])
        return self.query('{function_name}', params)
"""
        return template.format(
            function_name=fct_desc["name"],
            function_signature=cls.get_fct_signature(fct_desc["parameters"]),
            function_doc=cls.get_fct_doc(fct_desc["doc"]),
            function_payload=cls.get_fct_payload(fct_desc["parameters"])
        )

    @classmethod
    def get_fct_signature(cls, parameters):
        """
        :param parameters:
        :return:
        """
        return ", ".join(
            [p['py_name'] + ("" if not p['default'] else "=" + p["default"])
             for p in parameters]
        )

    @classmethod
    def get_fct_doc(cls, doc, indent=8):
        """
        Get the python docstring with a given indent based on the documenation
        that was parsed.
        :param doc: parsed documentation
        :param indent: number of characters to indent
        :return: python docstring
        """
        # TODO: Add parameter mapping
        lines = ['"""'] + doc.split("\n") + ['"""']
        # Add indent
        lines = [" " * indent + l for l in lines]

        return "\n".join(lines)

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
