#!/usr/bin/env python3
"""
GeneralData - Data Models and Structures for Evony Generals
Provides data classes, validation, serialization, and utility functions for general management

Author: EvonyGenerals Development Team
Version: 1.0
Date: October 7, 2025
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import json
import csv
import logging
from enum import Enum
import re

class SpecialtyType(Enum):
    """Enumeration of general specialty types"""
    ATTACK = "Attack"
    DEFENSE = "Defense"
    LEADERSHIP = "Leadership"
    POLITICS = "Politics"
    RANGED = "Ranged"
    SIEGE = "Siege"
    CAVALRY = "Cavalry"
    INFANTRY = "Infantry"
    ARCHERS = "Archers"
    SIEGE_MACHINES = "Siege Machines"
    MIXED = "Mixed"
    UNKNOWN = "Unknown"

class StarRating(Enum):
    """Enumeration of general star ratings"""
    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5

class GeneralStatus(Enum):
    """Enumeration of general status types"""
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    TRAINING = "Training"
    WOUNDED = "Wounded"
    ON_MARCH = "On March"
    DEFENDING = "Defending"
    UNKNOWN = "Unknown"

@dataclass
class Equipment:
    """Data class for general equipment"""
    name: str = ""
    type: str = ""  # weapon, armor, accessory, etc.
    level: int = 0
    quality: str = ""  # common, uncommon, rare, epic, legendary
    stats_bonus: Dict[str, int] = field(default_factory=dict)
    special_effects: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate equipment data after initialization"""
        if self.level < 0:
            self.level = 0
        if self.level > 50:  # Assuming max equipment level is 50
            self.level = 50
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment to dictionary"""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Equipment':
        """Create Equipment from dictionary"""
        return cls(**data)

@dataclass
class Skill:
    """Data class for general skills"""
    name: str = ""
    level: int = 0
    description: str = ""
    effect_type: str = ""  # buff, debuff, damage, etc.
    cooldown: int = 0
    mana_cost: int = 0
    
    def __post_init__(self):
        """Validate skill data after initialization"""
        if self.level < 0:
            self.level = 0
        if self.level > 10:  # Assuming max skill level is 10
            self.level = 10
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert skill to dictionary"""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Skill':
        """Create Skill from dictionary"""
        return cls(**data)

