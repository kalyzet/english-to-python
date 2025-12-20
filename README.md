# English to Python Translator

Aplikasi GUI yang menerjemahkan kalimat bahasa Inggris menjadi kode Python yang dapat dieksekusi.

## Features

-   GUI interface untuk input kalimat bahasa Inggris
-   Translation engine yang mengkonversi ke kode Python
-   Code generator yang menghasilkan kode Python yang valid
-   Kemampuan save/load file
-   Error handling dan feedback
-   Eksekusi kode Python langsung dari aplikasi

## Setup

### Prerequisites

-   Python 3.8 atau lebih tinggi
-   pip (Python package installer)

### Installation

1. Clone atau download project ini
2. Buat virtual environment:

    ```bash
    python -m venv venv
    ```

3. Aktifkan virtual environment:

    - Windows: `venv\Scripts\activate`
    - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

5. Download NLTK data (akan ditambahkan saat implementasi):
    ```python
    import nltk
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    ```

### Running the Application

```bash
python main.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test types
pytest -m unit          # Unit tests only
pytest -m property      # Property-based tests only
pytest -m integration   # Integration tests only

# Run with coverage
pytest --cov=src --cov-report=html
```

## Project Structure

```
english-to-python-translator/
├── src/
│   ├── models/        # Data models
│   ├── core/          # Core components (Parser, Generator)
│   ├── services/      # Service layer (Translation, Execution)
│   └── gui/           # GUI components
├── tests/
│   ├── unit/          # Unit tests
│   ├── property/      # Property-based tests
│   └── integration/   # Integration tests
├── main.py            # Application entry point
├── requirements.txt   # Dependencies
└── README.md          # This file
```

## Development Status

🚧 **In Development** - Project structure initialized, ready for implementation.

## License

MIT License
