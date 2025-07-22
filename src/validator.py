import os
from datetime import datetime

class ContentValidator:
    def __init__(self):
        self.validation_results = {
            "text_extraction_score": 0,
            "image_extraction_score": 0,
            "structure_accuracy_score": 0, 
            "overall_score": 0,
            "issues": []
        }

    def validate_text_extraction(self, extracted_content, expected_question_count=35):
        """
        Validate text extraction quality.
        `extracted_content` is the dictionary organized by sections.
        """
        total_questions = 0
        for section_name, questions_list in extracted_content.items():
            if section_name != "UNSORTED": 
                total_questions += len(questions_list)

        if total_questions >= expected_question_count * 0.9: 
            self.validation_results["text_extraction_score"] = 100
        else:
            score = (total_questions / expected_question_count) * 100
            self.validation_results["text_extraction_score"] = round(score, 2) 
            self.validation_results["issues"].append(
                f"Text Extraction: Expected ~{expected_question_count} questions, found {total_questions}."
            )

    def validate_image_extraction(self, images_dir, expected_images=50):
        """Validate image extraction quality."""
        if not os.path.exists(images_dir):
            self.validation_results["image_extraction_score"] = 0
            self.validation_results["issues"].append("Image Extraction: No images directory found.")
            return

        image_files = [f for f in os.listdir(images_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] 

        if len(image_files) >= expected_images * 0.8: 
            self.validation_results["image_extraction_score"] = 100
        else:
            score = (len(image_files) / expected_images) * 100
            self.validation_results["image_extraction_score"] = round(score, 2) 
            self.validation_results["issues"].append(
                f"Image Extraction: Expected ~{expected_images} images, found {len(image_files)}."
            )

    def validate_structure_accuracy(self, extracted_content, expected_sections=["LOGICAL_REASONING", "MATHEMATICS", "ACHIEVER_SECTION"]):
        """
        Validate the accuracy of the extracted content's structure.
        Checks if expected sections are present and if UNSORTED is minimal.
        """
        score = 0
        issues = []
        found_expected_sections = True
        for section in expected_sections:
            if section not in extracted_content or not extracted_content[section]:
                found_expected_sections = False
                issues.append(f"Structure Accuracy: Missing or empty section '{section}'.")

        if found_expected_sections:
            score += 50 
        unsorted_count = len(extracted_content.get("UNSORTED", []))
        total_extracted_items = sum(len(v) for k, v in extracted_content.items() if k != "UNSORTED") 

        if total_extracted_items > 0 and unsorted_count / total_extracted_items < 0.05:
            score += 50
        elif unsorted_count > 0:
            issues.append(f"Structure Accuracy: {unsorted_count} items found in 'UNSORTED' section.")

        self.validation_results["structure_accuracy_score"] = round(score, 2)
        self.validation_results["issues"].extend(issues)


    def calculate_overall_score(self):
        """Calculate overall extraction success score."""
        weights = {
            "text_extraction_score": 0.4,
            "image_extraction_score": 0.3,
            "structure_accuracy_score": 0.3
        }

        overall = sum(
            self.validation_results[metric] * weight
            for metric, weight in weights.items()
        )
        self.validation_results["overall_score"] = round(overall, 2) 
        return self.validation_results["overall_score"]

    def generate_validation_report(self):
        """Generate detailed validation report."""
        self.calculate_overall_score()
        report = {
            "timestamp": datetime.now().isoformat(),
            "scores": self.validation_results,
            "status": "PASS" if self.validation_results["overall_score"] >= 80 else "FAIL",
            "recommendations": self._generate_recommendations()
        }
        return report

    def _generate_recommendations(self):
        """Helper to generate recommendations based on issues."""
        recommendations = []
        if self.validation_results["overall_score"] < 80:
            recommendations.append("Overall score below 80%. Review extraction process.")
        if self.validation_results["text_extraction_score"] < 90:
            recommendations.append("Text extraction quality is low. Check PDF text layer or regex patterns.")
        if self.validation_results["image_extraction_score"] < 80:
            recommendations.append("Image extraction quality is low. Verify image paths and extraction logic.")
        if self.validation_results["structure_accuracy_score"] < 100:
             recommendations.append("Structural organization is not perfect. Review sectioning logic or expected structure.")
        if self.validation_results["issues"]:
            recommendations.append("Specific issues identified:")
            recommendations.extend([f"- {issue}" for issue in self.validation_results["issues"]])
        if not recommendations:
            recommendations.append("No specific recommendations. Extraction seems good.")
        return recommendations

    def validate_extraction(self, extracted_content, images_dir,
                            expected_question_count=35, expected_images=50,
                            expected_sections=["LOGICAL_REASONING", "MATHEMATICS", "ACHIEVER_SECTION"]):
        """
        Orchestrates all validation steps.
        This is the method that `main.py` should call.
        """
        self.validate_text_extraction(extracted_content, expected_question_count)
        self.validate_image_extraction(images_dir, expected_images)
        self.validate_structure_accuracy(extracted_content, expected_sections)
        self.calculate_overall_score() 
        return self.generate_validation_report()