from typing import List
from PyPDF2 import PdfReader
from enum import Enum
import re

class Category(Enum):
    prohibuted='prohibited'
    mandatory='mandatory'
    conditional='conditional'
    optional='optional'
    uncategorized='uncategorized'


class Severity(Enum):
    prohibuted='critical'
    mandatory='high'
    conditional='medium'
    optional='low'
    uncategorized='info'


class DataCleanising:

    def __init__(self, file):
        self.file = file 
        self.content: str = ''

    def extract_content(self) -> None:
        reader = PdfReader(self.file)
        for page in reader.pages:
            self.content += page.extract_text() 

    def clean_text(self) -> str:
        self.extract_content()

        # self.content = re.sub(r'\n(?=[a-z])', ' ', self.content)       # fix the broken sentence caused by line breaks
        self.content = re.sub(r'(?<=[.!?])\s+|\n(?=\d+\.\d+)', ' ', self.content)
        self.content = re.sub(r'(\d+\.\d+)', r' \1 ', self.content)     # preserver space for sections
        self.content = re.sub(r'\n+', '\n', self.content)
        self.content = re.sub(r'\s+', ' ', self.content)

        return self.content
    
    def split_clause(self) -> List:
        self.clean_text()

        clauses = re.split(r'(?<=[.!?])\s+', self.content)
        return [c.strip() for c in clauses if len(c.strip()) > 20]
    
    def categorize_clause(self, clause: str) -> str:
        clause = clause.lower() 

        if ('strictly prohibited' in clause) or ('zero tolerance' in clause) or ('must not' in clause):
            return Category.prohibuted.value
        
        if ('must' in clause) or ('required' in clause) or ('shall' in clause) or ('expected to' in clause):
            return Category.mandatory.value
        
        if ('if' in clause) or ('when' in clause) or ('unless' in clause):
            return Category.conditional.value
        
        if ('may' in clause) or ('should' in clause) or ('goal' in clause):
            return Category.optional.value
        
        return Category.uncategorized.value
    
    def structured_policy(self, clauses: List) -> List:
        structured = []

        for index, clause in enumerate(clauses):
            clause_data = dict()
            clause_data['clause_id'] = f'clause-BP{index}'
            clause_data['content'] = f'{clause}'
            clause_data['category'] = f'{self.categorize_clause(clause)}'

            match clause_data['category']:
                case Category.prohibuted.value: 
                    clause_data['severity'] = Severity.prohibuted.value
                case Category.mandatory.value:
                    clause_data['severity'] = Severity.mandatory.value
                case Category.conditional.value:
                    clause_data['severity'] = Severity.conditional.value
                case Category.optional.value:
                    clause_data['severity'] = Severity.optional.value
                case _:
                    clause_data['severity'] = Severity.uncategorized.value

            structured.append(clause_data)

        return structured
    

# obj = DataCleanising('output_files/business-policy.pdf')
# clauses = obj.split_clause()
# for i in obj.structured_policy(clauses):
#     print(i, end='\n\n\n')
