"""
Evaluation module for benchmark results
"""

import re
import json
from typing import Dict, List, Any, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class BenchmarkEvaluator:
    """Evaluates LLM responses against expected answers."""
    
    def __init__(self):
        pass
    
    def evaluate_response(self, response: str, expected: str, task_type: str) -> Dict[str, Any]:
        """
        Evaluate a single response against expected answer.
        
        Args:
            response: LLM response
            expected: Expected answer
            task_type: Type of task (affects evaluation method)
            
        Returns:
            Dictionary with evaluation metrics
        """
        if response is None or response == "":
            return {
                "exact_match": False,
                "normalized_match": False,
                "partial_match": False,
                "score": 0.0,
                "error": "Empty response"
            }
        
        # Convert to strings for consistent comparison
        response_str = str(response)
        expected_str = str(expected)
        
        # Normalize strings for comparison
        response_norm = self._normalize_text(response_str)
        expected_norm = self._normalize_text(expected_str)
        
        # Exact match (as strings)
        exact_match = response_str == expected_str
        
        # Normalized match (case insensitive, whitespace normalized)
        normalized_match = response_norm == expected_norm
        
        # Partial match (expected answer contained in response)
        partial_match = expected_norm in response_norm
        
        # Calculate score
        score = self._calculate_score(response_norm, expected_norm, exact_match, normalized_match, partial_match)
        
        return {
            "exact_match": exact_match,
            "normalized_match": normalized_match,
            "partial_match": partial_match,
            "score": score,
            "error": None
        }
    
    def _normalize_text(self, text) -> str:
        """Normalize text for comparison."""
        if text is None:
            return ""
        
        # Convert to string first (handles integers, floats, etc.)
        text = str(text).strip()
        
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common punctuation at the end
        text = re.sub(r'[.,!?;:]$', '', text)
        
        return text
    
    def _calculate_score(self, response: str, expected: str, exact: bool, normalized: bool, partial: bool) -> float:
        """Calculate evaluation score with confidence-based penalties."""
        if exact:
            return 1.0
        elif normalized:
            return 0.9
        elif partial:
            # For partial matches, check if it's a numerical answer contained in explanatory text
            if self._is_numeric(expected):
                # Extract numbers from response and check if expected number is there
                numbers_in_response = self._extract_numbers(response)
                if expected in numbers_in_response:
                    # Check for confidence indicators
                    confidence_penalty = self._calculate_confidence_penalty(response, expected)
                    base_score = 0.9  # Higher score for correct numerical answer with explanation
                    return max(0.0, base_score - confidence_penalty)
            
            # For non-numerical answers, apply confidence penalty
            confidence_penalty = self._calculate_confidence_penalty(response, expected)
            base_score = 0.7  # General partial match score
            return max(0.0, base_score - confidence_penalty)
        else:
            # Check for numerical similarity for numeric answers
            if self._is_numeric(expected) and self._is_numeric(response):
                try:
                    exp_num = float(expected)
                    resp_num = float(response)
                    if exp_num == resp_num:
                        return 0.8
                except:
                    pass
            return 0.0
    
    def _calculate_confidence_penalty(self, response: str, expected: str) -> float:
        """
        Calculate confidence penalty based on uncertainty indicators and wrong options.
        
        Returns:
            Penalty value between 0.0 and 0.5
        """
        penalty = 0.0
        
        # Convert to lowercase for case-insensitive matching
        response_lower = response.lower()
        
        # Uncertainty indicators that suggest the model is not confident
        uncertainty_indicators = [
            'but', 'however', 'although', 'though', 'while',
            'might be', 'could be', 'may be', 'possibly',
            'i think', 'i believe', 'i guess', 'i suppose',
            'not sure', 'uncertain', 'unclear', 'ambiguous',
            'either', 'or', 'alternatively', 'on the other hand',
            'some people think', 'others might say', 'it depends',
            'it could be argued', 'there are arguments for'
        ]
        
        # Count uncertainty indicators
        uncertainty_count = sum(1 for indicator in uncertainty_indicators if indicator in response_lower)
        if uncertainty_count > 0:
            penalty += min(0.2, uncertainty_count * 0.05)  # Max 0.2 penalty for uncertainty
        
        # Check for multiple options being mentioned (suggesting confusion)
        # Look for patterns like "A or B", "A, B, C", "A vs B", etc.
        option_patterns = [
            r'\b[a-d]\s*(?:or|vs|versus|,|and)\s*[a-d]\b',  # A or B, A vs B, A, B
            r'\b[a-d]\s*,\s*[a-d]\s*(?:,|and)\s*[a-d]\b',   # A, B, C
            r'\b(?:option|choice)\s*[a-d]\s*(?:and|or)\s*(?:option|choice)\s*[a-d]\b'
        ]
        
        import re
        option_matches = 0
        for pattern in option_patterns:
            matches = re.findall(pattern, response_lower)
            option_matches += len(matches)
        
        if option_matches > 0:
            penalty += min(0.3, option_matches * 0.1)  # Max 0.3 penalty for multiple options
        
        # Check if the expected answer appears with qualifiers that suggest uncertainty
        qualifier_patterns = [
            r'\b(?:probably|maybe|perhaps|likely)\s+' + re.escape(expected.lower()),
            re.escape(expected.lower()) + r'\s*\b(?:probably|maybe|perhaps|likely)\b',
            r'\b(?:i think|i believe|i guess)\s+' + re.escape(expected.lower()),
            re.escape(expected.lower()) + r'\s*\b(?:i think|i believe|i guess)\b'
        ]
        
        qualifier_matches = 0
        for pattern in qualifier_patterns:
            if re.search(pattern, response_lower):
                qualifier_matches += 1
        
        if qualifier_matches > 0:
            penalty += min(0.2, qualifier_matches * 0.1)  # Max 0.2 penalty for qualifiers
        
        # Check for contradiction patterns (mentioning both correct and clearly wrong answers)
        # This is a stronger penalty
        contradiction_indicators = [
            r'\b(?:wrong|incorrect|not|false)\s+[a-d]\b',
            r'\b[a-d]\s+(?:is wrong|is incorrect|is not correct|is false)\b',
            r'\b(?:eliminate|exclude|rule out)\s+[a-d]\b'
        ]
        
        contradiction_count = 0
        for pattern in contradiction_indicators:
            matches = re.findall(pattern, response_lower)
            contradiction_count += len(matches)
        
        if contradiction_count > 0:
            penalty += min(0.4, contradiction_count * 0.15)  # Max 0.4 penalty for contradictions
        
        return min(0.5, penalty)  # Cap total penalty at 0.5
    
    def _is_numeric(self, text: str) -> bool:
        """Check if text represents a number."""
        try:
            float(text.replace(',', ''))
            return True
        except:
            return False
    
    def _extract_numbers(self, text: str) -> List[str]:
        """Extract all numbers from text."""
        import re
        # Find all numbers (integers and decimals) in the text
        numbers = re.findall(r'\d+(?:\.\d+)?', text)
        return numbers
    
    def calculate_performance_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate overall performance metrics from a list of results.
        
        Args:
            results: List of evaluation results
            
        Returns:
            Dictionary with performance metrics
        """
        if not results:
            return {
                "total_cases": 0,
                "successful_responses": 0,
                "exact_match_rate": 0.0,
                "normalized_match_rate": 0.0,
                "partial_match_rate": 0.0,
                "average_score": 0.0,
                "success_rate": 0.0,
                "average_response_time": 0.0
            }
        
        total_cases = len(results)
        successful_responses = sum(1 for r in results if r.get('llm_result', {}).get('success', False))
        
        # Filter successful responses for accuracy metrics
        successful_results = [r for r in results if r.get('llm_result', {}).get('success', False)]
        
        if not successful_results:
            exact_match_rate = normalized_match_rate = partial_match_rate = average_score = 0.0
        else:
            exact_matches = sum(1 for r in successful_results if r.get('evaluation', {}).get('exact_match', False))
            normalized_matches = sum(1 for r in successful_results if r.get('evaluation', {}).get('normalized_match', False))
            partial_matches = sum(1 for r in successful_results if r.get('evaluation', {}).get('partial_match', False))
            
            exact_match_rate = exact_matches / len(successful_results)
            normalized_match_rate = normalized_matches / len(successful_results)
            partial_match_rate = partial_matches / len(successful_results)
            
            scores = [r.get('evaluation', {}).get('score', 0.0) for r in successful_results]
            average_score = sum(scores) / len(scores) if scores else 0.0
        
        # Calculate average response time
        response_times = [r.get('llm_result', {}).get('response_time', 0) for r in results if r.get('llm_result', {}).get('success', False)]
        average_response_time = sum(response_times) / len(response_times) if response_times else 0.0
        
        return {
            "total_cases": total_cases,
            "successful_responses": successful_responses,
            "exact_match_rate": exact_match_rate,
            "normalized_match_rate": normalized_match_rate,
            "partial_match_rate": partial_match_rate,
            "average_score": average_score,
            "success_rate": successful_responses / total_cases,
            "average_response_time": average_response_time
        }
    
    def analyze_by_format(self, results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by data format."""
        format_results = {}
        
        # Group results by data format
        for result in results:
            data_format = result.get('data_format', 'unknown')
            if data_format not in format_results:
                format_results[data_format] = []
            format_results[data_format].append(result)
        
        # Calculate metrics for each format
        format_metrics = {}
        for data_format, format_data in format_results.items():
            format_metrics[data_format] = self.calculate_performance_metrics(format_data)
        
        return format_metrics
    
    def analyze_by_task(self, results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Analyze performance by task type."""
        task_results = {}
        
        # Group results by task
        for result in results:
            task = result.get('task', 'unknown')
            if task not in task_results:
                task_results[task] = []
            task_results[task].append(result)
        
        # Calculate metrics for each task
        task_metrics = {}
        for task, task_data in task_results.items():
            task_metrics[task] = self.calculate_performance_metrics(task_data)
        
        return task_metrics
    
    def get_best_format(self, format_metrics: Dict[str, Dict[str, Any]]) -> Tuple[Optional[str], Dict[str, Any]]:
        """Determine the best performing data format."""
        if not format_metrics:
            return None, {}
        
        # Rank by average score, then by success rate
        best_format = None
        best_score = -1
        best_metrics = {}
        
        for data_format, metrics in format_metrics.items():
            # Weighted score: 70% accuracy + 30% success rate
            weighted_score = (metrics['average_score'] * 0.7) + (metrics['success_rate'] * 0.3)
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_format = data_format
                best_metrics = metrics
        
        return best_format, best_metrics 