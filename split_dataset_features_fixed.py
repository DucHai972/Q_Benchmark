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
    
    # Map JSON dataset names to directory names
    dataset_mapping = {
        "healthcare-dataset": "healthcare-dataset",
        "isbar": "isbar", 
        "self-reported-mental-health-college-students-2022": "self-reported-mental-health",
        "stack-overflow-2022-developer-survey": "stack-overflow-2022",
        "sus-uta7": "sus-uta7"
    }
    
    print("Splitting dataset_features.json into individual files...")
    print("=" * 60)
    
    # Create individual JSON files for each dataset
    base_dir = "/insight-fast/dnguyen/Q_Benchmark/questions_design"
    
    for json_dataset_name, features in all_features.items():
        # Get the corresponding directory name
        dir_name = dataset_mapping.get(json_dataset_name, json_dataset_name)
        
        # Create the output file path
        output_dir = os.path.join(base_dir, dir_name)
        output_file = os.path.join(output_dir, f"{dir_name}_features.json")
        
        # Create the dataset-specific JSON structure
        dataset_data = {
            "dataset_name": json_dataset_name,
            "directory_name": dir_name,
            "feature_count": len(features),
            "features": features
        }
        
        # Write to individual file
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(dataset_data, f, indent=2, ensure_ascii=False)
            
            print(f"✓ Created: {dir_name}/{dir_name}_features.json")
            print(f"  Original name: {json_dataset_name}")
            print(f"  Features: {len(features)}")
            
        except Exception as e:
            print(f"✗ Error creating {output_file}: {e}")
    
    print("\n" + "=" * 60)
    print("Split operation completed!")
    
    # Verify all files were created
    print("\nVerification:")
    for json_dataset_name in all_features.keys():
        dir_name = dataset_mapping.get(json_dataset_name, json_dataset_name)
        output_file = os.path.join(base_dir, dir_name, f"{dir_name}_features.json")
        if os.path.exists(output_file):
            print(f"✓ {dir_name}_features.json exists")
        else:
            print(f"✗ {dir_name}_features.json missing")

if __name__ == "__main__":
    split_dataset_features()