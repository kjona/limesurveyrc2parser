from setuptools import setup
from limesurveyrc2parser import __version__

setup(
    name="limesurveyrc2parser",
    version=__version__,
    description="LimeSurvey RC2 Parser",
    url="https://github.com/kjona/limesurveyrc2parser",
    author="Jonas Kunze",
    author_email="jkd3v@gmx.de",
    packages=["limesurveyrc2parser"],
    test_suite="tests",
    include_package_data=True,
    license="Apache",
    install_requires=[
        "requests",
        "pydash"
    ],
    entry_points={
        "console_scripts": [
            "lsrc2download=script:download",
            "lsrc2generatepy=script:generate_python_code"
        ]
    },
    keywords="limesurvey api remote control parser",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
)
