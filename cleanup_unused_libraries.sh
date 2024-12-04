#!/bin/bash

# Libraries not needed for the project
libraries=(
  "blinker"
  "certifi"
  "charset-normalizer"
  "ci-info"
  "click"
  "configobj"
  "configparser"
  "dnspython"
  "et-xmlfile"
  "etelemetry"
  "filelock"
  "fitz"
  "Flask"
  "httplib2"
  "idna"
  "isodate"
  "itsdangerous"
  "Jinja2"
  "looseversion"
  "lxml"
  "MarkupSafe"
  "networkx"
  "nibabel"
  "nipype"
  "numpy"
  "openpyxl"
  "packaging"
  "pandas"
  "pathlib"
  "prov"
  "pydot"
  "pyparsing"
  "python-dateutil"
  "pytz"
  "pyxnat"
  "rdflib"
  "scipy"
  "simplejson"
  "six"
  "soupsieve"
  "traits"
  "tzdata"
  "urllib3"
  "Werkzeug"
)

echo "Starting to uninstall unnecessary libraries..."

# Uninstall each library
for lib in "${libraries[@]}"; do
  echo "Uninstalling $lib..."
  pip uninstall -y "$lib"
done

echo "Unnecessary libraries removed successfully!"