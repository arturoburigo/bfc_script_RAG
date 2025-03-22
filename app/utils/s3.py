import boto3
import botocore
import os
from dotenv import find_dotenv, load_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

def download_s3_file(bucket_name, object_key, folder_path=None):    
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name='us-east-1'
    )
    
    file_name = os.path.basename(object_key)
    
    if folder_path:
        os.makedirs(folder_path, exist_ok=True)
        local_path = os.path.join(folder_path, file_name)
    else:
        local_path = file_name
    
    try:
        s3_client.download_file(bucket_name, object_key, local_path)
        return True, local_path
    except botocore.exceptions.ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        if error_code == '403':
            print(f"Erro: Permissão negada (403 Forbidden). Você não tem permissão para acessar este objeto.")
            print("Verifique suas permissões IAM e as políticas do bucket.")
        elif error_code == '404':
            print(f"Erro: Objeto não encontrado (404). Verifique se o bucket e o caminho do objeto estão corretos.")
        else:
            print(f"Erro ao baixar arquivo: {e}")
        return False, None
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False, None

def batch_download_s3_files(bucket_name, file_mappings):
    """
    Baixa múltiplos arquivos do S3 de acordo com um mapeamento.
    
    Args:
        bucket_name (str): Nome do bucket S3
        file_mappings (list): Lista de dicionários contendo 'object_key' e 'folder_path'
    
    Returns:
        dict: Dicionário com resultados para cada arquivo
    """
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

# Exemplo de uso
if __name__ == "__main__":
    bucket_name = "bfc-scripts-docs"
    file_mappings = [
        {
            'object_key': "chunks_embedded/documentation_chunks_with_embeddings.json",
            'folder_path': "../core/docs"
        },
    ]
    
    results = batch_download_s3_files(bucket_name, file_mappings)
    
    print("\nResumo dos downloads:")
    for object_key, result in results.items():
        status = "Sucesso" if result['success'] else "Falha"
        print(f"{object_key}: {status}")
        if result['success']:
            print(f"  → Salvo em: {result['file_path']}")