#!/usr/bin/env python3
"""
Respondent ID Consistency Validator

This script validates that the same case_id across different data formats
contains the same respondent IDs in the converted prompts.
"""

import csv
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Set
import logging
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RespondentIDExtractor:
    """Extract respondent IDs from different data formats."""
    
    def extract_from_json(self, data: str) -> Set[str]:
        """Extract respondent IDs from JSON format."""
        try:
            parsed_data = json.loads(data)
            respondent_ids = set()
            
            if 'responses' in parsed_data:
                for response in parsed_data['responses']:
                    if 'respondent' in response:
                        respondent_ids.add(str(response['respondent']))
            
            return respondent_ids
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to extract respondent IDs from JSON: {e}")
            return set()
    
    def extract_from_xml(self, data: str) -> Set[str]:
        """Extract respondent IDs from XML format."""
        try:
            # Clean up the XML data
            data = data.strip()
            root = ET.fromstring(data)
            respondent_ids = set()
            
            # Look for respondent elements with id attribute: <respondent id="2">
            for respondent in root.findall('.//respondent[@id]'):
                respondent_id = respondent.get('id')
                if respondent_id:
                    respondent_ids.add(respondent_id.strip())
            
            # Alternative structure - look for response elements
            for response in root.findall('.//response'):
                respondent_elem = response.find('respondent')
                if respondent_elem is not None and respondent_elem.text:
                    respondent_ids.add(respondent_elem.text.strip())
            
            # Alternative structure - respondent as attribute
            for response in root.findall('.//response[@respondent]'):
                respondent_ids.add(response.get('respondent'))
            
            return respondent_ids
            
        except ET.ParseError as e:
            logger.warning(f"Failed to parse XML: {e}")
            return set()
    
    def extract_from_html(self, data: str) -> Set[str]:
        """Extract respondent IDs from HTML format."""
        respondent_ids = set()
        
        # Use regex to find respondent IDs in HTML structure
        # Look for patterns like: <td>respondent_id</td> or similar
        patterns = [
            r'<td[^>]*>(\d+)</td>',  # Table cell with number
            r'respondent["\']?\s*:\s*["\']?(\d+)["\']?',  # respondent: id pattern
            r'<[^>]*respondent[^>]*>(\d+)</[^>]*>',  # Any tag with respondent containing number
            r'Respondent\s*(\d+)',  # "Respondent 123" pattern
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, data, re.IGNORECASE)
            respondent_ids.update(matches)
        
        return respondent_ids
    
    def extract_from_markdown(self, data: str) -> Set[str]:
        """Extract respondent IDs from Markdown format."""
        respondent_ids = set()
        
        # Look for patterns in markdown
        patterns = [
            r'\|\s*(\d+)\s*\|',  # Table format: | 123 |
            r'respondent[:\s]+(\d+)',  # respondent: 123 or respondent 123
            r'^\s*(\d+)\s*\|',  # Start of line number followed by |
            r'- Respondent (\d+)',  # - Respondent 123
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, data, re.IGNORECASE | re.MULTILINE)
            respondent_ids.update(matches)
        
        return respondent_ids
    
    def extract_from_txt(self, data: str) -> Set[str]:
        """Extract respondent IDs from plain text format."""
        respondent_ids = set()
        
        # Look for patterns in plain text
        patterns = [
            r'respondent[:\s]+(\d+)',  # respondent: 123 or respondent 123
            r'Respondent\s+(\d+)',  # Respondent 123
            r'ID[:\s]+(\d+)',  # ID: 123 or ID 123
            r'^(\d+)\s*[:\|]',  # Line starting with number followed by : or |
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, data, re.IGNORECASE | re.MULTILINE)
            respondent_ids.update(matches)
        
        return respondent_ids
    
    def extract_from_ttl(self, data: str) -> Set[str]:
        """Extract respondent IDs from TTL (Turtle/RDF) format."""
        respondent_ids = set()
        
        # Look for RDF/Turtle patterns - :Respondent2, :Respondent118, etc.
        patterns = [
            r':Respondent(\d+)',  # :Respondent2, :Respondent118
            r'respondent_(\d+)',  # respondent_123
            r'respondent:\s*"(\d+)"',  # respondent: "123"
            r'<[^>]*respondent[^>]*>\s*(\d+)',  # <respondent> 123
            r'pred:respondent\s+(\d+)',  # pred:respondent 123
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, data, re.IGNORECASE)
            respondent_ids.update(matches)
        
        return respondent_ids
    
    def extract_respondent_ids(self, data: str, format_type: str) -> Set[str]:
        """Extract respondent IDs based on format type."""
        format_type = format_type.lower()
        
        if format_type == 'json':
            return self.extract_from_json(data)
        elif format_type == 'xml':
            return self.extract_from_xml(data)
        elif format_type == 'html':
            return self.extract_from_html(data)
        elif format_type == 'md':
            return self.extract_from_markdown(data)
        elif format_type == 'txt':
            return self.extract_from_txt(data)
        elif format_type == 'ttl':
            return self.extract_from_ttl(data)
        else:
            logger.warning(f"Unknown format type: {format_type}")
            return set()


