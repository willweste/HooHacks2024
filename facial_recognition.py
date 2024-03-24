import boto3
import os
from flask import current_app
from rekognition_utils import create_collection, index_faces, collection_exists, check_faces_indexed
import cv2
from botocore.exceptions import ClientError
COLLECTION_ID = "users_collection"

def perform_facial_recognition(username, frame):
    user_image_folder = current_app.config["UPLOAD_FOLDER"]
    user_image_path = os.path.join(user_image_folder, f"{username}.jpg")

    if os.path.exists(user_image_path):
        with open(user_image_path, "rb") as image_file:
            user_image_data = image_file.read()

        rekognition_client = boto3.client('rekognition')

        # Create the collection if it doesn't exist
        create_collection(COLLECTION_ID)

        # Index the user's face if not already indexed
        if not collection_exists(COLLECTION_ID) or not check_faces_indexed(COLLECTION_ID):
            index_faces(COLLECTION_ID, user_image_data, username)

        # Save the user's reference image for debugging
        user_ref_image_path = os.path.join(user_image_folder, f"{username}_ref.jpg")
        with open(user_ref_image_path, "wb") as ref_image_file:
            ref_image_file.write(user_image_data)

        # Save the captured frame for debugging
        captured_frame_path = os.path.join(user_image_folder, f"{username}_captured.jpg")
        cv2.imwrite(captured_frame_path, frame)

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