@dataclass
class GeneralStats:
    """Data class for general base statistics"""
    attack: int = 0
    defense: int = 0
    leadership: int = 0
    politics: int = 0
    
    def __post_init__(self):
        """Validate stats after initialization"""
        # Ensure all stats are non-negative
        self.attack = max(0, self.attack)
        self.defense = max(0, self.defense)
        self.leadership = max(0, self.leadership)
        self.politics = max(0, self.politics)
        
    def total_power(self) -> int:
        """Calculate total power rating"""
        return self.attack + self.defense + self.leadership + self.politics
        
    def primary_stat(self) -> str:
        """Determine the highest stat category"""
        stats = {
            'Attack': self.attack,
            'Defense': self.defense,
            'Leadership': self.leadership,
            'Politics': self.politics
        }
        return max(stats, key=stats.get)
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary"""
        return asdict(self)
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneralStats':
        """Create GeneralStats from dictionary"""
        return cls(**data)

@dataclass
class GeneralData:
    """Complete data class for Evony generals"""
    
    # Basic Information
    name: str = ""
    level: int = 1
    stars: StarRating = StarRating.ONE_STAR
    specialty: SpecialtyType = SpecialtyType.UNKNOWN
    status: GeneralStatus = GeneralStatus.ACTIVE
    
    # Statistics
    base_stats: GeneralStats = field(default_factory=GeneralStats)
    current_stats: GeneralStats = field(default_factory=GeneralStats)
    
    # Equipment and Skills
    equipment: List[Equipment] = field(default_factory=lambda: [Equipment() for _ in range(4)])
    skills: List[Skill] = field(default_factory=lambda: [Skill() for _ in range(4)])
    
    # Metadata
    general_id: str = ""
    acquisition_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    extraction_confidence: float = 0.0
    validation_status: Dict[str, bool] = field(default_factory=dict)
    notes: str = ""
    
    # OCR and Processing Data
    ocr_source_image: str = ""
    processing_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate and initialize data after creation"""
        # Validate level
        if self.level < 1:
            self.level = 1
        if self.level > 50:  # Assuming max general level is 50
            self.level = 50
            
        # Generate ID if not provided
        if not self.general_id:
            self.general_id = self._generate_id()
            
        # Set timestamps if not provided
        if not self.acquisition_date:
            self.acquisition_date = datetime.now()
        if not self.last_updated:
            self.last_updated = datetime.now()
            
        # Ensure we have exactly 4 equipment slots and 4 skill slots
        self.equipment = (self.equipment + [Equipment() for _ in range(4)])[:4]
        self.skills = (self.skills + [Skill() for _ in range(4)])[:4]
        
    def _generate_id(self) -> str:
        """Generate a unique ID for the general"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        name_part = re.sub(r'[^A-Za-z0-9]', '', self.name)[:8]
        return f"GEN_{name_part}_{timestamp}"
        
    def update_timestamp(self):
        """Update the last_updated timestamp"""
        self.last_updated = datetime.now()
        
    def calculate_total_power(self) -> int:
        """Calculate total power including equipment bonuses"""
        base_power = self.current_stats.total_power()
        equipment_power = sum(
            sum(eq.stats_bonus.values()) for eq in self.equipment if eq.name
        )
        return base_power + equipment_power
        
    def get_specialty_effectiveness(self) -> float:
        """Calculate specialty effectiveness based on stats distribution"""
        if self.specialty == SpecialtyType.ATTACK:
            return self.current_stats.attack / max(1, self.current_stats.total_power())
        elif self.specialty == SpecialtyType.DEFENSE:
            return self.current_stats.defense / max(1, self.current_stats.total_power())
        elif self.specialty == SpecialtyType.LEADERSHIP:
            return self.current_stats.leadership / max(1, self.current_stats.total_power())
        elif self.specialty == SpecialtyType.POLITICS:
            return self.current_stats.politics / max(1, self.current_stats.total_power())
        else:
            # For mixed or unknown specialties, return balanced distribution score
            stats = [self.current_stats.attack, self.current_stats.defense, 
                    self.current_stats.leadership, self.current_stats.politics]
            max_stat = max(stats) if stats else 1
            return 1.0 - (max_stat - min(stats)) / max(1, max_stat)
            
    def is_high_quality(self) -> bool:
        """Determine if this is a high-quality general"""
        criteria = [
            self.stars.value >= 4,  # 4+ stars
            self.level >= 25,       # High level
            self.calculate_total_power() >= 1000,  # High total power
            self.extraction_confidence >= 0.8,     # High confidence extraction
            len([eq for eq in self.equipment if eq.name]) >= 3  # Well equipped
        ]
        return sum(criteria) >= 3  # Meet at least 3 criteria
        
    def get_recommended_build(self) -> Dict[str, str]:
        """Get recommended build based on specialty and stats"""
        recommendations = {
            'focus': self.specialty.value,
            'primary_stat': self.current_stats.primary_stat(),
            'equipment_priority': [],
            'skill_priority': [],
            'notes': []
        }
        
        # Equipment recommendations based on specialty
        if self.specialty in [SpecialtyType.ATTACK, SpecialtyType.CAVALRY, SpecialtyType.ARCHERS]:
            recommendations['equipment_priority'] = ['Weapon', 'Attack Accessory', 'Armor', 'Boots']
        elif self.specialty in [SpecialtyType.DEFENSE, SpecialtyType.INFANTRY]:
            recommendations['equipment_priority'] = ['Armor', 'Shield', 'Defense Accessory', 'Boots']
        elif self.specialty == SpecialtyType.LEADERSHIP:
            recommendations['equipment_priority'] = ['Leadership Weapon', 'Leadership Armor', 'Troop Boost', 'March Speed']
        elif self.specialty == SpecialtyType.POLITICS:
            recommendations['equipment_priority'] = ['Research Boost', 'Building Speed', 'Resource Production', 'Politics Gear']
        else:
            recommendations['equipment_priority'] = ['Balanced Weapon', 'Balanced Armor', 'General Boost', 'Speed Boost']
            
        # Add quality notes
        if self.is_high_quality():
            recommendations['notes'].append('High-quality general - invest in premium equipment')
        if self.stars.value >= 4:
            recommendations['notes'].append('High star rating - focus on skill development')
        if self.level < 30:
            recommendations['notes'].append('Continue leveling for stat growth')
            
        return recommendations
        
    def validate_data(self) -> Dict[str, bool]:
        """Validate all general data and return status"""
        validation_results = {
            'name_valid': bool(self.name and len(self.name.strip()) > 1),
            'level_valid': 1 <= self.level <= 50,
            'stars_valid': isinstance(self.stars, StarRating),
            'specialty_valid': isinstance(self.specialty, SpecialtyType),
            'stats_valid': all(stat >= 0 for stat in [
                self.current_stats.attack, self.current_stats.defense,
                self.current_stats.leadership, self.current_stats.politics
            ]),
            'equipment_valid': len(self.equipment) == 4,
            'skills_valid': len(self.skills) == 4,
            'confidence_valid': 0.0 <= self.extraction_confidence <= 1.0
        }
        
        validation_results['overall_valid'] = all(validation_results.values())
        self.validation_status = validation_results
        return validation_results
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert general data to dictionary for serialization"""
        data = {
            'general_id': self.general_id,
            'name': self.name,
            'level': self.level,
            'stars': self.stars.value if isinstance(self.stars, StarRating) else self.stars,
            'specialty': self.specialty.value if isinstance(self.specialty, SpecialtyType) else self.specialty,
            'status': self.status.value if isinstance(self.status, GeneralStatus) else self.status,
            'base_stats': self.base_stats.to_dict(),
            'current_stats': self.current_stats.to_dict(),
            'equipment': [eq.to_dict() for eq in self.equipment],
            'skills': [skill.to_dict() for skill in self.skills],
            'acquisition_date': self.acquisition_date.isoformat() if self.acquisition_date else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'extraction_confidence': self.extraction_confidence,
            'validation_status': self.validation_status,
            'notes': self.notes,
            'ocr_source_image': self.ocr_source_image,
            'processing_metadata': self.processing_metadata,
            'total_power': self.calculate_total_power(),
            'specialty_effectiveness': self.get_specialty_effectiveness(),
            'is_high_quality': self.is_high_quality()
        }
        return data
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeneralData':
        """Create GeneralData from dictionary"""
        # Handle enum conversions
        if 'stars' in data and isinstance(data['stars'], int):
            data['stars'] = StarRating(data['stars'])
        if 'specialty' in data and isinstance(data['specialty'], str):
            try:
                data['specialty'] = SpecialtyType(data['specialty'])
            except ValueError:
                data['specialty'] = SpecialtyType.UNKNOWN
        if 'status' in data and isinstance(data['status'], str):
            try:
                data['status'] = GeneralStatus(data['status'])
            except ValueError:
                data['status'] = GeneralStatus.UNKNOWN
                
        # Handle datetime conversions
        if 'acquisition_date' in data and isinstance(data['acquisition_date'], str):
            data['acquisition_date'] = datetime.fromisoformat(data['acquisition_date'])
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
            
        # Handle nested objects
        if 'base_stats' in data and isinstance(data['base_stats'], dict):
            data['base_stats'] = GeneralStats.from_dict(data['base_stats'])
        if 'current_stats' in data and isinstance(data['current_stats'], dict):
            data['current_stats'] = GeneralStats.from_dict(data['current_stats'])
        if 'equipment' in data and isinstance(data['equipment'], list):
            data['equipment'] = [Equipment.from_dict(eq) for eq in data['equipment']]
        if 'skills' in data and isinstance(data['skills'], list):
            data['skills'] = [Skill.from_dict(skill) for skill in data['skills']]
            
        # Remove computed fields that shouldn't be in constructor
        computed_fields = ['total_power', 'specialty_effectiveness', 'is_high_quality']
        for field in computed_fields:
            data.pop(field, None)
            
        return cls(**data)
        
    def to_json(self, indent: int = 2) -> str:
        """Convert general data to JSON string"""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
        
    @classmethod
    def from_json(cls, json_str: str) -> 'GeneralData':
        """Create GeneralData from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
        
    def to_csv_row(self) -> List[str]:
        """Convert general data to CSV row format"""
        return [
            self.general_id,
            self.name,
            str(self.level),
            str(self.stars.value),
            self.specialty.value,
            self.status.value,
            str(self.current_stats.attack),
            str(self.current_stats.defense),
            str(self.current_stats.leadership),
            str(self.current_stats.politics),
            str(self.calculate_total_power()),
            f"{self.get_specialty_effectiveness():.2f}",
            str(self.is_high_quality()),
            str(self.extraction_confidence),
            self.last_updated.isoformat() if self.last_updated else "",
            self.notes
        ]
        
    @classmethod
    def get_csv_headers(cls) -> List[str]:
        """Get CSV headers for general data"""
        return [
            'General_ID', 'Name', 'Level', 'Stars', 'Specialty', 'Status',
            'Attack', 'Defense', 'Leadership', 'Politics', 'Total_Power',
            'Specialty_Effectiveness', 'High_Quality', 'Extraction_Confidence',
            'Last_Updated', 'Notes'
        ]

class GeneralCollection:
    """Collection class for managing multiple generals"""
    
    def __init__(self):
        self.generals: Dict[str, GeneralData] = {}
        self.logger = logging.getLogger(__name__)
        
    def add_general(self, general: GeneralData) -> bool:
        """Add a general to the collection"""
        try:
            general.validate_data()
            self.generals[general.general_id] = general
            self.logger.info(f"Added general: {general.name} (ID: {general.general_id})")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add general {general.name}: {str(e)}")
            return False
            
    def remove_general(self, general_id: str) -> bool:
        """Remove a general from the collection"""
        if general_id in self.generals:
            removed = self.generals.pop(general_id)
            self.logger.info(f"Removed general: {removed.name} (ID: {general_id})")
            return True
        return False
        
    def get_general(self, general_id: str) -> Optional[GeneralData]:
        """Get a general by ID"""
        return self.generals.get(general_id)
        
    def find_by_name(self, name: str) -> List[GeneralData]:
        """Find generals by name (partial match)"""
        name_lower = name.lower()
        return [g for g in self.generals.values() if name_lower in g.name.lower()]
        
    def filter_by_specialty(self, specialty: SpecialtyType) -> List[GeneralData]:
        """Filter generals by specialty"""
        return [g for g in self.generals.values() if g.specialty == specialty]
        
    def filter_by_stars(self, min_stars: int, max_stars: int = 5) -> List[GeneralData]:
        """Filter generals by star rating"""
        return [g for g in self.generals.values() 
                if min_stars <= g.stars.value <= max_stars]
        
    def filter_by_level(self, min_level: int, max_level: int = 50) -> List[GeneralData]:
        """Filter generals by level"""
        return [g for g in self.generals.values() 
                if min_level <= g.level <= max_level]
        
    def get_high_quality_generals(self) -> List[GeneralData]:
        """Get all high-quality generals"""
        return [g for g in self.generals.values() if g.is_high_quality()]
        
    def get_top_generals(self, count: int = 10, sort_by: str = 'total_power') -> List[GeneralData]:
        """Get top generals sorted by specified criteria"""
        all_generals = list(self.generals.values())
        
        if sort_by == 'total_power':
            all_generals.sort(key=lambda g: g.calculate_total_power(), reverse=True)
        elif sort_by == 'level':
            all_generals.sort(key=lambda g: g.level, reverse=True)
        elif sort_by == 'stars':
            all_generals.sort(key=lambda g: g.stars.value, reverse=True)
        elif sort_by == 'specialty_effectiveness':
            all_generals.sort(key=lambda g: g.get_specialty_effectiveness(), reverse=True)
        
        return all_generals[:count]
        
    def get_statistics(self) -> Dict[str, Any]:
        """Get collection statistics"""
        if not self.generals:
            return {'total': 0}
            
        generals_list = list(self.generals.values())
        
        stats = {
            'total': len(generals_list),
            'average_level': sum(g.level for g in generals_list) / len(generals_list),
            'average_power': sum(g.calculate_total_power() for g in generals_list) / len(generals_list),
            'high_quality_count': len(self.get_high_quality_generals()),
            'specialty_distribution': {},
            'star_distribution': {},
            'level_distribution': {'1-10': 0, '11-20': 0, '21-30': 0, '31-40': 0, '41-50': 0}
        }
        
        # Calculate distributions
        for general in generals_list:
            # Specialty distribution
            specialty = general.specialty.value
            stats['specialty_distribution'][specialty] = stats['specialty_distribution'].get(specialty, 0) + 1
            
            # Star distribution
            stars = str(general.stars.value)
            stats['star_distribution'][stars] = stats['star_distribution'].get(stars, 0) + 1
            
            # Level distribution
            if general.level <= 10:
                stats['level_distribution']['1-10'] += 1
            elif general.level <= 20:
                stats['level_distribution']['11-20'] += 1
            elif general.level <= 30:
                stats['level_distribution']['21-30'] += 1
            elif general.level <= 40:
                stats['level_distribution']['31-40'] += 1
            else:
                stats['level_distribution']['41-50'] += 1
                
        return stats
        
    def export_to_csv(self, filename: str) -> bool:
        """Export collection to CSV file"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(GeneralData.get_csv_headers())
                
                for general in self.generals.values():
                    writer.writerow(general.to_csv_row())
                    
            self.logger.info(f"Exported {len(self.generals)} generals to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to export to CSV: {str(e)}")
            return False
            
    def import_from_csv(self, filename: str) -> int:
        """Import generals from CSV file"""
        imported_count = 0
        
        try:
            with open(filename, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    try:
                        # Convert CSV row back to GeneralData
                        general_data = {
                            'general_id': row['General_ID'],
                            'name': row['Name'],
                            'level': int(row['Level']),
                            'stars': StarRating(int(row['Stars'])),
                            'specialty': SpecialtyType(row['Specialty']),
                            'status': GeneralStatus(row['Status']),
                            'current_stats': GeneralStats(
                                attack=int(row['Attack']),
                                defense=int(row['Defense']),
                                leadership=int(row['Leadership']),
                                politics=int(row['Politics'])
                            ),
                            'extraction_confidence': float(row['Extraction_Confidence']),
                            'notes': row['Notes'],
                            'last_updated': datetime.fromisoformat(row['Last_Updated']) if row['Last_Updated'] else datetime.now()
                        }
                        
                        general = GeneralData(**general_data)
                        if self.add_general(general):
                            imported_count += 1
                            
                    except Exception as e:
                        self.logger.warning(f"Failed to import row: {str(e)}")
                        continue
                        
            self.logger.info(f"Imported {imported_count} generals from {filename}")
            return imported_count
            
        except Exception as e:
            self.logger.error(f"Failed to import from CSV: {str(e)}")
            return 0
            
    def save_to_json(self, filename: str) -> bool:
        """Save collection to JSON file"""
        try:
            collection_data = {
                'generals': {gid: general.to_dict() for gid, general in self.generals.items()},
                'metadata': {
                    'total_generals': len(self.generals),
                    'export_timestamp': datetime.now().isoformat(),
                    'statistics': self.get_statistics()
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(collection_data, f, indent=2, ensure_ascii=False)
                
            self.logger.info(f"Saved collection to {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save collection: {str(e)}")
            return False
            
    def load_from_json(self, filename: str) -> bool:
        """Load collection from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                collection_data = json.load(f)
                
            self.generals.clear()
            generals_data = collection_data.get('generals', {})
            
            for general_id, general_dict in generals_data.items():
                try:
                    general = GeneralData.from_dict(general_dict)
                    self.generals[general_id] = general
                except Exception as e:
                    self.logger.warning(f"Failed to load general {general_id}: {str(e)}")
                    
            self.logger.info(f"Loaded {len(self.generals)} generals from {filename}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load collection: {str(e)}")
            return False

# Example usage and testing
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Create test general data
    test_general = GeneralData(
        name="Alexander the Great",
        level=35,
        stars=StarRating.FIVE_STAR,
        specialty=SpecialtyType.ATTACK,
        current_stats=GeneralStats(attack=2500, defense=1800, leadership=2200, politics=1600),
        extraction_confidence=0.95,
        notes="Legendary attack general"
    )
    
    print("GeneralData module loaded successfully")
    print(f"Test general: {test_general.name}")
    print(f"Total power: {test_general.calculate_total_power()}")
    print(f"High quality: {test_general.is_high_quality()}")
    print(f"Specialty effectiveness: {test_general.get_specialty_effectiveness():.2f}")
    
    # Test collection
    collection = GeneralCollection()
    collection.add_general(test_general)
    stats = collection.get_statistics()
    print(f"Collection stats: {stats}")