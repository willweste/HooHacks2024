import boto3
import os
from botocore.exceptions import ClientError

def collection_exists(collection_id):
    rekognition_client = boto3.client('rekognition')

    try:
        response = rekognition_client.describe_collection(CollectionId=collection_id)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        else:
            raise e

def create_collection(collection_id):
    rekognition_client = boto3.client('rekognition')

    if not collection_exists(collection_id):
        try:
            response = rekognition_client.create_collection(CollectionId=collection_id)
            print(f"Collection {collection_id} created successfully. Status code: {response['StatusCode']}")
        except ClientError as e:
            print(f"Error creating collection: {e}")
    else:
        print(f"Collection {collection_id} already exists.")

def index_faces(collection_id, users_folder):
    rekognition_client = boto3.client('rekognition')

    for image_filename in os.listdir(users_folder):
        if image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(users_folder, image_filename)
            with open(image_path, 'rb') as image_file:
                try:
                    response = rekognition_client.index_faces(
                        CollectionId=collection_id,
                        Image={'Bytes': image_file.read()},
                        ExternalImageId=os.path.splitext(image_filename)[0],  # Use the filename without extension as ExternalImageId
                        DetectionAttributes=['ALL']
                    )
                    face_records = response['FaceRecords']
                    print(f"Faces indexed for {image_filename}: {len(face_records)} face(s) detected.")
                except ClientError as e:
                    print(f"Error indexing faces for {image_filename}: {e}")

def check_faces_indexed(collection_id, users_folder):
    rekognition_client = boto3.client('rekognition')

    try:
        response = rekognition_client.list_faces(CollectionId=collection_id)
        indexed_faces_count = len(response['Faces'])
        image_count = sum(1 for _ in os.listdir(users_folder) if _.lower().endswith(('.png', '.jpg', '.jpeg')))
        return indexed_faces_count >= image_count
    except ClientError as e:
        print(f"Error checking indexed faces: {e}")
        return False