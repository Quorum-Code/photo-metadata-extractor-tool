# photo-metadata-extractor-tool (PMET)
> Tool to speed up data entry of documents using the SuDoc numbering scheme

# PMET Wiki Documentation
[View the wiki here.](https://github.com/Quorum-Code/photo-metadata-extractor-tool/wiki)

## Installing PMET on Windows

1. Install [Python 3.10](https://www.python.org/downloads/) or newer.
2. Clone or download the repository.
3. Open the command line at the project and run `pip install -r requirements.txt`. (If you get an error try adding
`--user` to the end of the command, this installs the libraries to the current user.)
4. Download [ocr_models](https://drive.google.com/drive/folders/1tK0Ib3HjTdTPSaxudCNzJOWrYOmFfigx?usp=drive_link).
5. Move the "ml_models" into the project directory following the structure outlined in the ml_model_file_structure.txt file.
6. Start the program with `python -m main`.

*Example file structure of where to place ocr_models directory.*

```
.
└── photo-metadata-extractor-tool/
    ├── classifiers
    ├── documents
    ├── ...
    └── ocr_models
```


