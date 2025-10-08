# EvonyGenerals - Advanced General Management and Analysis Tool

An advanced desktop application for managing Evony: The King's Return generals using OCR technology and Google Sheets integration.

## Features

- **Advanced OCR Processing**: Extract general data with 95%+ accuracy
- **Google Sheets Integration**: Cloud-based data management and synchronization  
- **Comprehensive Analysis**: Generate detailed reports and recommendations
- **PyQt5 GUI**: Professional dark theme interface with tabbed workflow
- **BlueStacks Integration**: Seamless ADB communication with emulator

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Configure Google Sheets credentials (see `credentials_template.json`)
3. Connect to BlueStacks 5 emulator
4. Run: `python EvonyGenerals.py`

## Project Structure

```
EvonyGenerals/
├── EvonyGenerals.py         # Main application
├── EvonyADB.py              # Enhanced ADB communication
├── ManageImage.py           # Advanced image processing
├── GeneralData.py           # General data management
├── SheetsManager.py         # Google Sheets integration
├── OCREngine.py             # Specialized OCR processing
├── Resources/               # XML configs and templates
├── evony_shared.py          # Shared components
├── requirements.txt         # Dependencies
└── PRD_EvonyGenerals.md     # Complete product requirements
```

## Key Enhancements Over EvonyPresets

- **Enhanced OCR Engine**: Multi-region text extraction with confidence scoring
- **Google Sheets API**: Real-time bidirectional data synchronization
- **Advanced Data Models**: Complete general information with validation
- **Analysis & Reporting**: Statistical analysis and recommendation engine
- **Batch Processing**: Automated extraction of multiple generals

## Documentation

- [Product Requirements Document](PRD_EvonyGenerals.md) - Comprehensive specifications
- [Setup Guide](setup_guide.md) - Detailed installation instructions
- [API Documentation](api_docs.md) - Google Sheets integration details

## Requirements

- Windows 10/11
- Python 3.8+
- BlueStacks 5 emulator
- Google Sheets API credentials
- Tesseract OCR engine

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Support

For issues and questions, please use the GitHub Issues tracker.

---

**EvonyGenerals v1.0** - Advanced General Management for Evony: The King's Return