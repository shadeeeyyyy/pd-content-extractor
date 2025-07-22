import fitz
import os
import sys

def extract_text_from_pdf(pdf_path, output_dir="output"):
    text_dir = os.path.join(output_dir, "text")
    os.makedirs(text_dir, exist_ok=True)
    
    doc = fitz.open(pdf_path)
    all_text = []
    
    print(f"Extracting text from {len(doc)} pages...")
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text()
        all_text.append(page_text)
        
        page_file = os.path.join(text_dir, f"page_{page_num + 1}_text.txt")
        with open(page_file, 'w', encoding='utf-8') as f:
            f.write(f"=== PAGE {page_num + 1} ===\n\n")
            f.write(page_text)
        
        print(f"  ✅ Page {page_num + 1}: {len(page_text)} characters")
    
    complete_file = os.path.join(text_dir, "complete_document_text.txt")
    with open(complete_file, 'w', encoding='utf-8') as f:
        f.write("=== COMPLETE DOCUMENT TEXT ===\n\n")
        for i, page_text in enumerate(all_text, 1):
            f.write(f"\n{'='*30} PAGE {i} {'='*30}\n\n")
            f.write(page_text)
    
    doc.close()
    
    print(f"\n✅ Text extraction complete!")
    print(f"📁 Text files saved to: {text_dir}")
    print(f"📄 Total files created: {len(all_text) + 1}")
    
    return text_dir

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_text_extract.py <pdf_path>")
        print("Example: python quick_text_extract.py sample_pdf/IMO_sample.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found: {pdf_path}")
        sys.exit(1)
    
    extract_text_from_pdf(pdf_path)