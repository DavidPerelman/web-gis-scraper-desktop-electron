import pdfplumber
import pandas as pd
import numpy as np
import re
from collections import defaultdict
import warnings
import camelot
import io
import os
from PIL import Image
import pytesseract
warnings.filterwarnings('ignore')

class HebrewPDFTableExtractor:
    """
    מחלץ טבלאות מקבצי PDF בעברית בגישה אדפטיבית
    המחלקה מיישמת מספר שיטות חילוץ שונות ומנסה למצוא את השיטה הטובה ביותר לכל טבלה
    """
    
    def __init__(self, pdf_path, lang='heb'):
        """
        אתחול המחלקה
        
        Args:
            pdf_path: נתיב לקובץ ה-PDF
            lang: שפת הטקסט ל-OCR (ברירת מחדל: עברית)
        """
        self.pdf_path = pdf_path
        self.lang = lang
        # לטעינת הקובץ עם pdfplumber
        self.pdf = pdfplumber.open(pdf_path)
        self.extracted_tables = []
        self.detected_patterns = []
    
    def extract_all_tables(self, page_numbers=None, methods=None):
        """
        מחלץ את כל הטבלאות מהקובץ באמצעות שיטות שונות
        
        Args:
            page_numbers: רשימת מספרי עמודים (אם לא צוין, כל העמודים)
            methods: רשימת שיטות חילוץ לניסיון (אם לא צוין, כל השיטות)
            
        Returns:
            רשימה של DataFrames, כל אחד מייצג טבלה מחולצת
        """
        if methods is None:
            methods = ['camelot_lattice', 'camelot_stream', 'pdfplumber', 'regex_pattern']
        
        if page_numbers is None:
            page_numbers = list(range(len(self.pdf.pages)))
            
        tables = []
        
        # ניסיון לחלץ טבלאות בכל העמודים
        for page_num in page_numbers:
            print(f"מחלץ טבלאות מעמוד {page_num+1}...")
            
            page_tables = []
            
            # ניסיון כל שיטות החילוץ
            for method in methods:
                try:
                    method_tables = getattr(self, f"_extract_with_{method}")(page_num)
                    if method_tables:
                        page_tables.extend([(table, method) for table in method_tables])
                        print(f"  נמצאו {len(method_tables)} טבלאות באמצעות {method}")
                except Exception as e:
                    print(f"  שגיאה בשיטת {method}: {str(e)}")
            
            # בחירת הטבלאות הטובות ביותר
            if page_tables:
                best_tables = self._select_best_tables(page_tables)
                tables.extend(best_tables)
                
        self.extracted_tables = tables
        return tables
    
    def _extract_with_camelot_lattice(self, page_num):
        """חילוץ טבלאות באמצעות camelot עם שיטת lattice"""
        try:
            tables = camelot.read_pdf(self.pdf_path, pages=str(page_num+1), flavor='lattice')
            return [table.df for table in tables if table.df.size > 0]
        except Exception as e:
            print(f"  שגיאה ב-camelot lattice: {str(e)}")
            return []
    
    def _extract_with_camelot_stream(self, page_num):
        """חילוץ טבלאות באמצעות camelot עם שיטת stream"""
        try:
            tables = camelot.read_pdf(self.pdf_path, pages=str(page_num+1), flavor='stream')
            return [table.df for table in tables if table.df.size > 0]
        except Exception as e:
            print(f"  שגיאה ב-camelot stream: {str(e)}")
            return []
    
    def _extract_with_pdfplumber(self, page_num):
        """חילוץ טבלאות באמצעות pdfplumber"""
        try:
            page = self.pdf.pages[page_num]
            tables = page.extract_tables()
            if not tables:
                return []
                
            dfs = []
            for table in tables:
                # סינון שורות ריקות
                filtered_table = [[cell or '' for cell in row] for row in table if any(cell for cell in row)]
                if filtered_table:
                    # הנחה שהשורה הראשונה היא כותרות
                    headers = filtered_table[0]
                    data = filtered_table[1:]
                    df = pd.DataFrame(data, columns=headers)
                    dfs.append(df)
            return dfs
        except Exception as e:
            print(f"  שגיאה ב-pdfplumber: {str(e)}")
            return []
    
    def _extract_with_regex_pattern(self, page_num):
        """חילוץ טבלאות באמצעות זיהוי תבניות"""
        try:
            page = self.pdf.pages[page_num]
            text = page.extract_text()
            lines = text.split('\n')
            
            # זיהוי תבניות נפוצות של טבלאות בעברית
            patterns = [
                # תבנית 1: זיהוי טבלת מידע הכוללת "יעוד", "שימוש", וכו'
                {
                    'header_pattern': r"יעוד.*שימוש.*(?:תאי שטח|בניין).*גודל מגרש",
                    'row_pattern': r"(\S+(?:\s+\S+)*)\s+(\S+(?:\s+\(\S+\))?)\s+(\d+)\s+(.*?)\s+(\d+(?:[\.,]\d+)?)",
                    'num_columns': 5,
                    'column_names': ["יעוד", "שימוש", "תאי שטח", "בניין / מקום", "גודל מגרש"]
                },
                # תבנית 2: זיהוי טבלת מספרים כללית עם כותרות כלשהן
                {
                    'header_pattern': r"^\s*(\S+(?:\s+\S+)?)\s+(\S+(?:\s+\S+)?)\s+(\S+(?:\s+\S+)?)",
                    'row_pattern': r"^\s*(\S+(?:\s+\S+)?)\s+(\d+(?:[\.,]\d+)?)\s+(\d+(?:[\.,]\d+)?)",
                    'num_columns': 3
                }
            ]
            
            dfs = []
            
            for pattern in patterns:
                # חיפוש התבנית בטקסט
                header_idx = None
                for i, line in enumerate(lines):
                    if re.search(pattern['header_pattern'], line):
                        header_idx = i
                        # שמירת הכותרות שנמצאו
                        self.detected_patterns.append({
                            'page': page_num,
                            'pattern_type': 'header',
                            'text': line,
                            'line_number': i
                        })
                        break
                
                if header_idx is None:
                    continue
                    
                # הנחה שהשורה אחרי הכותרת היא תת-כותרת אם קיימת
                header_lines = [lines[header_idx]]
                if header_idx + 1 < len(lines) and not re.match(r"^\d", lines[header_idx + 1].strip()):
                    header_lines.append(lines[header_idx + 1])
                    data_start = header_idx + 2
                else:
                    data_start = header_idx + 1
                
                # חילוץ שורות הנתונים
                data_rows = []
                for i in range(data_start, len(lines)):
                    line = lines[i].strip()
                    if not line:
                        continue
                    
                    # חיפוש תבנית בשורה
                    match = re.search(pattern['row_pattern'], line)
                    if match:
                        # שמירת השורה שנמצאה
                        self.detected_patterns.append({
                            'page': page_num,
                            'pattern_type': 'data_row',
                            'text': line,
                            'line_number': i,
                            'values': match.groups()
                        })
                        
                        values = list(match.groups())
                        data_rows.append(values)
                
                if data_rows:
                    # מציאת שמות עמודות על פי המידע שנמצא
                    if 'column_names' in pattern:
                        column_names = pattern['column_names']
                    else:
                        # אם אין שמות עמודות מוגדרים, נשתמש בכותרות שנמצאו
                        header_text = ' '.join(header_lines)
                        words = re.findall(r'\S+(?:\s+\S+){0,2}', header_text)
                        column_names = words[:pattern['num_columns']]
                        
                        # אם עדיין אין מספיק שמות עמודות, נוסיף עמודות גנריות
                        while len(column_names) < pattern['num_columns']:
                            column_names.append(f"עמודה_{len(column_names)+1}")
                    
                    # מילוי וליישור מספר העמודות
                    for i, row in enumerate(data_rows):
                        while len(row) < len(column_names):
                            row.append('')
                        data_rows[i] = row[:len(column_names)]
                    
                    # יצירת DataFrame
                    df = pd.DataFrame(data_rows, columns=column_names)
                    self._clean_dataframe(df)
                    dfs.append(df)
            
            return dfs
        except Exception as e:
            print(f"  שגיאה בזיהוי תבניות: {str(e)}")
            return []
    
    def _select_best_tables(self, tables_with_methods):
        """
        בחירת הטבלאות הטובות ביותר מבין כל השיטות
        
        Args:
            tables_with_methods: רשימה של זוגות (DataFrame, שיטת_חילוץ)
            
        Returns:
            רשימה של DataFrames מסוננים
        """
        # איתור טבלאות עם איכות גבוהה
        best_tables = []
        
        # מיון הטבלאות לפי מספר העמודות והשורות
        sorted_tables = sorted(tables_with_methods, 
                              key=lambda x: (x[0].shape[1], x[0].shape[0], 
                                            self._score_table_quality(x[0])), 
                              reverse=True)
        
        # סף מינימלי לגודל הטבלה
        min_size = 4  # טבלה צריכה להכיל לפחות 4 תאים
        
        for df, method in sorted_tables:
            # נבדוק שהטבלה גדולה מספיק ומכילה מידע משמעותי
            if df.size < min_size:
                continue
                
            # נוודא שהטבלה מכילה מידע משמעותי (לא רק תאים ריקים)
            non_empty_cells = df.count().sum()
            if non_empty_cells < min_size:
                continue
            
            # ניקוי וטיוב הטבלה
            cleaned_df = self._clean_dataframe(df.copy())
            
            # אם כבר יש טבלה דומה, נדלג
            if any(self._is_similar_table(cleaned_df, existing) for existing in best_tables):
                continue
                
            best_tables.append(cleaned_df)
        
        return best_tables
    
    def _score_table_quality(self, df):
        """הערכת איכות הטבלה"""
        # בדיקת רמת המידע בטבלה (הערכת עמודות מספריות)
        numeric_ratio = sum(pd.to_numeric(df[col], errors='coerce').notna().sum() 
                          for col in df.columns) / (df.size or 1)
        
        # איזון בין מספר העמודות למספר השורות
        shape_balance = min(df.shape[0], df.shape[1]) / (max(df.shape[0], df.shape[1]) or 1)
        
        # לא מעדיפים טבלאות עם יותר מדי עמודות ביחס לשורות
        if df.shape[1] > 20 and shape_balance < 0.1:
            return 0
            
        return numeric_ratio * 0.7 + shape_balance * 0.3
    
    def _is_similar_table(self, df1, df2, threshold=0.8):
        """בדיקה האם שתי טבלאות דומות"""
        # אם מספר השורות או העמודות שונה מאוד, הטבלאות שונות
        if abs(df1.shape[0] - df2.shape[0]) / max(df1.shape[0], df2.shape[0]) > 0.5:
            return False
        if abs(df1.shape[1] - df2.shape[1]) / max(df1.shape[1], df2.shape[1]) > 0.5:
            return False
            
        # בדיקת חפיפה בשמות העמודות
        common_cols = set(df1.columns) & set(df2.columns)
        if len(common_cols) / max(len(df1.columns), len(df2.columns)) > threshold:
            return True
            
        return False
        
    def _clean_dataframe(self, df):
        """
        ניקוי וטיוב של DataFrame
        
        Args:
            df: DataFrame לניקוי
            
        Returns:
            DataFrame מנוקה
        """
        if df.empty:
            return df
            
        # הסרת עמודות ריקות
        df = df.dropna(axis=1, how='all')
        
        # הסרת כותרות כפולות או ריקות
        df.columns = [str(col).strip() for col in df.columns]
        df.columns = [col if col else f"עמודה_{i+1}" for i, col in enumerate(df.columns)]
        
        # המרת ערכים מספריים
        for col in df.columns:
            # זיהוי עמודות שכנראה מכילות מספרים
            if df[col].dtype == object:  # רק עבור עמודות טקסט
                numeric_count = sum(1 for val in df[col] if isinstance(val, str) and 
                                  re.match(r'^[\d\.,]+

# דוגמה לשימוש:
# נתיב לקובץ PDF
file_path = 'ab2cccab-9b5f-46a2-a0ec-55d8b40f499c.pdf'

# חילוץ הטבלה
df_table = extract_table_from_hebrew_pdf(file_path)

# הצגת התוצאות
print(df_table.head())

# שמירה לקובץ Excel
df_table.to_excel("hebrew_table_extracted.xlsx", index=False)

# להצגה מותאמת עבור נתונים בעברית ב-Jupyter Notebook
def display_hebrew_dataframe(df):
    """מציג DataFrame בעברית בצורה מותאמת RTL ב-Jupyter Notebook"""
    from IPython.display import display, HTML
    
    # יצירת סגנון RTL
    rtl_style = """
    <style>
        table {direction: rtl;}
        th, td {text-align: right !important;}
    </style>
    """
    
    # המרת ה-DataFrame ל-HTML עם סגנון RTL
    html = rtl_style + df.to_html(index=False)
    
    # הצגת ה-HTML
    display(HTML(html))

# אם אתה עובד ב-Jupyter Notebook, אתה יכול להשתמש ב:
# display_hebrew_dataframe(df_table)
, val.strip()))
                
                numeric_ratio = numeric_count / (df[col].count() or 1)
                
                if numeric_ratio > 0.7:  # אם מעל 70% מהערכים נראים כמו מספרים
                    df[col] = df[col].apply(lambda x: 
                        pd.to_numeric(str(x).replace(',', ''), errors='coerce') 
                        if x and str(x).strip() else np.nan)
        
        # טיפול בערכים חסרים
        df = df.replace('', np.nan)
        
        # זיהוי וטיפול בכותרות היררכיות
        df = self._handle_hierarchical_headers(df)
        
        return df
    
    def _handle_hierarchical_headers(self, df):
        """
        זיהוי וטיפול בכותרות היררכיות
        
        Args:
            df: DataFrame עם כותרות פוטנציאליות היררכיות
            
        Returns:
            DataFrame עם כותרות מאוחדות היררכיות אם רלוונטי
        """
        # אם יש פחות מ-2 שורות, אין אפשרות לכותרות היררכיות
        if df.shape[0] < 2:
            return df
            
        # בדיקה האם השורה הראשונה או השנייה עשויה להיות המשך של הכותרות
        first_row = df.iloc[0]
        
        # בדיקה האם השורה הראשונה נראית כמו כותרת משנית
        header_pattern = False
        non_empty_count = sum(1 for val in first_row if pd.notna(val) and str(val).strip())
        
        # האם רוב התאים בשורה הראשונה אינם מספרים?
        non_numeric_ratio = sum(1 for val in first_row if pd.notna(val) and not re.match(r'^[\d\.,]+

# דוגמה לשימוש:
# נתיב לקובץ PDF
file_path = 'ab2cccab-9b5f-46a2-a0ec-55d8b40f499c.pdf'

# חילוץ הטבלה
df_table = extract_table_from_hebrew_pdf(file_path)

# הצגת התוצאות
print(df_table.head())

# שמירה לקובץ Excel
df_table.to_excel("hebrew_table_extracted.xlsx", index=False)

# להצגה מותאמת עבור נתונים בעברית ב-Jupyter Notebook
def display_hebrew_dataframe(df):
    """מציג DataFrame בעברית בצורה מותאמת RTL ב-Jupyter Notebook"""
    from IPython.display import display, HTML
    
    # יצירת סגנון RTL
    rtl_style = """
    <style>
        table {direction: rtl;}
        th, td {text-align: right !important;}
    </style>
    """
    
    # המרת ה-DataFrame ל-HTML עם סגנון RTL
    html = rtl_style + df.to_html(index=False)
    
    # הצגת ה-HTML
    display(HTML(html))

# אם אתה עובד ב-Jupyter Notebook, אתה יכול להשתמש ב:
# display_hebrew_dataframe(df_table)
, str(val).strip())) / (non_empty_count or 1)
        
        if non_numeric_ratio > 0.7 and non_empty_count > df.shape[1] * 0.3:
            header_pattern = True
        
        if header_pattern:
            # יצירת כותרות מורכבות
            current_headers = list(df.columns)
            subheaders = [str(val) if pd.notna(val) else '' for val in first_row]
            
            # יצירת תוויות עמודה חדשות על ידי שילוב הכותרות הקיימות והמשניות
            new_headers = []
            for i, (main, sub) in enumerate(zip(current_headers, subheaders)):
                if sub and sub.strip():
                    new_headers.append(f"{main} - {sub}")
                else:
                    new_headers.append(main)
            
            # עדכון הכותרות והסרת השורה שהייתה כותרת משנית
            df.columns = new_headers
            df = df.iloc[1:].reset_index(drop=True)
        
        return df

    def extract_from_text(self, text):
        """
        חילוץ טבלאות מתוך טקסט גולמי
        
        Args:
            text: טקסט גולמי שעשוי להכיל טבלאות
            
        Returns:
            רשימה של DataFrames שחולצו
        """
        lines = text.split('\n')
        
        # יצירת רשימת דפוסים לחיפוש
        patterns = [
            # דפוס 1: שורות שמכילות מספר עמודות קבוע של מספרים או טקסט
            {
                'name': 'fixed_columns',
                'pattern': r'^([\u0590-\u05FF\s]+)\s+(\d+[\.,]?\d*)\s+(\d+[\.,]?\d*)\s+(\d+[\.,]?\d*)',
                'min_matches': 3  # מינימום מספר שורות שצריכות להתאים
            },
            # דפוס 2: שורות שמתחילות במספר (כמו מספור שורות) ואחריהן נתונים
            {
                'name': 'numbered_rows',
                'pattern': r'^(\d+)\.\s+([\u0590-\u05FF\s]+)\s+(\d+[\.,]?\d*)',
                'min_matches': 3
            }
        ]
        
        tables = []
        
        for pattern_def in patterns:
            matches = []
            for line in lines:
                match = re.search(pattern_def['pattern'], line)
                if match:
                    matches.append(match.groups())
            
            if len(matches) >= pattern_def['min_matches']:
                # יצירת DataFrame מהנתונים שנמצאו
                df = pd.DataFrame(matches)
                
                # ניקוי הטבלה
                df = self._clean_dataframe(df)
                tables.append(df)
        
        return tables
    
    def extract_from_specific_pattern(self, pattern, column_names=None):
        """
        חילוץ טבלאות על פי תבנית ספציפית
        
        Args:
            pattern: ביטוי רגולרי לחיפוש בשורות הטקסט
            column_names: רשימת שמות עמודות לטבלה (אופציונלי)
            
        Returns:
            DataFrame שחולץ
        """
        text = ""
        for page in self.pdf.pages:
            text += page.extract_text() + "\n"
        
        lines = text.split('\n')
        matches = []
        
        for line in lines:
            match = re.search(pattern, line)
            if match:
                matches.append(match.groups())
        
        if matches:
            df = pd.DataFrame(matches, columns=column_names)
            return self._clean_dataframe(df)
        
        return None
    
    def __del__(self):
        """סגירת משאבים בסיום"""
        if hasattr(self, 'pdf') and self.pdf:
            self.pdf.close()
    
