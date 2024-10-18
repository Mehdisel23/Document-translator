import tkinter as tk
from tkinter import filedialog
from googletrans import Translator
import PyPDF2
import pypdfium2
import os
import odf.text
import odf.teletype
from odf.opendocument import load
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit

def open_file():
    file_path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[
            ("All Supported Files", "*.txt;*.pdf;*.odt"),
            ("Text Files", "*.txt"),
            ("PDF Files", "*.pdf"),
            ("ODF Files", "*.odt"),
            ("All Files", "*.*")
        ]
    )
    
    if file_path:
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension == ".txt":
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        elif file_extension == ".pdf":
            content = extract_text_from_pdf(file_path)
        elif file_extension == ".odt":
            content = extract_text_from_odf(file_path)
        else:
            print("Unsupported file")
            return None, None
        
        return file_path, content
    return None, None

def extract_text_from_pdf(file_path):
    text = ''
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text()
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None

def extract_text_from_odf(file_path):
    try:
        textdoc = load(file_path)
        allparas = textdoc.getElementsByType(odf.text.P)
        text = ""
        for para in allparas:
            text += odf.teletype.extractText(para) + "\n"
        return text
    except Exception as e:
        print(f"Error reading ODF: {e}")
        return None

def translate_text(text, src_lang, dest_lang):
    if text is None:
        return None
    translator = Translator()
    try:
        translated = translator.translate(text, src=src_lang, dest=dest_lang)
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return None

def create_pdf(text, output_path):
    try:
        # Create a new PDF with letter size
        c = canvas.Canvas(output_path, pagesize=letter)
        width, height = letter
        
        # Set font and size
        c.setFont("Helvetica", 12)
        
        # Split text into lines that fit the page width
        margin = 72  # 1 inch margins
        text_width = width - 2 * margin
        text_height = height - 2 * margin
        
        # Split the text into lines
        lines = []
        for paragraph in text.split('\n'):
            lines.extend(simpleSplit(paragraph, "Helvetica", 12, text_width))
            lines.append('')  # Add space between paragraphs
        
        # Calculate lines per page
        line_height = 14
        lines_per_page = int(text_height / line_height)
        
        # Write text to PDF
        y = height - margin
        page_lines = 0
        
        for line in lines:
            if page_lines >= lines_per_page:
                c.showPage()
                c.setFont("Helvetica", 12)
                y = height - margin
                page_lines = 0
            
            if line:
                c.drawString(margin, y, line)
            y -= line_height
            page_lines += 1
        
        # Save the PDF
        c.save()
        return True
    except Exception as e:
        print(f"Error creating PDF: {e}")
        return False

def save_translated_file(file_path, translated_text, target_lang):
    if translated_text is None:
        print("No text to save")
        return None
    try:
        base, ext = os.path.splitext(file_path)
        new_file_path = f"{base}_translated_{target_lang}.pdf"
        if create_pdf(translated_text, new_file_path):
            return new_file_path
        return None
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def translate_file():
    # Get file and its content
    file_path, content = open_file()
    if not file_path:
        print("No file selected.")
        return
    
    # Get the source and target language from user input
    src_lang = input("Enter source language (e.g., 'en' for English): ").strip()
    target_lang = input("Enter target language (e.g., 'fr' for French): ").strip()
    
    translated_content = translate_text(content, src_lang, target_lang)
    
    if translated_content:
        # Save the translated text
        new_file_path = save_translated_file(file_path, translated_content, target_lang)
        if new_file_path:
            print(f"File translated and saved as: {new_file_path}")

root = tk.Tk()
root.withdraw()  # Hide the root window

# Run the file translation
translate_file()