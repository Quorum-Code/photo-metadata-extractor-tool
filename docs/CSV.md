# CSV 

The PMET program reads and writes Comma Separated Value (.csv) files.

The PMET program does not use default CSVs, instead uses the pipe character or  `|` as the separator or delimiter for its files.

## SuDoc CSV

You can create your own SuDoc CSV to skip the photo processing step of the program.
The program expects a CSV that uses the pipe character as its separator or delimiter, instead of the comma character.

The data in the CSV must be formatted as such, where the first line of the CSV is name of the column, QueryTerm.
The column can contain any data and the program will attempt to search using that as its query term.

| QueryTerm  |
|------------|
| DOCS A 123 |