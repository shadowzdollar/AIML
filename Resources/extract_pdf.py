from pypdf import PdfReader

reader = PdfReader('Python-for-Data-Analysis.pdf')
print(f'Total pages: {len(reader.pages)}')

# Extract text from all pages
full_text = ''
for i, page in enumerate(reader.pages):
    text = page.extract_text()
    if text:
        full_text += f'\n--- PAGE {i+1} ---\n{text}'

# Save to file for analysis
with open('pdf_text.txt', 'w', encoding='utf-8') as f:
    f.write(full_text)

print('Text extracted and saved to pdf_text.txt')