#!/usr/bin/env python3
"""
Prompt Parser CLI

Command-line interface for generating configurable prompts with different options:
- --one_shot: Omit the one-shot example
- --partition: Omit partition marks (like <example>, <task>, etc.)
- --role: Omit role prompting  
- --format: Omit format explanation
- --order_change: Put questionnaire DATA at the end

Usage:
    python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json
    python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --one_shot --role
    python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --order_change
"""

import argparse
import sys
from pathlib import Path
from configurable_prompt_generator import ConfigurableAdvancedPromptGenerator, PromptConfig, ConfigurablePromptExporter


def create_parser():
    """Create the command line argument parser."""
    
    parser = argparse.ArgumentParser(
        description="Generate configurable advanced prompts with different options",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default prompt (all components included)
  python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json
  
  # Omit one-shot example
  python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --one_shot
  
  # Omit partition marks
  python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --partition
  
  # Omit role prompting
  python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --role
  
  # Omit format explanation
  python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --format
  
  # Put data at the end
  python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --order_change
  
  # Minimal prompt (omit multiple components)
  python prompt_parser_cli.py --dataset healthcare-dataset --task answer_lookup --case case_1 --format json --one_shot --partition --role --format
        """
    )
    
    # Required arguments
    parser.add_argument('--dataset', required=True, 
                       choices=['healthcare-dataset', 'isbar', 'self-reported-mental-health-college-students-2022', 
                               'stack-overflow-2022-developer-survey', 'sus-uta7'],
                       help='Dataset name')
    
    parser.add_argument('--task', required=True,
                       choices=['answer_lookup', 'answer_reverse_lookup', 'conceptual_aggregation',
                               'multi_hop_relational_inference', 'respondent_count', 'rule_based_querying'],
                       help='Task type')
    
    parser.add_argument('--case', required=True,
                       help='Case identifier (e.g., case_1, case_2, case_3)')
    
    parser.add_argument('--format', required=True,
                       choices=['json', 'xml', 'html', 'md', 'txt', 'ttl'],
                       help='Data format')
    
    # Configuration flags (when specified, these components are OMITTED)
    parser.add_argument('--one_shot', action='store_true',
                       help='Omit the one-shot example')
    
    parser.add_argument('--partition', action='store_true',
                       help='Omit partition marks (like <example>, <task>, etc.)')
    
    parser.add_argument('--role', action='store_true',
                       help='Omit role prompting')
    
    parser.add_argument('--format_explanation', action='store_true',
                       help='Omit format explanation')
    
    parser.add_argument('--order_change', action='store_true',
                       help='Put questionnaire DATA at the end instead of middle')
    
    # Output options
    parser.add_argument('--output', '-o', 
                       help='Output file path (default: print to stdout)')
    
    parser.add_argument('--export-dir', 
                       default='exported_prompts_cli',
                       help='Directory to export prompts (default: exported_prompts_cli)')
    
    parser.add_argument('--save', action='store_true',
                       help='Save prompt to file instead of printing')
    
    parser.add_argument('--show-config', action='store_true',
                       help='Show configuration details')
    
    return parser


def main():
    """Main CLI function."""
    
    parser = create_parser()
    args = parser.parse_args()
    
    # Create prompt configuration from CLI arguments
    config = PromptConfig(
        include_one_shot=not args.one_shot,          # Flag omits, so invert
        include_partition=not args.partition,        # Flag omits, so invert
        include_role=not args.role,                  # Flag omits, so invert
        include_format=not args.format_explanation,  # Flag omits, so invert
        data_at_end=args.order_change                # Flag enables, so use directly
    )
    
    try:
        # Initialize generator
        generator = ConfigurableAdvancedPromptGenerator()
        
        # Generate the prompt
        prompt_data = generator.generate_configurable_prompt(
            dataset=args.dataset,
            task=args.task,
            case_id=args.case,
            data_format=args.format,
            config=config
        )
        
        # Show configuration if requested
        if args.show_config:
            print("🔧 PROMPT CONFIGURATION:")
            print("=" * 40)
            print(f"✓ One-shot example: {config.include_one_shot}")
            print(f"✓ Partition marks: {config.include_partition}")
            print(f"✓ Role prompting: {config.include_role}")
            print(f"✓ Format explanation: {config.include_format}")
            print(f"✓ Data at end: {config.data_at_end}")
            print("=" * 40)
            print()
        
        # Handle output
        if args.save or args.output:
            # Save to file
            if args.output:
                output_file = Path(args.output)
            else:
                # Auto-generate filename
                config_parts = []
                if not config.include_one_shot:
                    config_parts.append("no_oneshot")
                if not config.include_partition:
                    config_parts.append("no_partition")
                if not config.include_role:
                    config_parts.append("no_role")
                if not config.include_format:
                    config_parts.append("no_format")
                if config.data_at_end:
                    config_parts.append("data_end")
                
                config_name = "_".join(config_parts) if config_parts else "default"
                output_dir = Path(args.export_dir) / args.dataset / args.task / config_name / args.format
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / f"{args.case}.txt"
            
            # Format content for file
            content = []
            content.append("=" * 80)
            content.append(f"GENERATED PROMPT - CLI")
            content.append("=" * 80)
            content.append(f"Dataset: {args.dataset}")
            content.append(f"Task: {args.task}")
            content.append(f"Case: {args.case}")
            content.append(f"Format: {args.format}")
            content.append(f"Expected Answer: {prompt_data['expected_answer']}")
            content.append("")
            content.append("Configuration:")
            content.append(f"• One-shot example: {config.include_one_shot}")
            content.append(f"• Partition marks: {config.include_partition}")
            content.append(f"• Role prompting: {config.include_role}")
            content.append(f"• Format explanation: {config.include_format}")
            content.append(f"• Data at end: {config.data_at_end}")
            content.append("")
            content.append("=" * 80)
            content.append("ASSEMBLED PROMPT")
            content.append("=" * 80)
            content.append("")
            content.append(prompt_data['prompt'])
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))
            
            print(f"✅ Prompt saved to: {output_file}")
            
        else:
            # Print to stdout
            print("=" * 80)
            print("GENERATED PROMPT")
            print("=" * 80)
            print()
            print(prompt_data['prompt'])
            print()
            print("=" * 80)
            print(f"Expected Answer: {prompt_data['expected_answer']}")
            print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 