import zipfile
import xml.etree.ElementTree as ET
import os
import glob

def extract_text_from_docx(docx_path):
    try:
        doc = zipfile.ZipFile(docx_path)
        xml_content = doc.read('word/document.xml')
        doc.close()
        tree = ET.XML(xml_content)
        
        namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        paragraphs = []
        for paragraph in tree.findall('.//w:p', namespace):
            texts = [node.text for node in paragraph.findall('.//w:t', namespace) if node.text]
            if texts:
                paragraphs.append(''.join(texts))
            else:
                paragraphs.append('') # empty line
                
        return '\n'.join(paragraphs)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    files = glob.glob('*.docx')
    with open('extracted_texts.md', 'w', encoding='utf-8') as f:
        for file in files:
            f.write(f'# {file}\n')
            f.write(extract_text_from_docx(file))
            f.write('\n\n')
    print("Extraction complete.")
