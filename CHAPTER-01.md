# Chapter 01: Working with Spacy

## Introduction

In this chapter, we will explore Spacy, a popular and robust Natural Language Processing (NLP) library in Python. Spacy is known for its industrial-strength performance and ease of use, making it a suitable choice for various NLP tasks such as named entity recognition, part-of-speech tagging, and dependency parsing.

## Overview of Spacy

- **Release Year**: 2015
- **Developed by**: Explosion AI
- **Language**: Python
- **Purpose**: To provide a comprehensive NLP toolkit with pre-trained models for a wide range of tasks.

### Pros

- **Ease of use**: Simple API for complex NLP tasks.
- **Speed**: Efficient and fast.
- **Accuracy**: High accuracy with pre-trained models.
- **Integration**: Easily integrates with other Python libraries.

### Cons

- **Model Size**: Large models can be memory-intensive.
- **Customization**: Custom training can be complex.
- **Dependencies**: Requires installation of specific models.

## Installation

To use Spacy, you need to install it and download a pre-trained model. Follow these steps:

### macOS and Ubuntu

```sh
# Install Spacy
pip install spacy

# Download a pre-trained model (e.g., 'en_core_web_sm')
python -m spacy download en_core_web_sm

```
import spacy

# Load pre-trained model
nlp = spacy.load("en_core_web_sm")

# Test with a sample text
doc = nlp("Hello, this is a test.")
for ent in doc.ents:
    print(ent.text, ent.label_)

```