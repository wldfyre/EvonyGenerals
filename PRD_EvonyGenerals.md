# Product Requirements Document (PRD)
## EvonyGenerals - General Management and Analysis Tool

### Document Information
- **Product Name**: EvonyGenerals
- **Version**: 1.0
- **Date**: October 7, 2025
- **Author**: EvonyGenerals Development Team
- **Status**: In Development

---

## 1. Executive Summary

EvonyGenerals is an advanced desktop application designed to automate general management for the mobile game Evony: The King's Return. The application leverages OCR technology and image processing to extract, analyze, and manage general information, integrating with Google Sheets for cloud-based data management and analysis.

## 2. Product Overview

### 2.1 Purpose
- Automate general data extraction from Evony
- Provide comprehensive general analysis and management
- Enable cloud-based general database with Google Sheets integration
- Support strategic decision-making for general optimization

### 2.2 Target Users
- Advanced Evony: The King's Return players
- Alliance leaders and strategists
- Players managing large general collections
- Data-driven strategy enthusiasts

## 3. Features and Requirements

### 3.1 Core Features

#### 3.1.1 General Data Extraction
- **Requirement**: Extract general information using OCR technology
- **Details**: Name, level, stars, specialties, abilities, and equipment
- **Priority**: High
- **Implementation**: pytesseract OCR with image preprocessing

#### 3.1.2 Google Sheets Integration
- **Requirement**: Sync general data with Google Sheets
- **Details**: Real-time data upload, template management, multi-sheet support
- **Priority**: High
- **Implementation**: gspread library with OAuth authentication

#### 3.1.3 Advanced Image Processing
- **Requirement**: Robust image analysis for general screens
- **Details**: Template matching, region detection, quality enhancement
- **Priority**: High
- **Implementation**: OpenCV with custom image filters

#### 3.1.4 General Database Management
- **Requirement**: Local and cloud general database
- **Details**: Search, filter, sort generals by various attributes
- **Priority**: Medium
- **Implementation**: SQLite local database + Google Sheets cloud

#### 3.1.5 Analysis and Reporting
- **Requirement**: Generate general performance analytics
- **Details**: Statistical analysis, recommendation engine, progress tracking
- **Priority**: Medium
- **Implementation**: pandas data analysis with visualization

### 3.2 Enhanced OCR Requirements

#### 3.2.1 Multi-Language Support
- **Requirement**: Support multiple game language settings
- **Details**: English, Chinese, Spanish, French, German
- **Priority**: Medium
- **Implementation**: pytesseract language packs

#### 3.2.2 Adaptive OCR Processing
- **Requirement**: Dynamic OCR configuration based on screen content
- **Details**: Automatic threshold adjustment, noise reduction
- **Priority**: High
- **Implementation**: OpenCV preprocessing pipelines

#### 3.2.3 Data Validation
- **Requirement**: Validate extracted OCR data for accuracy
- **Details**: Cross-reference with known general databases
- **Priority**: High
- **Implementation**: Pattern matching and data validation rules

### 3.3 Google Sheets Features

#### 3.3.1 Template Management
- **Requirement**: Pre-configured Google Sheets templates
- **Details**: General roster, specialty analysis, equipment tracking
- **Priority**: High
- **Implementation**: Template creation and deployment automation

#### 3.3.2 Real-time Synchronization
- **Requirement**: Live data sync between application and sheets
- **Details**: Bidirectional updates, conflict resolution
- **Priority**: Medium
- **Implementation**: Google Sheets API with change detection

#### 3.3.3 Collaborative Features
- **Requirement**: Multi-user access and collaboration
- **Details**: Shared sheets, permission management, audit trails
- **Priority**: Low
- **Implementation**: Google Workspace collaboration features

## 4. Technical Architecture

### 4.1 Enhanced Core Classes
- **EvonyGenerals**: Main application interface (inherited from EvonyPresets)
- **EvonyADB**: Enhanced ADB communication with general-specific methods
- **ManageImage**: Advanced image processing with OCR specialization
- **GeneralData**: Data structure for general information
- **SheetsManager**: Google Sheets integration and management
- **OCREngine**: Specialized OCR processing with validation

### 4.2 File Structure
```
EvonyGenerals/
├── EvonyGenerals.py         # Main application
├── EvonyADB.py              # Enhanced ADB communication
├── ManageImage.py           # Advanced image processing
├── GeneralData.py           # General data management
├── SheetsManager.py         # Google Sheets integration
├── OCREngine.py             # Specialized OCR processing
├── Resources/               # Enhanced XML configs and templates
│   ├── locations.xml        # General-specific screen coordinates
│   ├── templates/           # Image templates for matching
│   └── sheets_templates/    # Google Sheets templates
├── evony_shared.py          # Shared components from EvonyPresets
└── requirements.txt         # Enhanced dependencies
```

