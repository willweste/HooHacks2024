import boto3
import os
from flask import current_app
from rekognition_utils import create_collection, index_faces, collection_exists, check_faces_indexed
import cv2
from botocore.exceptions import ClientError
from app.models import User

COLLECTION_ID = "users_collection"

def perform_facial_recognition(frame):
    rekognition_client = boto3.client('rekognition')

    # Ensure the collection exists
    create_collection(COLLECTION_ID)

    # Get all users from the database
    users = User.query.all()

    # Index the faces from the database
    for user in users:
        try:
            response = rekognition_client.index_faces(
                CollectionId=COLLECTION_ID,
                Image={'Bytes': user.image_data},
                ExternalImageId=str(user.id),
                DetectionAttributes=['ALL']
            )
            face_records = response['FaceRecords']
            print(f"Faces indexed for user {user.username}: {len(face_records)} face(s) detected.")
        except ClientError as e:
            print(f"Error indexing faces for user {user.username}: {e}")

    # Perform facial recognition on the captured frame
    _, buffer = cv2.imencode('.jpg', frame)
    try:
        search_response = rekognition_client.search_faces_by_image(
            CollectionId=COLLECTION_ID,
            Image={'Bytes': buffer.tobytes()},
            MaxFaces=1,
            FaceMatchThreshold=80
        )

        if search_response['FaceMatches']:
            recognized_user_id = search_response['FaceMatches'][0]['Face']['ExternalImageId']
            recognized_user = User.query.get(int(recognized_user_id))
            print(f"Recognized user: {recognized_user.username}")
            return recognized_user.id
        else:
            print("Unknown user detected")
            return None

    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterException':
            print("No faces detected in the image")
        else:
            raise e

    return None