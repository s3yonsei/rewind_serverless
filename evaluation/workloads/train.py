import boto3

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

import pandas as pd
import time
import re
import io

cleanup_re = re.compile('[^a-z]+')
tmp = '/tmp/'

def s3_connection():
    s3 = boto3.client(
        service_name="",
        region_name="",
        aws_access_key_id="",
        aws_secret_access_key="",
    )
    return s3

def s3_put_object(s3, bucket, filepath, access_key):
    s3.upload_file(
        Filename=filepath,
        Bucket=bucket,
        Key=access_key
    )

def s3_get_object(s3, bucket, access_key):
    obj = s3.get_object(
        Bucket=bucket,
        Key=access_key
    )
    return obj

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

s3 = s3_connection()

def main(args):
    download_key = args.get("model", "lrtrain10mb.csv")
    filepath = '/tmp/'+download_key

    obj = s3_get_object(s3, '', download_key)

    startTime = time.time()
    df = pd.read_csv(io.BytesIO(obj['Body'].read()))
    df['train'] = df['Text'].apply(cleanup)
    tfidf_vector = TfidfVectorizer(min_df=100).fit(df['train'])
    train = tfidf_vector.transform(df['train'])

    model = LogisticRegression()
    model.fit(train, df['Score'])

    model_file_path = tmp + 'lr_model.pk'
    joblib.dump(model, model_file_path)
    t8 = time.time()

    upload_key = "lr_model.pk"
    s3_put_object(s3, 'rewind-serverless', model_file_path, upload_key)

    return {"startTime": startTime, "functionTime": t8-startTime}

