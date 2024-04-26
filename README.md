# Processing PDF statements with Python

This project takes PDF statements as inputs, extracts data and metadata out of it.
Data is cleaned, merged and then output as a single excel spreadsheet.

## Detailed process

All files in a root repository will be analyzed.
PDF files will be stored in a dictionary, as keys and each file's metadata as values.
Each file is read with Camelot, a python package to process PDf files.
First page, "inbetween" pages and last page have different structures.
Different parameters are passed to extract data properly from the files.
Then, data is cleaned and metadata is added.
Finally, data is merged into a single file, output as an excel spreadsheet.

## Built with

- Python [os, pandas, PyPDF2, camelot]

## Contributing

Contributions aren't required.
This project is just for showcase purposes.

## License

Check License.txt for further details.