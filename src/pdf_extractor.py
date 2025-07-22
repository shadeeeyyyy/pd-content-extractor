import fitz
import json
import os
from PIL import Image
import re

class PDFExtractor:
    def __init__(self, pdf_path, output_dir="output"):
        self.pdf_path = pdf_path
        self.output_dir = output_dir
        self.images_dir = os.path.join(self.output_dir, "extracted_images")
        self.text_dir = os.path.join(self.output_dir, "extracted_text")   
        self.doc = None 

    def setup_directories(self):
        # Create necessary output directories
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.text_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)

    def extract_text_from_page(self, page):
        #Extract raw text from a PDF page.
        return page.get_text()

    def extract_images_from_page(self, page, page_num):
        # Extract all images from a PDF page.Images are saved to self.images_dir
        image_list = page.get_images()
        extracted_images_paths = []
        for img_index, img in enumerate(image_list):
            xref = img[0]
            try:
                pix = fitz.Pixmap(self.doc, xref)
                if pix.n - pix.alpha < 4:
                    img_filename = f"page_{page_num+1}_image_{img_index+1}.png"
                    img_path = os.path.join(self.images_dir, img_filename)
                    pix.save(img_path)
                    extracted_images_paths.append(img_path)
                else:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
                    img_filename = f"page_{page_num+1}_image_{img_index+1}.png"
                    img_path = os.path.join(self.images_dir, img_filename)
                    pix.save(img_path)
                    extracted_images_paths.append(img_path)
            except Exception as e:
                print(f"Warning: Could not extract image {img_index} on page {page_num+1}: {e}")
            finally:
                if 'pix' in locals() and pix is not None:
                    pix = None 
        return extracted_images_paths

    def identify_question_blocks(self, page_text, page_images):
        # Identify question blocks based on patterns in the text.
        question_pattern = r'(\d+)\.\s*(.+?)(?=\n*\d+\.\s*|\Z)'

        questions = re.findall(question_pattern, page_text, re.DOTALL)

        question_blocks = []
        for i, (q_num, q_text) in enumerate(questions):
            block = {
                "question_number": int(q_num),
                "question_text": q_text.strip(),
                "images": [], 
                "options": []  
            }
            question_blocks.append(block)
        return question_blocks

    def organize_by_sections(self, content):
        sections = {
            "LOGICAL_REASONING": [],
            "MATHEMATICS": [],
            "ACHIEVER_SECTION": [],
            "UNSORTED": [] 
        }

        current_section = "UNSORTED"
        section_ranges = {
            "LOGICAL_REASONING": (1, 15),
            "MATHEMATICS": (16, 30),
            "ACHIEVER_SECTION": (31, 35)
        }

        for key in sections:
            sections[key] = []

        for item in content:
            q_num = item.get("question_number")
            if q_num is None:
                sections["UNSORTED"].append(item)
                continue

            found_section = False
            for section_name, (start, end) in section_ranges.items():
                if start <= q_num <= end:
                    sections[section_name].append(item)
                    found_section = True
                    break
            if not found_section:
                sections["UNSORTED"].append(item)

        return sections

    def extract_options(self, question_text):
        option_pattern = r'\[([A-D])\]\s*([^[]*?)(?=\s*\[[A-D]\]|\Z)'
        options = re.findall(option_pattern, question_text, re.DOTALL)

        formatted_options = []
        for option_letter, option_text in options:
            formatted_options.append({
                "letter": option_letter.strip(),
                "text": option_text.strip()
            })
        return formatted_options

    def associate_images_with_questions(self, questions, page_images):
        if not questions:
            return [] 
        updated_questions = [q.copy() for q in questions] 

        if page_images:
            images_per_question = len(page_images) / len(updated_questions) 

            for i, question in enumerate(updated_questions):
                start_img_idx = int(round(i * images_per_question))
                end_img_idx = int(round((i + 1) * images_per_question))
                start_img_idx = max(0, min(start_img_idx, len(page_images)))
                end_img_idx = max(0, min(end_img_idx, len(page_images)))

                question["images"] = page_images[start_img_idx:end_img_idx]
        else:
            for question in updated_questions:
                question["images"] = [] 
        for question in updated_questions:
            question["options"] = self.extract_options(question["question_text"])

        return updated_questions

    def extract_all_content(self):
        """Main method to extract all content from PDF."""
        try:
            self.doc = fitz.open(self.pdf_path)
        except fitz.FileDataError as e:
            print(f"Error: Could not open PDF file '{self.pdf_path}'. {e}")
            return {} 
        except Exception as e:
            print(f"An unexpected error occurred while opening PDF: {e}")
            return {}

        all_content_blocks = []

        for page_num in range(len(self.doc)):
            page = self.doc[page_num]

            page_text = self.extract_text_from_page(page)
            page_images = self.extract_images_from_page(page, page_num)
            question_blocks = self.identify_question_blocks(page_text, page_images)
            question_blocks_with_assets = self.associate_images_with_questions(
                question_blocks, page_images
            )
            all_content_blocks.extend(question_blocks_with_assets)
        organized_content = self.organize_by_sections(all_content_blocks)

        self.doc.close()
        return organized_content