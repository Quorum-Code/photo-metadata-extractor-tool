# Library Innovation Hub

Evan Putnam '23 \
Bryan Portillo '23

## Photo Metadata Extractor Tool
The Photo-Metadata-Extractor-Tool aims to speed the processing of library documents using the SuDoc numbering scheme.
The program uses a machine learning model to extract text, like cover page titles and SuDoc numbers, from photos of 
documents. Then it searches for documents by the provided SuDoc number using OCLC's API to find corresponding documents.
Finally, the program compiles results into a CSV with all relevant information about the document.

The standard process of recording a SuDoc numbered document is a slow and uncertain workflow. Several problems can arise
while manually processing documents, such as cover titles not reflecting the actual title of the document, unreadable 
text due to wear, or any other issue with the physical document. Accessing an outside database allows for more 
information to be recorded than otherwise possible with just the physical document.

PMET has also been developed with consideration for searching for other documents and recording different resulting
information. The program can be configured through the user interface to change what kind of term the query should be
searching for, such as searching by title, government number, or many other indexes described by OCLC in their API
documentation. What data is saved from the query can be changed as well, an OCLC query can return hundreds of pieces of
information about a given document.