### 4.3 Data Flow Architecture
1. **Image Capture**: Screenshot general screens via ADB
2. **Image Processing**: OpenCV preprocessing and region extraction
3. **OCR Processing**: pytesseract text extraction with validation
4. **Data Parsing**: Structure extracted text into general objects
5. **Cloud Sync**: Upload/sync with Google Sheets
6. **Local Storage**: Cache data in SQLite for offline access

## 5. User Workflows

### 5.1 General Data Collection
1. Connect to BlueStacks instance
2. Navigate to Generals screen in Evony
3. Initiate automated general scanning
4. Review and validate extracted data
5. Sync to Google Sheets

### 5.2 General Analysis Workflow
1. Load general data from sheets
2. Apply filters and search criteria
3. Generate analysis reports
4. Export recommendations
5. Track general progression over time

### 5.3 Batch Processing Workflow
1. Configure OCR processing parameters
2. Select general screens for batch processing
3. Execute automated data extraction
4. Review extraction results
5. Bulk upload to Google Sheets

## 6. Integration Requirements

### 6.1 Google Sheets API
- **Authentication**: OAuth 2.0 service account
- **Permissions**: Read/write access to specified sheets
- **Rate Limits**: Respect Google API quotas and limits
- **Error Handling**: Robust retry logic and fallback options

### 6.2 OCR Engine Integration
- **Tesseract Version**: 4.1.1 or higher
- **Language Support**: Multiple OCR language packs
- **Configuration**: Custom OCR configs for game text
- **Performance**: Parallel processing for batch operations

## 7. Success Metrics

### 7.1 OCR Accuracy Metrics
- General name extraction: >95% accuracy
- Numeric data (levels, stats): >98% accuracy
- Specialty recognition: >90% accuracy
- Overall data completeness: >95%

### 7.2 Performance Metrics
- Single general processing: <5 seconds
- Batch processing rate: >10 generals/minute
- Google Sheets sync time: <10 seconds per update
- Application startup time: <8 seconds

### 7.3 User Experience Metrics
- Data extraction success rate: >90%
- UI responsiveness: <2 second response time
- Error recovery rate: >95%
- User satisfaction: >4.5/5 rating

## 8. Risk Assessment

### 8.1 Technical Risks
- **OCR Accuracy Variability**: High risk - implement validation and manual correction
- **Google Sheets API Limits**: Medium risk - implement caching and batch operations
- **Game UI Changes**: High risk - use template matching and adaptive processing
- **Performance Degradation**: Medium risk - optimize image processing pipelines

### 8.2 Data Security Risks
- **Google Sheets Access**: Medium risk - implement secure authentication
- **Personal Data**: Low risk - no sensitive personal information stored
- **API Key Management**: High risk - secure credential storage and rotation

### 8.3 Mitigation Strategies
- Comprehensive OCR validation with manual review options
- Fallback local storage when cloud sync fails
- Template-based UI element detection for game compatibility
- Encrypted credential storage and secure authentication flows

## 9. Future Enhancements

### 9.1 Advanced Analytics
- Machine learning for general performance prediction
- Automated general build recommendations
- Alliance-wide general analysis and comparison
- Historical performance tracking and trends

### 9.2 Extended Integrations
- Discord bot for general sharing and alerts
- Web dashboard for remote access
- Mobile app companion
- Integration with other Evony tools

### 9.3 AI-Powered Features
- Intelligent general categorization
- Optimal general pairing suggestions
- Battle outcome prediction based on general stats
- Automated general upgrade planning

## 10. Acceptance Criteria

### 10.1 MVP Requirements
- [ ] Connect to BlueStacks and capture general screens
- [ ] Extract general data using OCR with >90% accuracy
- [ ] Validate and structure extracted general information
- [ ] Integrate with Google Sheets for data storage
- [ ] Provide search and filter capabilities
- [ ] Support batch processing of multiple generals
- [ ] Generate basic general analysis reports

### 10.2 Quality Standards
- [ ] Robust error handling for OCR and API operations
- [ ] Comprehensive logging and debugging capabilities
- [ ] User-friendly interface with progress indicators
- [ ] Secure Google Sheets authentication
- [ ] Performance optimization for large general collections
- [ ] Comprehensive unit and integration testing

### 10.3 Integration Standards
- [ ] Seamless inheritance from EvonyPresets core classes
- [ ] Backward compatibility with existing configurations
- [ ] Modular architecture for future enhancements
- [ ] API documentation for Google Sheets integration
- [ ] Configuration management for OCR parameters

---

**Document Approval**
- Product Owner: [TBD]
- Technical Lead: [TBD]
- OCR Specialist: [TBD]
- Last Updated: October 7, 2025