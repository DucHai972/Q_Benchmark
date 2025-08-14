#!/usr/bin/env python3
import json

def extract_detailed_features():
    """Extract detailed features including sub-features for mental health dataset."""
    
    # Read the original JSON data to get the complete structure
    json_file = "/insight-fast/dnguyen/Q_Benchmark/preprocessed_data/self-reported-mental-health-college-students-2022/mental_health_questionnaire.json"
    
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {json_file}: {e}")
        return
    
    questions = data.get("questions", {})
    
    # Build detailed feature structure
    detailed_features = []
    simple_features = []
    
    # Add respondent (always first)
    simple_features.append("respondent")
    detailed_features.append({
        "name": "respondent",
        "type": "identifier",
        "sub_features": None
    })
    
    for main_feature, content in questions.items():
        simple_features.append(main_feature)
        
        if isinstance(content, dict) and "sub_questions" in content:
            # This is a hierarchical feature with sub-features
            sub_feature_names = list(content["sub_questions"].keys())
            detailed_features.append({
                "name": main_feature,
                "type": "hierarchical",
                "base_question": content.get("base_question", ""),
                "sub_features": sub_feature_names,
                "sub_feature_count": len(sub_feature_names)
            })
            
            # Add each sub-feature to simple list for backward compatibility
            for sub_name in sub_feature_names:
                simple_features.append(f"{main_feature}.{sub_name}")
                
        else:
            # This is a simple feature
            detailed_features.append({
                "name": main_feature,
                "type": "simple",
                "question": content if isinstance(content, str) else "",
                "sub_features": None
            })
    
    # Create the comprehensive feature data
    feature_data = {
        "dataset_name": "self-reported-mental-health-college-students-2022",
        "directory_name": "self-reported-mental-health",
        "feature_count": len(simple_features),
        "simple_features": simple_features,
        "detailed_features": detailed_features,
        "hierarchical_feature_count": len([f for f in detailed_features if f["type"] == "hierarchical"]),
        "simple_feature_count": len([f for f in detailed_features if f["type"] == "simple"]),
        "total_sub_features": sum(len(f.get("sub_features", [])) for f in detailed_features if f.get("sub_features"))
    }
    
    # Write the updated file
    output_file = "/insight-fast/dnguyen/Q_Benchmark/questions_design/self-reported-mental-health/self-reported-mental-health_features.json"
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(feature_data, f, indent=2, ensure_ascii=False)
        
        print("Updated self-reported-mental-health_features.json with detailed structure")
        print("=" * 70)
        print(f"Total features: {feature_data['feature_count']}")
        print(f"Simple features: {feature_data['simple_feature_count']}")
        print(f"Hierarchical features: {feature_data['hierarchical_feature_count']}")
        print(f"Total sub-features: {feature_data['total_sub_features']}")
        
        print("\nHierarchical features:")
        for feature in detailed_features:
            if feature["type"] == "hierarchical":
                print(f"  {feature['name']}: {len(feature['sub_features'])} sub-features")
                for sub in feature['sub_features']:
                    print(f"    - {sub}")
        
    except Exception as e:
        print(f"Error writing to {output_file}: {e}")

if __name__ == "__main__":
    extract_detailed_features()