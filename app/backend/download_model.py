#!/usr/bin/env python3
"""
Script to download the sentence transformer model locally for offline deployment.
Run this script in an environment with internet access before deployment.
"""

import os
import sys
from sentence_transformers import SentenceTransformer

def download_model():
    """Download the sentence transformer model to local directory."""
    model_name = 'all-MiniLM-L6-v2'
    local_model_path = os.path.join(os.path.dirname(__file__), 'models', model_name)
    
    print(f"📥 Downloading model '{model_name}' to {local_model_path}...")
    
    try:
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(local_model_path), exist_ok=True)
        
        # Download the model
        model = SentenceTransformer(model_name)
        
        # Save the model locally
        model.save(local_model_path)
        
        print(f"✅ Model successfully downloaded to: {local_model_path}")
        print(f"📁 Model size: {get_directory_size(local_model_path):.2f} MB")
        
        # Test the model to ensure it works
        print("🧪 Testing model...")
        test_text = ["This is a test sentence for model verification."]
        embeddings = model.encode(test_text)
        print(f"✅ Model test successful. Embedding shape: {embeddings.shape}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        return False

def get_directory_size(path):
    """Calculate directory size in MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)  # Convert to MB

def verify_model_exists():
    """Verify that the model exists locally."""
    model_name = 'all-MiniLM-L6-v2'
    local_model_path = os.path.join(os.path.dirname(__file__), 'models', model_name)
    
    if os.path.exists(local_model_path):
        print(f"✅ Model exists at: {local_model_path}")
        try:
            model = SentenceTransformer(local_model_path)
            test_embeddings = model.encode(["test"])
            print(f"✅ Model is functional. Embedding shape: {test_embeddings.shape}")
            return True
        except Exception as e:
            print(f"❌ Model exists but is not functional: {e}")
            return False
    else:
        print(f"❌ Model not found at: {local_model_path}")
        return False

if __name__ == "__main__":
    print("🤖 Sentence Transformer Model Downloader")
    print("=" * 50)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verify":
        verify_model_exists()
    else:
        if download_model():
            print("\n🎉 Model download completed successfully!")
            print("💡 You can now deploy the application without internet access.")
            print("💡 Run with --verify flag to check if model exists and works.")
        else:
            print("\n❌ Model download failed.")
            sys.exit(1)
