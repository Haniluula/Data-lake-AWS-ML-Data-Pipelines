import json
import boto3
from datetime import datetime
dynamodb=boto3.resource('dynamodb')
table = dynamodb.Table('imageData-table-cv')
s3 = boto3.resource('s3')
cv_client = boto3.client('rekognition')
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    img_filename = event['Records'][0]['s3']['object']['key']
    s3_obj = s3.Object(bucket_name, img_filename)
    s3_image = s3_obj.get()['Body'].read()
    cv_response = cv_client.detect_text(Image={'Bytes': s3_image})
    print('CV Rekognition response:')
    print(cv_response)
    all_txt_info = []
    for txt in cv_response['TextDetections']:
        detected_txt = txt['DetectedText']
        all_txt_info.append(detected_txt)
    final_text = " | ".join(all_txt_info)
    print('Detected text:')
    print(final_text)
    now = datetime.utcnow().isoformat()
    dynamodb_response = table.put_item(Item={'img_filename': img_filename,
                                             'insert_timestamp': now,
                                             'detected_text': final_text})
    print('All done!')
    return dynamodb_response