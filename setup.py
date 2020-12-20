#   Copyright 2020 Kevin Systrom
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#!/usr/bin/env python3

from codecs import open
from os.path import join
from setuptools import setup, find_packages
import re

DISTNAME = "rtlive"
DESCRIPTION = "Modified rt.live model"
AUTHOR = "Kyle Penner"
URL = "https://github.com/kdpenner/covid-model/tree/kpmods"
LICENSE = "Apache License, Version 2.0"

classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: Apache Software License",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering",
    "Topic :: Scientific/Engineering :: Mathematics",
    "Operating System :: OS Independent",
]

def get_version():
    VERSIONFILE = join("covid", "__init__.py")
    lines = open(VERSIONFILE, "rt").readlines()
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in lines:
        mo = re.search(version_regex, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError("Unable to find version in %s." % (VERSIONFILE,))


if __name__ == "__main__":
    setup(
        name=DISTNAME,
        version=get_version(),
        maintainer=AUTHOR,
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        packages=find_packages(),
        include_package_data=True,
        classifiers=classifiers,
        python_requires=">=3.7",
    )
