import re
import json

def parse_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    documents = re.split(r'^#\s+', content, flags=re.MULTILINE)
    
    parsed_docs = []

    for doc in documents:
        if not doc.strip():
            continue
            
        doc_lines = doc.strip().split('\n')
        doc_title = doc_lines[0].strip()
        
        if 'CEVAP ANAHTARI' not in doc:
            continue
            
        parts = doc.split('CEVAP ANAHTARI')
        questions_part = parts[0]
        answers_part = parts[1]
        
        # Parse answers
        ans_sections = re.split(r'BÖLÜM\s+([A-Z])', answers_part)
        answers_dict = {}
        for i in range(1, len(ans_sections), 2):
            sec_letter = ans_sections[i]
            sec_content = ans_sections[i+1].strip()
            
            answers_dict[sec_letter] = {}
            if sec_letter == 'A':
                # S1 \n S2 \n ... \n B \n C \n
                lines = [line.strip() for line in sec_content.split('\n') if line.strip()]
                # find where answers start (first single letter A-E)
                q_ids = []
                ans_vals = []
                for line in lines:
                    if re.match(r'^S\d+$', line):
                        q_ids.append(line.replace('S', ''))
                    elif line in ['A', 'B', 'C', 'D', 'E']:
                        ans_vals.append(line)
                for q, a in zip(q_ids, ans_vals):
                    answers_dict[sec_letter][q] = a
            elif sec_letter == 'D':
                # 1-c | 2-d ...
                matches = re.findall(r'(\d+)\s*-\s*([a-z])', sec_content)
                for num, letter in matches:
                    answers_dict[sec_letter][num] = letter
            else:
                # 1. Answer \n 2. Answer
                matches = re.findall(r'^(\d+)\.\s+(.*?)$', sec_content, re.MULTILINE)
                for num, ans in matches:
                    answers_dict[sec_letter][num] = ans

        # Parse questions
        q_sections = re.split(r'BÖLÜM\s+([A-Z]):\s*(.*?)$', questions_part, flags=re.MULTILINE)
        
        doc_data = {
            "title": doc_title.replace('.docx', ''),
            "sections": []
        }
        
        for i in range(1, len(q_sections), 3):
            sec_letter = q_sections[i]
            sec_title = q_sections[i+1].strip()
            sec_content = q_sections[i+2].strip()
            
            section_data = {
                "letter": sec_letter,
                "title": sec_title,
                "questions": []
            }
            
            # Extract questions using 1. 2. 3.
            # Some questions might not start with numbers (like matching lists) but let's try
            q_splits = re.split(r'^(\d+)\.\s+', sec_content, flags=re.MULTILINE)
            
            # The first part is prologue (instructions)
            prologue = q_splits[0].strip()
            if prologue:
                section_data["instructions"] = prologue
                
            for j in range(1, len(q_splits), 2):
                q_num = q_splits[j]
                q_text = q_splits[j+1].strip()
                
                ans = answers_dict.get(sec_letter, {}).get(q_num, "Cevap bulunamadı.")
                
                section_data["questions"].append({
                    "number": q_num,
                    "text": q_text,
                    "answer": ans
                })
                
            doc_data["sections"].append(section_data)
            
        parsed_docs.append(doc_data)

    with open('qa_data.json', 'w', encoding='utf-8') as f:
        json.dump(parsed_docs, f, ensure_ascii=False, indent=4)
        
    print("Parsing complete. Generated qa_data.json")

if __name__ == "__main__":
    parse_markdown('extracted_texts.md')
