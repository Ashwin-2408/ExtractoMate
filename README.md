# QA Text File Analyzer

## Overview

QA Text File Analyzer is a Flask-based web application that facilitates the extraction of answers from text files using Hugging Face Transformers. Users can upload sets of questions and corresponding labels, which are then applied to text files stored in a specified directory. The application extracts answers to these questions from each file and saves the results in both JSON and CSV formats. Users can download these processed files for further analysis.

## Features

- Upload questions and labels to apply to text files.
- Utilizes Hugging Face Transformers for question answering capabilities.
- Extracts answers from text files based on uploaded questions.
- Saves results as JSON and CSV files for download and detailed analysis.

## Installation

- **Clone this repository**
- **Install the dependencies**
``` bash
pip install requirements.txt
```
**Ensure that you have stored your textfiles in the DATA_FOLDER,and make sure you use the proper path to the directory**
**Run the application**
``` bash
App.py
```

