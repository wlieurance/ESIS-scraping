# Introduction #
The purpose of this script is to download Ecological Site Descriptions (ESDs) from the US Department of Agriculture's (USDA) Ecological Site Information System (ESIS) website.  As of the writing of this, there is no way to directly download these ESDs, which requires the user to visit each URL and print and/or download the ESD's html directly.  This script automates this process.

# Prerequisites/Installation #
This script is built in python 3.6. 'pip install -r requirements.txt' to isntall requirements.
Additionally in order to export to pdf the wkhtmltopdf library needs to be installed.
for instructions on how to get wkhtmltopdf installed on your system please see the Installation section of the [pdfkit](https://github.com/JazzCore/python-pdfkit) repository.

# Use #
py -3.6 scrape_ESIS.py "path/to/ecosite_list" "directory/to/export/in"
(note: your python call may be different depending on  your specific setup and system, e.g. python3, python3.6, py -3.5 etc.)

The ecosite_list should be file having one ecosite per line in the following format:

R023XY001NV
F036XY002CA
etc.

# Limitations #
The script will save the html and images associated with each URL, but will not save precipitation and temperature graphs, as these are JavaScript produced items (jQuery).

