# photo-metadata-extractor-tool
> Tool to speed up data entry of documents using the SuDoc numbering scheme

## Installing PMET on Windows

1. Install Python 3.10 or newer.
2. Clone or download the repository.
3. Open the command line at the project and run `pip install -r requirements.txt`.
4. Download [ocr_models](https://drive.google.com/drive/folders/1aVnQa8RhbWujhjkp-LcivGucdrFSTn4b?usp=sharing).
5. Move the "ocr_models" into the project directory.
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


