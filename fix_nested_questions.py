#!/usr/bin/env python3
"""
Fix Nested Questions in Self-Reported Mental Health Dataset

This script fixes the nested question structure in the self-reported-mental-health dataset
by properly representing the base_question and sub_questions hierarchy in all formats
(XML, HTML, MD, TXT, TTL) to match the JSON structure.
"""

import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NestedQuestionFixer:
    """Fix nested question structures across different formats."""
    
    def __init__(self, benchmark_cache_dir: str = "benchmark_cache"):
        self.benchmark_cache_dir = Path(benchmark_cache_dir)
        self.dataset_name = "self-reported-mental-health"
        self.dataset_path = self.benchmark_cache_dir / self.dataset_name
        
        # Define the nested questions that need fixing based on JSON structure
        self.nested_questions = {
            "Parental Education": {
                "base_question": "How many years of education did your parents receive? [Open-ended]",
                "sub_questions": {
                    "Father": "Father?",
                    "Mother": "Mother?"
                }
            },
            "Emotional Regulation Frequency": {
                "base_question": "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 4, where 0 is never, 1 is 'almost never', 2 is 'sometimes', 3 is 'fairly often', and 4 is 'very often', how often you experienced the following feelings during the last month: [Likert 0–4]",
                "sub_questions": {
                    "Upset by Unexpected Events": "how often have you been upset because of something that happened unexpectedly?",
                    "Unable to Control Important Things": "how often have you felt that you were unable to control the important things in your life?",
                    "Nervous and Stressed": "how often have you felt nervous and stressed?",
                    "Lacked Confidence Handling Problems": "how often have you felt confident about your ability to handle your personal problems?",
                    "Things Going Your Way": "how often have you felt that things were going your way?",
                    "Unable to Cope": "how often have you found that you could not cope with all the things that you had to do?",
                    "Irritated by Life": "how often have you been able to control irritations in your life?",
                    "On Top of Things": "how often have you felt that you were on top of things?",
                    "Angered by Uncontrollable Events": "how often have you been angered because of things that happened that were outside of your control?",
                    "Felt Overwhelmed": "how often have you felt difficulties were piling up so high that you could not overcome them?"
                }
            },
            "Anxiety Symptoms Frequency": {
                "base_question": "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]",
                "sub_questions": {
                    "Feeling Nervous or On Edge": "Feeling nervous, anxious, or on edge",
                    "Uncontrollable Worrying": "Not being able to stop or control worrying",
                    "Excessive Worry": "Worrying too much about different things",
                    "Trouble Relaxing": "Trouble relaxing",
                    "Restlessness": "Being so restless that it is hard to sit still",
                    "Irritability": "Becoming easily annoyed or irritable",
                    "Fear Something Awful Might Happen": "Feeling afraid, as if something awful might happen"
                }
            },
            "Depression Symptoms Frequency": {
                "base_question": "Next, you will be asked questions about your emotional state. Please answer on a scale of 0 to 3, where 0 is 'Not at all', 1 is 'several days', 2 is 'more than half of the days', and 3 is 'Nearly every day'. Over the last two weeks, how often have you been bothered by the following problems? [Likert 0–3]",
                "sub_questions": {
                    "Little Interest or Pleasure": "Little interest or pleasure in doing things",
                    "Feeling Down or Hopeless": "Feeling down, depressed, or hopeless",
                    "Sleep Problems": "Trouble falling or staying asleep, or sleeping too much",
                    "Feeling Tired": "Feeling tired or having little energy",
                    "Poor Appetite": "Poor appetite or overeating",
                    "Feeling Bad About Yourself": "Feeling bad about yourself or that you are a failure or have let yourself or your family down",
                    "Trouble Concentrating": "Trouble concentrating on things, such as reading the newspaper or watching television",
                    "Moving Slowly or Restlessly": "Moving or speaking so slowly that other people could have noticed. Or the opposite being so fidgety or restless that you have been moving around a lot more than usual",
                    "Thoughts of Self-Harm": "Thoughts that you would be better off dead, or thoughts of hurting yourself in some way"
                }
            }
        }
    
    def load_json_reference(self, task: str, case_id: str) -> Dict[str, Any]:
        """Load JSON reference to get the correct nested structure."""
        json_file = self.dataset_path / task / "json" / f"{case_id}.json"
        if not json_file.exists():
            raise FileNotFoundError(f"JSON reference file not found: {json_file}")
        
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def fix_html_format(self, task: str, case_id: str) -> bool:
        """Fix HTML format nested questions."""
        html_file = self.dataset_path / task / "html" / f"{case_id}.html"
        if not html_file.exists():
            logger.warning(f"HTML file not found: {html_file}")
            return False
        
        logger.info(f"Fixing HTML format for {task}/{case_id}")
        
        # Load JSON reference
        json_data = self.load_json_reference(task, case_id)
        
        # Read current HTML
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Build new questions section
        new_questions_html = []
        
        for question_key, question_data in json_data["questions"].items():
            if isinstance(question_data, dict) and "base_question" in question_data:
                # This is a nested question
                base_question = question_data["base_question"]
                sub_questions = question_data["sub_questions"]
                
                # Add base question with nested sub-questions
                new_questions_html.append(f'  <li>')
                new_questions_html.append(f'    <strong>{question_key}:</strong> {base_question}')
                new_questions_html.append(f'    <ul>')
                
                for sub_key, sub_question in sub_questions.items():
                    new_questions_html.append(f'      <li><strong>{sub_key}:</strong> {sub_question}</li>')
                
                new_questions_html.append(f'    </ul>')
                new_questions_html.append(f'  </li>')
            else:
                # Regular question
                new_questions_html.append(f'  <li><strong>{question_key}:</strong> {question_data}</li>')
        
        # Replace the questions section
        questions_section = '\n'.join(new_questions_html)
        
        # Pattern to match the questions list
        pattern = r'<ul>\s*(.*?)\s*</ul>'
        replacement = f'<ul>\n{questions_section}\n</ul>'
        
        new_html_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
        
        # Write back to file
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(new_html_content)
        
        return True
    
    def fix_xml_format(self, task: str, case_id: str) -> bool:
        """Fix XML format nested questions."""
        xml_file = self.dataset_path / task / "xml" / f"{case_id}.xml"
        if not xml_file.exists():
            logger.warning(f"XML file not found: {xml_file}")
            return False
        
        logger.info(f"Fixing XML format for {task}/{case_id}")
        
        # Load JSON reference
        json_data = self.load_json_reference(task, case_id)
        
        # Parse existing XML
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Find questions element
        questions_elem = root.find('questions')
        if questions_elem is None:
            logger.error(f"No questions element found in {xml_file}")
            return False
        
        # Clear existing questions
        questions_elem.clear()
        
        # Add new questions with proper nesting
        for question_key, question_data in json_data["questions"].items():
            if isinstance(question_data, dict) and "base_question" in question_data:
                # This is a nested question
                base_question = question_data["base_question"]
                sub_questions = question_data["sub_questions"]
                
                # Add base question group
                question_group = ET.SubElement(questions_elem, 'question_group', {'id': question_key})
                base_elem = ET.SubElement(question_group, 'base_question')
                base_elem.text = base_question
                
                # Add sub-questions
                sub_questions_elem = ET.SubElement(question_group, 'sub_questions')
                for sub_key, sub_question in sub_questions.items():
                    sub_elem = ET.SubElement(sub_questions_elem, 'question', {'id': sub_key})
                    sub_elem.text = sub_question
            else:
                # Regular question
                question_elem = ET.SubElement(questions_elem, 'question', {'id': question_key})
                question_elem.text = question_data
        
        # Write back to file
        tree.write(xml_file, encoding='utf-8', xml_declaration=True)
        
        return True
    
    def fix_markdown_format(self, task: str, case_id: str) -> bool:
        """Fix Markdown format nested questions."""
        md_file = self.dataset_path / task / "md" / f"{case_id}.md"
        if not md_file.exists():
            logger.warning(f"Markdown file not found: {md_file}")
            return False
        
        logger.info(f"Fixing Markdown format for {task}/{case_id}")
        
        # Load JSON reference
        json_data = self.load_json_reference(task, case_id)
        
        # Build new markdown content
        markdown_lines = [
            "# Survey Data",
            "",
            "## Questions",
            ""
        ]
        
        question_num = 1
        for question_key, question_data in json_data["questions"].items():
            if isinstance(question_data, dict) and "base_question" in question_data:
                # This is a nested question
                base_question = question_data["base_question"]
                sub_questions = question_data["sub_questions"]
                
                markdown_lines.append(f"{question_num}. **{question_key}**: {base_question}")
                
                for sub_key, sub_question in sub_questions.items():
                    markdown_lines.append(f"   - **{sub_key}**: {sub_question}")
                
                markdown_lines.append("")
                question_num += 1
            else:
                # Regular question
                markdown_lines.append(f"{question_num}. **{question_key}**: {question_data}")
                markdown_lines.append("")
                question_num += 1
        
        # Read existing file to preserve responses section
        with open(md_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Find responses section
        responses_match = re.search(r'## Responses.*$', existing_content, re.DOTALL)
        if responses_match:
            responses_section = responses_match.group(0)
            markdown_lines.extend(["", responses_section])
        
        # Write back to file
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(markdown_lines))
        
        return True
    
    def fix_txt_format(self, task: str, case_id: str) -> bool:
        """Fix TXT format nested questions."""
        txt_file = self.dataset_path / task / "txt" / f"{case_id}.txt"
        if not txt_file.exists():
            logger.warning(f"TXT file not found: {txt_file}")
            return False
        
        logger.info(f"Fixing TXT format for {task}/{case_id}")
        
        # Load JSON reference
        json_data = self.load_json_reference(task, case_id)
        
        # Build new text content
        txt_lines = [
            "Survey Data",
            "=" * 50,
            "",
            "Questions:"
        ]
        
        question_num = 1
        for question_key, question_data in json_data["questions"].items():
            if isinstance(question_data, dict) and "base_question" in question_data:
                # This is a nested question
                base_question = question_data["base_question"]
                sub_questions = question_data["sub_questions"]
                
                txt_lines.append(f"{question_num}. {question_key}: {base_question}")
                
                for sub_key, sub_question in sub_questions.items():
                    txt_lines.append(f"   - {sub_key}: {sub_question}")
                
                question_num += 1
            else:
                # Regular question
                txt_lines.append(f"{question_num}. {question_key}: {question_data}")
                question_num += 1
        
        # Read existing file to preserve responses section
        with open(txt_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Find responses section
        responses_match = re.search(r'Responses:.*$', existing_content, re.DOTALL)
        if responses_match:
            responses_section = responses_match.group(0)
            txt_lines.extend(["", "", responses_section])
        
        # Write back to file
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(txt_lines))
        
        return True
    
    def fix_ttl_format(self, task: str, case_id: str) -> bool:
        """Fix TTL format nested questions."""
        ttl_file = self.dataset_path / task / "ttl" / f"{case_id}.ttl"
        if not ttl_file.exists():
            logger.warning(f"TTL file not found: {ttl_file}")
            return False
        
        logger.info(f"Fixing TTL format for {task}/{case_id}")
        
        # Load JSON reference
        json_data = self.load_json_reference(task, case_id)
        
        # Build new TTL content
        ttl_lines = [
            "@prefix : <http://example.org/survey#> .",
            "@prefix pred: <http://example.org/predicate#> .",
            "",
            "# Questions"
        ]
        
        for question_key, question_data in json_data["questions"].items():
            question_id = question_key.replace(" ", "_").replace("-", "_")
            
            if isinstance(question_data, dict) and "base_question" in question_data:
                # This is a nested question
                base_question = question_data["base_question"]
                sub_questions = question_data["sub_questions"]
                
                # Add base question
                ttl_lines.append(f":Q{question_id} pred:text \"{base_question}\" ;")
                ttl_lines.append(f"    pred:hasSubQuestions (")
                
                # Add sub-questions
                for sub_key, sub_question in sub_questions.items():
                    sub_id = sub_key.replace(" ", "_").replace("-", "_")
                    ttl_lines.append(f"        :Q{question_id}_{sub_id}")
                
                ttl_lines.append("    ) .")
                ttl_lines.append("")
                
                # Define sub-questions
                for sub_key, sub_question in sub_questions.items():
                    sub_id = sub_key.replace(" ", "_").replace("-", "_")
                    ttl_lines.append(f":Q{question_id}_{sub_id} pred:text \"{sub_question}\" .")
                
                ttl_lines.append("")
            else:
                # Regular question
                ttl_lines.append(f":Q{question_id} pred:text \"{question_data}\" .")
        
        # Read existing file to preserve responses section
        with open(ttl_file, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Find responses section
        responses_match = re.search(r'# Responses.*$', existing_content, re.DOTALL)
        if responses_match:
            responses_section = responses_match.group(0)
            ttl_lines.extend(["", responses_section])
        
        # Write back to file
        with open(ttl_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(ttl_lines))
        
        return True
    
    def fix_case(self, task: str, case_id: str) -> Dict[str, bool]:
        """Fix all formats for a specific case."""
        results = {}
        
        # Fix each format
        results['html'] = self.fix_html_format(task, case_id)
        results['xml'] = self.fix_xml_format(task, case_id)  
        results['md'] = self.fix_markdown_format(task, case_id)
        results['txt'] = self.fix_txt_format(task, case_id)
        results['ttl'] = self.fix_ttl_format(task, case_id)
        
        return results
    
    def fix_task(self, task: str, max_cases: Optional[int] = None) -> Dict[str, Dict[str, bool]]:
        """Fix all cases for a specific task."""
        task_path = self.dataset_path / task
        if not task_path.exists():
            logger.error(f"Task directory not found: {task_path}")
            return {}
        
        # Get all cases from JSON directory
        json_dir = task_path / "json"
        if not json_dir.exists():
            logger.error(f"JSON directory not found: {json_dir}")
            return {}
        
        case_files = sorted(json_dir.glob("case_*.json"))
        if max_cases:
            case_files = case_files[:max_cases]
        
        results = {}
        for case_file in case_files:
            case_id = case_file.stem  # e.g., "case_1"
            logger.info(f"Processing {task}/{case_id}")
            results[case_id] = self.fix_case(task, case_id)
        
        return results
    
    def fix_all_tasks(self, max_cases: Optional[int] = None) -> Dict[str, Dict[str, Dict[str, bool]]]:
        """Fix all tasks in the dataset."""
        if not self.dataset_path.exists():
            logger.error(f"Dataset directory not found: {self.dataset_path}")
            return {}
        
        # Get all task directories
        tasks = [d.name for d in self.dataset_path.iterdir() 
                if d.is_dir() and d.name != "metadata.json"]
        
        results = {}
        for task in tasks:
            logger.info(f"Processing task: {task}")
            results[task] = self.fix_task(task, max_cases)
        
        return results
    
    def generate_report(self, results: Dict[str, Dict[str, Dict[str, bool]]]) -> None:
        """Generate a summary report of the fixes."""
        total_cases = 0
        successful_fixes = 0
        failed_fixes = 0
        
        print("\n" + "="*60)
        print("NESTED QUESTIONS FIX REPORT")
        print("="*60)
        
        for task, task_results in results.items():
            print(f"\n📋 Task: {task}")
            print("-" * 40)
            
            for case_id, case_results in task_results.items():
                total_cases += 1
                case_success = all(case_results.values())
                
                if case_success:
                    successful_fixes += 1
                    print(f"  ✅ {case_id}: All formats fixed successfully")
                else:
                    failed_fixes += 1
                    print(f"  ❌ {case_id}: Some formats failed")
                    for format_name, success in case_results.items():
                        if not success:
                            print(f"    - {format_name}: FAILED")
        
        print(f"\n📊 SUMMARY:")
        print(f"  Total cases processed: {total_cases}")
        print(f"  Successful fixes: {successful_fixes}")
        print(f"  Failed fixes: {failed_fixes}")
        print(f"  Success rate: {(successful_fixes/total_cases*100):.1f}%" if total_cases > 0 else "No cases processed")


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Fix nested question structure in self-reported-mental-health dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--task", "-t",
        help="Fix specific task only (e.g., answer_lookup)"
    )
    
    parser.add_argument(
        "--case", "-c", 
        help="Fix specific case only (e.g., case_1). Requires --task"
    )
    
    parser.add_argument(
        "--max-cases", "-n",
        type=int,
        help="Maximum number of cases to fix per task"
    )
    
    parser.add_argument(
        "--benchmark-cache-dir",
        default="benchmark_cache",
        help="Path to benchmark cache directory (default: benchmark_cache)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize fixer
    fixer = NestedQuestionFixer(args.benchmark_cache_dir)
    
    try:
        if args.case and args.task:
            # Fix specific case
            logger.info(f"Fixing specific case: {args.task}/{args.case}")
            case_results = fixer.fix_case(args.task, args.case)
            
            results = {args.task: {args.case: case_results}}
            fixer.generate_report(results)
            
        elif args.task:
            # Fix specific task
            logger.info(f"Fixing specific task: {args.task}")
            task_results = fixer.fix_task(args.task, args.max_cases)
            
            results = {args.task: task_results}
            fixer.generate_report(results)
            
        else:
            # Fix all tasks
            logger.info("Fixing all tasks in self-reported-mental-health dataset")
            results = fixer.fix_all_tasks(args.max_cases)
            fixer.generate_report(results)
        
        logger.info("Nested question fixes completed!")
        return 0
        
    except Exception as e:
        logger.error(f"Fix operation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())