class RespondentConsistencyValidator:
    """Validate respondent ID consistency across formats."""
    
    def __init__(self, converted_prompts_dir: str = "converted_prompts"):
        self.converted_prompts_dir = Path(converted_prompts_dir)
        self.extractor = RespondentIDExtractor()
        self.formats = ['json', 'xml', 'html', 'md', 'txt', 'ttl']
    
    def load_csv_data(self, csv_file: Path) -> List[Dict[str, str]]:
        """Load data from CSV file."""
        data = []
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                # Increase field size limit to handle large questionnaire data
                csv.field_size_limit(1000000)
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(row)
        except Exception as e:
            logger.error(f"Error reading CSV file {csv_file}: {e}")
        
        return data
    
    def extract_case_respondents(self, dataset: str, task: str) -> Dict[str, Dict[str, Set[str]]]:
        """
        Extract respondent IDs for each case across all formats.
        
        Returns:
            Dict[case_id, Dict[format, Set[respondent_ids]]]
        """
        task_dir = self.converted_prompts_dir / dataset / task
        
        if not task_dir.exists():
            logger.warning(f"Task directory not found: {task_dir}")
            return {}
        
        case_respondents = defaultdict(lambda: defaultdict(set))
        
        for format_type in self.formats:
            csv_file = task_dir / f"{task}_{format_type}_converted_prompts.csv"
            
            if not csv_file.exists():
                logger.warning(f"CSV file not found: {csv_file}")
                continue
            
            logger.info(f"Processing {csv_file}")
            csv_data = self.load_csv_data(csv_file)
            
            for row in csv_data:
                case_id = row.get('case_id', '')
                questionnaire = row.get('questionnaire', '')
                
                if case_id and questionnaire:
                    respondent_ids = self.extractor.extract_respondent_ids(questionnaire, format_type)
                    case_respondents[case_id][format_type] = respondent_ids
                    
                    logger.debug(f"Case {case_id} ({format_type}): {len(respondent_ids)} respondents")
        
        return dict(case_respondents)
    
    def validate_case_consistency(self, case_respondents: Dict[str, Dict[str, Set[str]]]) -> List[Dict]:
        """Validate that each case has consistent respondent IDs across formats."""
        inconsistencies = []
        
        for case_id, format_data in case_respondents.items():
            if len(format_data) <= 1:
                continue  # Need at least 2 formats to compare
            
            # Get all unique respondent sets
            respondent_sets = list(format_data.values())
            reference_set = respondent_sets[0]
            
            # Check if all sets are identical
            all_identical = all(resp_set == reference_set for resp_set in respondent_sets)
            
            if not all_identical:
                inconsistency = {
                    'case_id': case_id,
                    'formats': {},
                    'issue_type': 'respondent_mismatch'
                }
                
                for format_type, respondent_set in format_data.items():
                    inconsistency['formats'][format_type] = {
                        'respondent_ids': sorted(list(respondent_set)),
                        'count': len(respondent_set)
                    }
                
                inconsistencies.append(inconsistency)
        
        return inconsistencies
    
    def validate_dataset_task(self, dataset: str, task: str) -> Dict:
        """Validate a specific dataset/task combination."""
        logger.info(f"Validating {dataset}/{task}")
        
        case_respondents = self.extract_case_respondents(dataset, task)
        inconsistencies = self.validate_case_consistency(case_respondents)
        
        # Summary statistics
        total_cases = len(case_respondents)
        inconsistent_cases = len(inconsistencies)
        consistent_cases = total_cases - inconsistent_cases
        
        return {
            'dataset': dataset,
            'task': task,
            'total_cases': total_cases,
            'consistent_cases': consistent_cases,
            'inconsistent_cases': inconsistent_cases,
            'consistency_rate': (consistent_cases / total_cases * 100) if total_cases > 0 else 0,
            'inconsistencies': inconsistencies
        }
    
    def validate_all(self) -> Dict:
        """Validate all datasets and tasks."""
        logger.info("Starting comprehensive respondent ID consistency validation")
        
        if not self.converted_prompts_dir.exists():
            raise FileNotFoundError(f"Converted prompts directory not found: {self.converted_prompts_dir}")
        
        results = {
            'validation_results': [],
            'summary': {
                'total_datasets': 0,
                'total_tasks': 0,
                'total_cases': 0,
                'total_consistent_cases': 0,
                'total_inconsistent_cases': 0,
                'overall_consistency_rate': 0
            }
        }
        
        datasets = [d.name for d in self.converted_prompts_dir.iterdir() if d.is_dir()]
        
        total_cases = 0
        total_consistent = 0
        total_inconsistent = 0
        total_tasks = 0
        
        for dataset in datasets:
            dataset_dir = self.converted_prompts_dir / dataset
            tasks = [t.name for t in dataset_dir.iterdir() if t.is_dir()]
            
            for task in tasks:
                total_tasks += 1
                task_result = self.validate_dataset_task(dataset, task)
                results['validation_results'].append(task_result)
                
                total_cases += task_result['total_cases']
                total_consistent += task_result['consistent_cases']
                total_inconsistent += task_result['inconsistent_cases']
        
        # Update summary
        results['summary'] = {
            'total_datasets': len(datasets),
            'total_tasks': total_tasks,
            'total_cases': total_cases,
            'total_consistent_cases': total_consistent,
            'total_inconsistent_cases': total_inconsistent,
            'overall_consistency_rate': (total_consistent / total_cases * 100) if total_cases > 0 else 0
        }
        
        return results
    
    def generate_report(self, results: Dict, output_file: str = "respondent_consistency_report.json"):
        """Generate a detailed validation report."""
        
        # Save detailed JSON report
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Detailed report saved to: {output_file}")
        
        # Print summary to console
        summary = results['summary']
        
        print("\n" + "="*60)
        print("RESPONDENT ID CONSISTENCY VALIDATION REPORT")
        print("="*60)
        print(f"📊 Total Datasets: {summary['total_datasets']}")
        print(f"📋 Total Tasks: {summary['total_tasks']}")
        print(f"📄 Total Cases: {summary['total_cases']}")
        print(f"✅ Consistent Cases: {summary['total_consistent_cases']}")
        print(f"❌ Inconsistent Cases: {summary['total_inconsistent_cases']}")
        print(f"📈 Overall Consistency Rate: {summary['overall_consistency_rate']:.2f}%")
        
        # Show problematic cases
        problematic_results = [r for r in results['validation_results'] if r['inconsistent_cases'] > 0]
        
        if problematic_results:
            print(f"\n⚠️  ISSUES FOUND ({len(problematic_results)} dataset/task combinations):")
            print("-" * 60)
            
            for result in problematic_results:
                print(f"📁 {result['dataset']}/{result['task']}: {result['inconsistent_cases']}/{result['total_cases']} cases inconsistent ({result['consistency_rate']:.1f}% consistent)")
                
                # Show first few inconsistencies as examples
                for i, inconsistency in enumerate(result['inconsistencies'][:3]):
                    print(f"  • Case {inconsistency['case_id']}:")
                    for fmt, data in inconsistency['formats'].items():
                        print(f"    - {fmt.upper()}: {data['count']} respondents {data['respondent_ids']}")
                
                if len(result['inconsistencies']) > 3:
                    print(f"    ... and {len(result['inconsistencies']) - 3} more cases")
                print()
        else:
            print("\n🎉 No inconsistencies found! All cases have matching respondent IDs across formats.")
        
        print(f"\n📄 Full detailed report saved to: {output_file}")


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate respondent ID consistency across data formats",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--converted-prompts-dir",
        default="converted_prompts",
        help="Directory containing converted prompts (default: converted_prompts)"
    )
    
    parser.add_argument(
        "--dataset",
        help="Validate specific dataset only"
    )
    
    parser.add_argument(
        "--task", 
        help="Validate specific task only (requires --dataset)"
    )
    
    parser.add_argument(
        "--output",
        default="respondent_consistency_report.json",
        help="Output report file (default: respondent_consistency_report.json)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    validator = RespondentConsistencyValidator(args.converted_prompts_dir)
    
    try:
        if args.dataset and args.task:
            # Validate specific dataset/task
            result = validator.validate_dataset_task(args.dataset, args.task)
            results = {
                'validation_results': [result],
                'summary': {
                    'total_datasets': 1,
                    'total_tasks': 1,
                    'total_cases': result['total_cases'],
                    'total_consistent_cases': result['consistent_cases'],
                    'total_inconsistent_cases': result['inconsistent_cases'],
                    'overall_consistency_rate': result['consistency_rate']
                }
            }
        elif args.dataset:
            # Validate all tasks for specific dataset
            dataset_dir = Path(args.converted_prompts_dir) / args.dataset
            if not dataset_dir.exists():
                logger.error(f"Dataset directory not found: {dataset_dir}")
                return 1
            
            tasks = [t.name for t in dataset_dir.iterdir() if t.is_dir()]
            validation_results = []
            total_cases = total_consistent = total_inconsistent = 0
            
            for task in tasks:
                result = validator.validate_dataset_task(args.dataset, task)
                validation_results.append(result)
                total_cases += result['total_cases']
                total_consistent += result['consistent_cases']
                total_inconsistent += result['inconsistent_cases']
            
            results = {
                'validation_results': validation_results,
                'summary': {
                    'total_datasets': 1,
                    'total_tasks': len(tasks),
                    'total_cases': total_cases,
                    'total_consistent_cases': total_consistent,
                    'total_inconsistent_cases': total_inconsistent,
                    'overall_consistency_rate': (total_consistent / total_cases * 100) if total_cases > 0 else 0
                }
            }
        else:
            # Validate all datasets and tasks
            results = validator.validate_all()
        
        validator.generate_report(results, args.output)
        
        # Return exit code based on consistency
        if results['summary']['total_inconsistent_cases'] > 0:
            logger.warning("Validation completed with inconsistencies found")
            return 1
        else:
            logger.info("Validation completed successfully - all cases consistent")
            return 0
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())