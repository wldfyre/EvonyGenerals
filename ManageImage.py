#class to contain all the methods to manage images
import imagehash
from collections import namedtuple
from PIL import Image
import cv2
import numpy as np
import matplotlib.pyplot as plt # for plotting
import pytesseract #pytesseract library for OCR
import xml.etree.ElementTree as ET # for parsing XML files
import os

class ManageImage:
    def __init__(self):
        pass

    def GetXMLData(self, strLocation, screenshot):
        # This method should read the locations.xml file and return the coordinates for the given area name
        # For example, if strAreaName is "MainGeneralBox", it should return the coordinates for that area
        # You can use the xml.etree.ElementTree module to parse the XML file
        # get screenshot dimensions
        if screenshot is None:
            print("Error: Screenshot is empty or could not be read")
            # display error message to user indicating screenshot could not be read
            return False,0,0,0,0,"False"
        
        intHeight, intWidth, _ = screenshot.shape
        # Parse the XML file to find the location
        if __debug__:
            print(f"GetXMLData called for {strLocation}, where height={intHeight} and width={intWidth}")
        
        config_dir = os.path.dirname(os.path.abspath(__file__))
        xml_file = os.path.join(config_dir, "Resources", "locations.xml")
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for location in root.findall('preset'):
            name = location.get('name')
            if name == strLocation:
                x1 = int(float(location.get('xLoc')) * intWidth) 
                y1 = int(float(location.get('yLoc')) * intHeight)
                x2 = int(float(location.get('xDest')) * intWidth) 
                y2 = int(float(location.get('yDest')) * intHeight)
                
                click_and_drag = location.get('ClickAndDrag')
                
                if __debug__:
                    print(f"Coordinates for {strLocation}: ({x1}, {y1}), ({x2}, {y2}), ClickAndDrag: {click_and_drag}")

                return (True, x1, y1, x2, y2, click_and_drag) 
        # If the xml name is not found, return False       
        return (False, 0, 0, 0, 0, "False")

    def GetMainGeneral(self, screenshot):
        # Placeholder for method to get Main General Name
        # This method should return the name of the main general
        # by using OCR to search the screenshot for the phrase "Main General" first,
        # then reading the name below it (which may be more than one word)
        # first, call GetScreenshot() to capture the march preset screen
        # then use pytesseract to read the text for the Main General
        strXMLItem = "MainGeneralBox"

        tupXMLData = self.GetXMLData(self, "MainGeneralBox", screenshot)
        (boolFound, x1, y1, x2, y2, _) = tupXMLData
        if boolFound:
            # crop the screenshot to the area of interest
            cropped_image = screenshot[y1:y2, x1:x2]
            # save the cropped image for debugging
            if __debug__:
                config_dir = os.path.dirname(os.path.abspath(__file__))
                if not os.path.exists(os.path.join(config_dir, "Temp")):
                    os.makedirs(os.path.join(config_dir, "Temp"))
                # save the cropped image to a file
                cropped_image_filename = os.path.join(config_dir, "Temp", "cropped_main_general.png")
                cv2.imwrite(cropped_image_filename, cropped_image)
            
            # use pytesseract to read the text from the cropped image
            main_general_name = pytesseract.image_to_string(cropped_image)
            
            if __debug__:
                print(f"Main General Name: {main_general_name}")
            
            return main_general_name.strip()
        
        

    def GetAssistantGeneral(self, screenshot):
        # Placeholder for method to get Assistant General Name
        # This method should return the name of the assistant general, if one is set
        pass

    def GetMilitaryTactics(self, screenshot):
        # Placeholder for method to get Military Tactics Name
        # This method should return the name of the military tactics, if one is set
        pass

    def GetSubCityCheckmark(self, screenshot):
        # Placeholder for method to determine if a sub city is checked
        # This method should return True if a sub city is set, False otherwise
        pass

    def GetTroopInfo(self, screenshot):
        troop_list = []
        # 1. scroll screen until verified we are at the top of the screen, using ImageHash
        #    and CompareImage to compare the current screenshot with the previous one
        # 2. open the google sheets file containing troop names
        # 3. get the troop box size from the XML file

        # 4. get the screen snippet for the troops
        # 5. use pytesseract to read the troop level, name, and counts
        # 6. using the troop level and name, search the google sheets file for the troop type
        # 7. add the troop level, type, and count to the troop_list
        # 8. scroll down the screen to the next troop box
        # 9. verify screen has changed using ImageHash and CompareImage. 
        #    If not, break the loop and pull the remaining troops from the current screen
        # 9. else repeat steps 4-8 until all troops are read
        
        return troop_list
    
    # method to compare two images using imagehash
    def CompareImage(self, img1_path, img2_path):
        try:
            hash1 = imagehash.average_hash(Image.open(img1_path))
            hash2 = imagehash.average_hash(Image.open(img2_path))
            # Calculate the difference between the hashes
            difference = hash1 - hash2
            # Define a threshold for similarity (you can adjust this value)
            threshold = 5
            if difference < threshold:
                return True  # Images are similar
            else:
                return False  # Images are different
        except Exception as e:
            print(f"Error comparing images: {e}")
            return False

    def FindImageTemplate(self, templateName, screenshot, threshold=0.8):
        """Find a template image in the screenshot using CV2 template matching"""
        if __debug__:
            print(f"FindImageTemplate: Looking for '{templateName}' template")
        
        # Load template image from Resources folder
        config_dir = os.path.dirname(os.path.abspath(__file__))
        template_path = os.path.join(config_dir, "Resources", f"{templateName}.png")
        
        if not os.path.exists(template_path):
            if __debug__:
                print(f"Template image not found: {template_path}")
            return None
            
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            if __debug__:
                print(f"Failed to load template image: {template_path}")
            return None
            
        # Convert both images to grayscale for better template matching
        screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # Perform template matching
        result = cv2.matchTemplate(screenshot_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        
        # Get the best match location
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if __debug__:
            print(f"Template matching confidence: {max_val}")
        
        # Check if match confidence is above threshold
        if max_val >= threshold:
            # Get template dimensions
            template_height, template_width = template_gray.shape
            
            # Calculate center of matched region
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2
            
            if __debug__:
                print(f"Template '{templateName}' found at center: ({center_x}, {center_y})")
                
            return (center_x, center_y)
        else:
            if __debug__:
                print(f"Template '{templateName}' not found (confidence {max_val} < {threshold})")
            return None

    # Check if the passed text is in the screen snippet
    def TextOnScreen(self, strText, objSnippet):
        if __debug__:
            print(f"TextOnScreen: '{strText}' called")

        # Convert to RGB for pytesseract
        img_rgb = cv2.cvtColor(objSnippet, cv2.COLOR_BGR2RGB)

        # Use pytesseract to get bounding boxes for all detected words
        data = pytesseract.image_to_data(img_rgb, output_type=pytesseract.Output.DICT, config='--psm 11')

        for i, word in enumerate(data['text']):
            if word.strip().lower() == strText.strip().lower():
                x = data['left'][i]
                y = data['top'][i]
                w = data['width'][i]
                h = data['height'][i]
                center_x = x + w // 2
                center_y = y + h // 2
                return (center_x, center_y)

        print(f"Text '{strText}' not found on screen.")
        return None

    # Enhanced OCR method for generals management
    def ExtractGeneralsData(self, screenshot, region_name):
        """Extract general information using OCR from a specific screen region"""
        tupXMLData = self.GetXMLData(region_name, screenshot)
        (boolFound, x1, y1, x2, y2, _) = tupXMLData
        
        if boolFound:
            # Crop to region of interest
            cropped_image = screenshot[y1:y2, x1:x2]
            
            # Apply image preprocessing for better OCR
            gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
            # Apply adaptive thresholding
            processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            
            # Use pytesseract to extract text with specific configuration
            custom_config = r'--oem 3 --psm 6'
            extracted_text = pytesseract.image_to_string(processed, config=custom_config)
            
            if __debug__:
                config_dir = os.path.dirname(os.path.abspath(__file__))
                if not os.path.exists(os.path.join(config_dir, "Temp")):
                    os.makedirs(os.path.join(config_dir, "Temp"))
                debug_filename = os.path.join(config_dir, "Temp", f"extracted_{region_name}.png")
                cv2.imwrite(debug_filename, processed)
                print(f"Extracted text from {region_name}: {extracted_text}")
            
            return extracted_text.strip()
        
        return None

    def FindMultipleTemplates(self, templateNames, screenshot, threshold=0.8):
        """Find multiple template images in the screenshot"""
        found_templates = []
        
        for templateName in templateNames:
            coords = self.FindImageTemplate(templateName, screenshot, threshold)
            if coords:
                found_templates.append({
                    'name': templateName,
                    'coordinates': coords
                })
        
        return found_templates