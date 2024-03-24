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


def index_faces(collection_id, user_image_data, external_image_id):
    rekognition_client = boto3.client('rekognition')

    try:
        response = rekognition_client.index_faces(
            CollectionId=collection_id,
            Image={'Bytes': user_image_data},
            ExternalImageId=external_image_id,
            DetectionAttributes=['ALL']
        )
        face_records = response['FaceRecords']
        print(f"Faces indexed for {external_image_id}: {len(face_records)} face(s) detected.")
    except ClientError as e:
        print(f"Error indexing faces for {external_image_id}: {e}")


def check_faces_indexed(collection_id):
    rekognition_client = boto3.client('rekognition')

    try:
        response = rekognition_client.list_faces(CollectionId=collection_id)
        return len(response['Faces']) > 0
    except ClientError as e:
        print(f"Error checking indexed faces: {e}")
        return False