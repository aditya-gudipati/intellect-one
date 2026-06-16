"""
Utility module for reading and extracting plain text from Microsoft Word (.docx) files
without using any external third-party dependencies.
"""

import os
import zipfile
import xml.etree.ElementTree as ET

def extract_text_from_docx(filepath: str) -> str:
    """
    Extracts text from a Microsoft Word (.docx) file.
    
    Args:
        filepath: The absolute or relative path to the .docx file.
        
    Returns:
        The extracted plain text with paragraphs separated by newlines.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid zip file or missing word/document.xml.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")

    if not zipfile.is_zipfile(filepath):
        raise ValueError(f"File '{filepath}' is not a valid zip archive (.docx)")

    with zipfile.ZipFile(filepath, 'r') as docx:
        if 'word/document.xml' not in docx.namelist():
            raise ValueError(f"File '{filepath}' is not a valid Word Document (missing word/document.xml)")
            
        xml_content = docx.read('word/document.xml')
        root = ET.fromstring(xml_content)
        
        paragraphs = []
        for elem in root.iter():
            tag = elem.tag
            # Match paragraph tags namespace-agnostically
            if tag.endswith('}p'):
                text_parts = []
                for child in elem.iter():
                    # Match text tags namespace-agnostically and append non-empty text
                    if child.tag.endswith('}t') and child.text:
                        text_parts.append(child.text)
                paragraphs.append("".join(text_parts))
                
        return "\n".join(paragraphs)
