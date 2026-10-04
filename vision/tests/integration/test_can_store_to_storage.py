from src.infrastructure.gcs_adapter import GoogleCloudStorageAdapter



def can_store_to_storage() -> None:
    gcs_adapter = GoogleCloudStorageAdapter()
    
