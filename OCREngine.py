#!/usr/bin/env python3
"""
OCREngine - Enhanced OCR Processing Module
Specialized OCR engine for extracting and validating Evony general data with advanced image processing

Author: EvonyGenerals Development Team
Version: 1.0
Date: October 7, 2025
"""

import cv2
import numpy as np
import pytesseract
import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
import json
import os

@dataclass
class OCRRegion:
    """Defines a region for OCR processing"""
    name: str
    x: int
    y: int
    width: int
    height: int
    preprocessing: List[str] = None
    validation_pattern: str = None
    confidence_threshold: float = 0.7

@dataclass
class OCRResult:
    """Contains OCR extraction results with confidence scoring"""
    text: str
    confidence: float
    region: str
    processed_text: str = ""
    validation_passed: bool = False

class OCREngine:
    """Advanced OCR engine for Evony general data extraction"""
    
    def __init__(self, config_file: str = "ocr_config.json"):
        """
        Initialize the OCR engine with configuration
        
        Args:
            config_file: Path to OCR configuration file
        """
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config = self._load_config()
        
        # OCR regions for different general screen elements
        self.regions = self._initialize_regions()
        
        # Validation patterns for different data types
        self.validation_patterns = self._initialize_validation_patterns()
        
        # OCR configurations for different languages and content types
        self.ocr_configs = {
            'default': '--oem 3 --psm 8',
            'numbers': '--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789',
            'text_only': '--oem 3 --psm 8 -c tessedit_char_blacklist=0123456789',
            'single_word': '--oem 3 --psm 8',
            'multi_line': '--oem 3 --psm 6',
            'sparse_text': '--oem 3 --psm 11'
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Load OCR configuration from file"""
        default_config = {
            "language": "eng",
            "confidence_threshold": 0.7,
            "preprocessing": ["denoise", "enhance_contrast", "sharpen"],
            "validation_enabled": True,
            "debug_mode": False
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    default_config.update(config)
        except Exception as e:
            self.logger.warning(f"Failed to load config, using defaults: {str(e)}")
            
        return default_config
        
    def _initialize_regions(self) -> Dict[str, OCRRegion]:
        """Initialize OCR regions for general screen elements"""
        return {
            'general_name': OCRRegion(
                name='general_name',
                x=200, y=50, width=300, height=40,
                preprocessing=['denoise', 'enhance_contrast'],
                validation_pattern=r'^[A-Za-z\s\-\'\.]{2,30}$',
                confidence_threshold=0.8
            ),
            'general_level': OCRRegion(
                name='general_level',
                x=150, y=100, width=80, height=30,
                preprocessing=['enhance_contrast', 'threshold'],
                validation_pattern=r'^(Lv\.|Level\s)?(\d{1,2})$',
                confidence_threshold=0.9
            ),
            'general_stars': OCRRegion(
                name='general_stars',
                x=250, y=100, width=100, height=30,
                preprocessing=['enhance_contrast'],
                validation_pattern=r'^[1-5]\s?(Star|Stars|\*)?$',
                confidence_threshold=0.8
            ),
            'specialty': OCRRegion(
                name='specialty',
                x=200, y=150, width=200, height=40,
                preprocessing=['denoise', 'enhance_contrast'],
                validation_pattern=r'^(Attack|Defense|Leadership|Politics|Ranged|Siege|Mixed).*$',
                confidence_threshold=0.7
            ),
            'attack_stat': OCRRegion(
                name='attack_stat',
                x=100, y=200, width=100, height=30,
                preprocessing=['enhance_contrast', 'threshold'],
                validation_pattern=r'^\d{1,6}(\.\d{1,2})?[KM]?$',
                confidence_threshold=0.9
            ),
            'defense_stat': OCRRegion(
                name='defense_stat',
                x=250, y=200, width=100, height=30,
                preprocessing=['enhance_contrast', 'threshold'],
                validation_pattern=r'^\d{1,6}(\.\d{1,2})?[KM]?$',
                confidence_threshold=0.9
            ),
            'leadership_stat': OCRRegion(
                name='leadership_stat',
                x=400, y=200, width=100, height=30,
                preprocessing=['enhance_contrast', 'threshold'],
                validation_pattern=r'^\d{1,6}(\.\d{1,2})?[KM]?$',
                confidence_threshold=0.9
            ),
            'politics_stat': OCRRegion(
                name='politics_stat',
                x=550, y=200, width=100, height=30,
                preprocessing=['enhance_contrast', 'threshold'],
                validation_pattern=r'^\d{1,6}(\.\d{1,2})?[KM]?$',
                confidence_threshold=0.9
            ),
            'equipment_slot_1': OCRRegion(
                name='equipment_slot_1',
                x=100, y=300, width=80, height=80,
                preprocessing=['enhance_contrast', 'edge_detection'],
                confidence_threshold=0.6
            ),
            'equipment_slot_2': OCRRegion(
                name='equipment_slot_2',
                x=200, y=300, width=80, height=80,
                preprocessing=['enhance_contrast', 'edge_detection'],
                confidence_threshold=0.6
            ),
            'equipment_slot_3': OCRRegion(
                name='equipment_slot_3',
                x=300, y=300, width=80, height=80,
                preprocessing=['enhance_contrast', 'edge_detection'],
                confidence_threshold=0.6
            ),
            'equipment_slot_4': OCRRegion(
                name='equipment_slot_4',
                x=400, y=300, width=80, height=80,
                preprocessing=['enhance_contrast', 'edge_detection'],
                confidence_threshold=0.6
            )
        }
        
    def _initialize_validation_patterns(self) -> Dict[str, str]:
        """Initialize validation patterns for different data types"""
        return {
            'general_name': r'^[A-Za-z\s\-\'\.]{2,30}$',
            'level': r'^\d{1,2}$',
            'stars': r'^[1-5]$',
            'stat_value': r'^\d{1,6}(\.\d{1,2})?[KMB]?$',
            'specialty_type': r'^(Attack|Defense|Leadership|Politics|Ranged|Siege|Mixed|Cavalry|Infantry|Archers|Siege Machines).*$'
        }
        
    def extract_general_data(self, image_path: str) -> Dict[str, Any]:
        """
        Extract complete general data from screenshot
        
        Args:
            image_path: Path to the general screen screenshot
            
        Returns:
            Dictionary containing extracted general information
        """
        try:
            # Load the image
            image = cv2.imread(image_path)
            if image is None:
                self.logger.error(f"Failed to load image: {image_path}")
                return {}
                
            # Extract data for each region
            results = {}
            ocr_results = {}
            
            for region_name, region in self.regions.items():
                ocr_result = self._extract_region_data(image, region)
                ocr_results[region_name] = ocr_result
                
                if ocr_result and ocr_result.validation_passed:
                    results[region_name] = ocr_result.processed_text
                else:
                    results[region_name] = ""
                    
            # Post-process and structure the data
            structured_data = self._structure_general_data(results, ocr_results)
            
            if self.config.get('debug_mode', False):
                self._save_debug_info(image_path, ocr_results, structured_data)
                
            return structured_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract general data: {str(e)}")
            return {}
            
    def _extract_region_data(self, image: np.ndarray, region: OCRRegion) -> Optional[OCRResult]:
        """
        Extract text from a specific region of the image
        
        Args:
            image: Input image as numpy array
            region: OCRRegion defining the extraction area
            
        Returns:
            OCRResult with extracted text and confidence
        """
        try:
            # Extract the region of interest
            roi = image[region.y:region.y + region.height, 
                       region.x:region.x + region.width]
                       
            if roi.size == 0:
                return None
                
            # Apply preprocessing
            processed_roi = self._preprocess_image(roi, region.preprocessing or [])
            
            # Choose appropriate OCR configuration
            ocr_config = self._select_ocr_config(region.name)
            
            # Perform OCR
            try:
                # Get text and confidence data
                data = pytesseract.image_to_data(processed_roi, config=ocr_config, output_type=pytesseract.Output.DICT)
                
                # Extract text with confidence filtering
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                texts = [text for i, text in enumerate(data['text']) if int(data['conf'][i]) > 0]
                
                if not texts:
                    return OCRResult("", 0.0, region.name)
                    
                # Combine text and calculate average confidence
                extracted_text = ' '.join(texts).strip()
                avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.0
                
            except Exception as ocr_error:
                self.logger.warning(f"OCR failed for region {region.name}: {str(ocr_error)}")
                return OCRResult("", 0.0, region.name)
                
            # Process and validate the text
            processed_text = self._process_extracted_text(extracted_text, region.name)
            validation_passed = self._validate_text(processed_text, region.validation_pattern)
            
            # Check confidence threshold
            meets_threshold = avg_confidence >= region.confidence_threshold
            
            result = OCRResult(
                text=extracted_text,
                confidence=avg_confidence,
                region=region.name,
                processed_text=processed_text,
                validation_passed=validation_passed and meets_threshold
            )
            
            if self.config.get('debug_mode', False):
                self.logger.debug(f"Region {region.name}: '{extracted_text}' -> '{processed_text}' "
                                f"(conf: {avg_confidence:.2f}, valid: {validation_passed})")
                
            return result
            
        except Exception as e:
            self.logger.error(f"Failed to extract region {region.name}: {str(e)}")
            return OCRResult("", 0.0, region.name)
            
    def _preprocess_image(self, image: np.ndarray, preprocessing_steps: List[str]) -> np.ndarray:
        """
        Apply preprocessing steps to improve OCR accuracy
        
        Args:
            image: Input image as numpy array
            preprocessing_steps: List of preprocessing step names
            
        Returns:
            Preprocessed image
        """
        processed = image.copy()
        
        for step in preprocessing_steps:
            try:
                if step == 'grayscale':
                    processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                    
                elif step == 'denoise':
                    processed = cv2.fastNlMeansDenoising(processed)
                    
                elif step == 'enhance_contrast':
                    # Convert to PIL Image for enhancement
                    pil_image = Image.fromarray(cv2.cvtColor(processed, cv2.COLOR_BGR2RGB))
                    enhancer = ImageEnhance.Contrast(pil_image)
                    enhanced = enhancer.enhance(1.5)
                    processed = cv2.cvtColor(np.array(enhanced), cv2.COLOR_RGB2BGR)
                    
                elif step == 'sharpen':
                    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
                    processed = cv2.filter2D(processed, -1, kernel)
                    
                elif step == 'threshold':
                    if len(processed.shape) == 3:
                        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                    _, processed = cv2.threshold(processed, 127, 255, cv2.THRESH_BINARY)
                    
                elif step == 'edge_detection':
                    if len(processed.shape) == 3:
                        processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
                    processed = cv2.Canny(processed, 50, 150)
                    
                elif step == 'morphology':
                    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
                    
            except Exception as e:
                self.logger.warning(f"Preprocessing step '{step}' failed: {str(e)}")
                continue
                
        return processed
        
    def _select_ocr_config(self, region_name: str) -> str:
        """
        Select appropriate OCR configuration based on region type
        
        Args:
            region_name: Name of the region being processed
            
        Returns:
            OCR configuration string
        """
        if 'stat' in region_name or 'level' in region_name:
            return self.ocr_configs['numbers']
        elif 'name' in region_name:
            return self.ocr_configs['single_word']
        elif 'specialty' in region_name:
            return self.ocr_configs['text_only']
        elif 'equipment' in region_name:
            return self.ocr_configs['sparse_text']
        else:
            return self.ocr_configs['default']
            
    def _process_extracted_text(self, text: str, region_name: str) -> str:
        """
        Process extracted text based on region type
        
        Args:
            text: Raw extracted text
            region_name: Name of the region
            
        Returns:
            Processed and cleaned text
        """
        if not text:
            return ""
            
        processed = text.strip()
        
        # Region-specific processing
        if 'level' in region_name:
            # Extract numeric level from "Lv.25" or "Level 25"
            match = re.search(r'\d+', processed)
            if match:
                processed = match.group()
                
        elif 'stars' in region_name:
            # Extract star count
            match = re.search(r'[1-5]', processed)
            if match:
                processed = match.group()
                
        elif 'stat' in region_name:
            # Clean stat values - remove spaces, normalize K/M notation
            processed = re.sub(r'\s+', '', processed)
            processed = re.sub(r'(\d+)K', r'\1000', processed)
            processed = re.sub(r'(\d+)M', r'\1000000', processed)
            processed = re.sub(r'(\d+)B', r'\1000000000', processed)
            
        elif 'name' in region_name:
            # Clean general names
            processed = re.sub(r'[^A-Za-z\s\-\'\.]', '', processed)
            processed = ' '.join(processed.split())  # Normalize whitespace
            
        elif 'specialty' in region_name:
            # Standardize specialty names
            specialty_map = {
                'att': 'Attack',
                'def': 'Defense',
                'lea': 'Leadership',
                'pol': 'Politics',
                'ran': 'Ranged',
                'sie': 'Siege'
            }
            
            for abbr, full in specialty_map.items():
                if abbr.lower() in processed.lower():
                    processed = full
                    break
                    
        return processed
        
    def _validate_text(self, text: str, pattern: Optional[str]) -> bool:
        """
        Validate extracted text against pattern
        
        Args:
            text: Text to validate
            pattern: Regex pattern for validation
            
        Returns:
            True if validation passes, False otherwise
        """
        if not self.config.get('validation_enabled', True):
            return True
            
        if not pattern or not text:
            return bool(text)  # Return True if text exists when no pattern
            
        try:
            return bool(re.match(pattern, text, re.IGNORECASE))
        except Exception as e:
            self.logger.warning(f"Validation pattern error: {str(e)}")
            return True  # Default to valid if pattern fails
            
    def _structure_general_data(self, results: Dict[str, str], ocr_results: Dict[str, OCRResult]) -> Dict[str, Any]:
        """
        Structure extracted data into standard general format
        
        Args:
            results: Dictionary of extracted text results
            ocr_results: Dictionary of OCRResult objects
            
        Returns:
            Structured general data dictionary
        """
        structured = {
            'name': results.get('general_name', ''),
            'level': self._safe_int_convert(results.get('general_level', '')),
            'stars': self._safe_int_convert(results.get('general_stars', '')),
            'specialty': results.get('specialty', ''),
            'attack': self._safe_int_convert(results.get('attack_stat', '')),
            'defense': self._safe_int_convert(results.get('defense_stat', '')),
            'leadership': self._safe_int_convert(results.get('leadership_stat', '')),
            'politics': self._safe_int_convert(results.get('politics_stat', '')),
            'equipment_1': results.get('equipment_slot_1', ''),
            'equipment_2': results.get('equipment_slot_2', ''),
            'equipment_3': results.get('equipment_slot_3', ''),
            'equipment_4': results.get('equipment_slot_4', ''),
            'extraction_timestamp': self._get_timestamp(),
            'confidence_scores': {
                region: result.confidence for region, result in ocr_results.items()
            },
            'validation_status': {
                region: result.validation_passed for region, result in ocr_results.items()
            }
        }
        
        # Calculate overall confidence
        confidences = [r.confidence for r in ocr_results.values() if r.confidence > 0]
        structured['overall_confidence'] = sum(confidences) / len(confidences) if confidences else 0.0
        
        return structured
        
    def _safe_int_convert(self, value: str) -> int:
        """Safely convert string to integer"""
        try:
            return int(value) if value and value.isdigit() else 0
        except ValueError:
            return 0
            
    def _get_timestamp(self) -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
    def _save_debug_info(self, image_path: str, ocr_results: Dict[str, OCRResult], 
                        structured_data: Dict[str, Any]):
        """Save debug information for OCR analysis"""
        try:
            debug_dir = "ocr_debug"
            os.makedirs(debug_dir, exist_ok=True)
            
            timestamp = self._get_timestamp().replace(':', '-').replace(' ', '_')
            debug_file = os.path.join(debug_dir, f"debug_{timestamp}.json")
            
            debug_data = {
                'image_path': image_path,
                'ocr_results': {
                    region: {
                        'text': result.text,
                        'confidence': result.confidence,
                        'processed_text': result.processed_text,
                        'validation_passed': result.validation_passed
                    } for region, result in ocr_results.items()
                },
                'structured_data': structured_data,
                'config': self.config
            }
            
            with open(debug_file, 'w') as f:
                json.dump(debug_data, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save debug info: {str(e)}")
            
    def create_config_template(self, output_path: str = "ocr_config_template.json"):
        """Create a template OCR configuration file"""
        template_config = {
            "language": "eng",
            "confidence_threshold": 0.7,
            "preprocessing": ["denoise", "enhance_contrast", "sharpen"],
            "validation_enabled": True,
            "debug_mode": False,
            "custom_regions": {
                "example_region": {
                    "name": "custom_region",
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 50,
                    "preprocessing": ["enhance_contrast"],
                    "validation_pattern": "^[A-Za-z0-9\\s]+$",
                    "confidence_threshold": 0.8
                }
            }
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(template_config, f, indent=2)
            self.logger.info(f"OCR config template created at {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to create config template: {str(e)}")
            
    def update_regions_from_xml(self, xml_path: str):
        """Update OCR regions from XML configuration file"""
        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for region_elem in root.findall('.//region'):
                name = region_elem.get('name')
                if name:
                    x = int(region_elem.get('x', 0))
                    y = int(region_elem.get('y', 0))
                    width = int(region_elem.get('width', 100))
                    height = int(region_elem.get('height', 50))
                    
                    self.regions[name] = OCRRegion(
                        name=name, x=x, y=y, width=width, height=height
                    )
                    
            self.logger.info(f"Updated regions from XML: {xml_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to update regions from XML: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create OCR engine instance
    ocr_engine = OCREngine()
    
    # Create configuration template
    ocr_engine.create_config_template()
    
    print("OCREngine module loaded successfully")
    print("Key features:")
    print("- Advanced image preprocessing")
    print("- Multi-region OCR extraction")
    print("- Text validation and confidence scoring")
    print("- Debug mode for OCR analysis")
    print("- Configurable regions and preprocessing")