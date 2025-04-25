import boto3
import botocore
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

def download_s3_file(bucket_name, object_key, folder_path):
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1'
    )
    
    file_name = os.path.basename(object_key)
    
    if not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Destination directory does not exist: {folder_path}")
    
    local_path = os.path.join(folder_path, file_name)

    try:
        s3_client.download_file(bucket_name, object_key, local_path)
        return True, local_path
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == '403':
            print(f"Error: Permission denied (403 Forbidden). Please check your IAM permissions and bucket policies.")
        elif error_code == '404':
            print(f"Error: Object not found (404). Please verify the bucket and object path.")
        else:
            print(f"Error downloading file: {e}")
        return False, None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False, None

def batch_download_s3_files(bucket_name, file_mappings):
    results = {}
    
    for mapping in file_mappings:
        object_key = mapping['object_key']
        folder_path = mapping['folder_path']

        success, file_path = download_s3_file(bucket_name, object_key, folder_path)

        results[object_key] = {
            'success': success,
            'file_path': file_path
        }
    
    return results

if __name__ == "__main__":
    # Absolute path to 'bfc_script_RAG/app/core/docs'
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "core", "docs"))

    if not os.path.isdir(base_dir):
        raise FileNotFoundError(f"Expected directory does not exist: {base_dir}")

    bucket_name = "bfc-scripts-docs"
    file_mappings = [
        {
            'object_key': "chunks_embedded/documentation_chunks_with_embeddings.json",
            'folder_path': base_dir  # Correct directory without creating new subfolders
        },
    ]

    results = batch_download_s3_files(bucket_name, file_mappings)

    print("\nDownload Summary:")
    for object_key, result in results.items():
        status = "Success" if result['success'] else "Failed"
        print(f"{object_key}: {status}")
        if result['success']:
            print(f"  → Saved at: {result['file_path']}")