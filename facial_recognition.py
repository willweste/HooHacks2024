import boto3
import os
from flask import current_app
from rekognition_utils import create_collection, index_faces, collection_exists, check_faces_indexed
import cv2
from botocore.exceptions import ClientError

COLLECTION_ID = "users_collection"

def perform_facial_recognition(frame):
    rekognition_client = boto3.client('rekognition')

    # Ensure the collection exists
    create_collection(COLLECTION_ID)

    # Get the userImages folder path
    user_image_folder = current_app.config["UPLOAD_FOLDER"]

    # Check if faces have already been indexed
    if not check_faces_indexed(COLLECTION_ID, user_image_folder):
        # Index the faces in the userImages folder
        index_faces(COLLECTION_ID, user_image_folder)

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
            print(f"Recognized user: {recognized_user_id}")
            return recognized_user_id
        else:
            print("Unknown user detected")
            return None

    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidParameterException':
            print("No faces detected in the image")
        else:
            raise e

    return None