def extract_tables_from_hebrew_pdf(pdf_path, page_numbers=None, methods=None):
    """
    פונקציית עזר נוחה לחילוץ טבלאות מקובץ PDF בעברית
    
    Args:
        pdf_path: נתיב לקובץ ה-PDF
        page_numbers: רשימת מספרי עמודים (אם לא צוין, כל העמודים)
        methods: רשימת שיטות חילוץ לניסיון (אם לא צוין, כל השיטות)
        
    Returns:
        רשימה של DataFrames, כל אחד מייצג טבלה מחולצת
    """
    extractor = HebrewPDFTableExtractor(pdf_path)
    return extractor.

# דוגמה לשימוש:
# נתיב לקובץ PDF
file_path = 'ab2cccab-9b5f-46a2-a0ec-55d8b40f499c.pdf'

# חילוץ הטבלה
df_table = extract_table_from_hebrew_pdf(file_path)

# הצגת התוצאות
print(df_table.head())

# שמירה לקובץ Excel
df_table.to_excel("hebrew_table_extracted.xlsx", index=False)

# להצגה מותאמת עבור נתונים בעברית ב-Jupyter Notebook
def display_hebrew_dataframe(df):
    """מציג DataFrame בעברית בצורה מותאמת RTL ב-Jupyter Notebook"""
    from IPython.display import display, HTML
    
    # יצירת סגנון RTL
    rtl_style = """
    <style>
        table {direction: rtl;}
        th, td {text-align: right !important;}
    </style>
    """
    
    # המרת ה-DataFrame ל-HTML עם סגנון RTL
    html = rtl_style + df.to_html(index=False)
    
    # הצגת ה-HTML
    display(HTML(html))

# אם אתה עובד ב-Jupyter Notebook, אתה יכול להשתמש ב:
# display_hebrew_dataframe(df_table)
