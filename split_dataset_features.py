#!/usr/bin/env python3
import json
import os

def split_dataset_features():
    """Split dataset_features.json into separate files for each dataset."""
    
    # Read the main dataset_features.json file
    input_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/dataset_features.json"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            all_features = json.load(f)
    except FileNotFoundError:
        print(f"Error: {input_file} not found!")
        return
    except Exception as e:
        print(f"Error reading {input_file}: {e}")
        return
    
    print("Splitting dataset_features.json into individual files...")
    print("=" * 60)
    
    # Create individual JSON files for each dataset
    base_dir = "/insight-fast/dnguyen/Q_Benchmark/questions_design"
    
    for dataset_name, features in all_features.items():
        # Create the output file path
        output_dir = os.path.join(base_dir, dataset_name)
        output_file = os.path.join(output_dir, f"{dataset_name}_features.json")
        
        # Create the dataset-specific JSON structure
        dataset_data = {
            "dataset_name": dataset_name,
            "feature_count": len(features),
            "features": features
        }
        
        # Write to individual file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Created: {dataset_name}/{dataset_name}_features.json")
            print(f"  Features: {len(features)}")
            
        except Exception as e:
            print(f"✗ Error creating {output_file}: {e}")
    
    print("\n" + "=" * 60)
    print("Split operation completed!")
    
    # Verify all files were created
    print("\nVerification:")
    for dataset_name in all_features.keys():
        output_file = os.path.join(base_dir, dataset_name, f"{dataset_name}_features.json")
        if os.path.exists(output_file):
            print(f"✓ {dataset_name}_features.json exists")
        else:
            print(f"✗ {dataset_name}_features.json missing")

if __name__ == "__main__":
    split_dataset_features()