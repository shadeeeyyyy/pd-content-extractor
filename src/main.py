import sys
import json
import os 
from pdf_extractor import PDFExtractor
from validator import ContentValidator

def main(pdf_path):
    print(f"Starting PDF analysis for: {pdf_path}")

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        sys.exit(1)
    output_base_dir = "output"
    images_output_dir = os.path.join(output_base_dir, "extracted_images")
    text_output_dir = os.path.join(output_base_dir, "extracted_text")

    extractor = PDFExtractor(pdf_path, output_dir=output_base_dir)
    extractor.setup_directories() 
    print("Extracting content...")
    try:
        extracted_content = extractor.extract_all_content()
        if not extracted_content:
            print("Warning: No content extracted from PDF. Check PDF content or extraction logic.")
    except Exception as e:
        print(f"Error during content extraction: {e}")
        sys.exit(1)
    output_json_path = os.path.join(extractor.output_dir, "extracted_content.json")
    try:
        with open(output_json_path, 'w', encoding='utf-8') as f:
            json.dump(extracted_content, f, indent=2, ensure_ascii=False)
        print(f"Extracted content saved to: {output_json_path}")
    except IOError as e:
        print(f"Error saving extracted content JSON: {e}")
        sys.exit(1)
    print("Validating extraction quality...")
    validator = ContentValidator()
    try:
        validation_report = validator.validate_extraction(
            extracted_content,
            extractor.images_dir,
            expected_question_count=35, 
            expected_images=50 
        )
    except Exception as e:
        print(f"Error during validation: {e}")
        sys.exit(1)
    report_path = os.path.join(extractor.output_dir, "validation_report.json")
    try:
        with open(report_path, 'w', encoding='utf-8') as f: 
            json.dump(validation_report, f, indent=2, ensure_ascii=False)
        print(f"Validation report saved to: {report_path}")
    except IOError as e:
        print(f"Error saving validation report JSON: {e}")
        sys.exit(1)

    print(f"\n--- Processing complete for {os.path.basename(pdf_path)} ---")
    print(f"Overall Score: {validation_report['scores']['overall_score']:.1f}%")
    print(f"Status: {validation_report['status']}")
    if validation_report["status"] == "FAIL":
        print("\nRecommendations:")
        for rec in validation_report["recommendations"]:
            print(f"  - {rec}")

    return extracted_content, validation_report

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python src/main.py <path_to_pdf>")
        sys.exit(1)

    pdf_path_arg = sys.argv[1]
    absolute_pdf_path = os.path.abspath(pdf_path_arg)

    main(absolute_pdf_path)