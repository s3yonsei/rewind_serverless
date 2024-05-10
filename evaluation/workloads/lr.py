import boto3
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import pandas as pd
import time
import os
import re

tmp = '/tmp/'
cleanup_re = re.compile('[^a-z]+')

def s3_connection():
    s3 = boto3.client(
        service_name="",
        region_name="",
        aws_access_key_id="",
        aws_secret_access_key="",
    )
    return s3

def s3_get_object(s3, bucket, filepath, access_key):
    s3.download_file(
        Filename=filepath,
        Bucket=bucket,
        Key=access_key
    )

def cleanup(sentence):
    sentence = sentence.lower()
    sentence = cleanup_re.sub(' ', sentence).strip()
    return sentence

s3 = s3_connection()

def main(args):
    x = args.get("x", "The ambiance is magical. The food and service was nice! The lobster and cheese was to die for and our steaks were cooked perfectly.")
    dataset_object_key = args.get("dataset_object_key", "lrserve10mb.csv")
    model_object_key = args.get("model_object_key", "lr_model.pk")  # example : lr_model.pk

    model_path = tmp + model_object_key
    s3_get_object(s3, '', model_path, model_object_key)

    dataset_path = tmp + dataset_object_key
    s3_get_object(s3, '', dataset_path, dataset_object_key)

    startTime = time.time()
    dataset = pd.read_csv(dataset_path)

    df_input = pd.DataFrame()
    df_input['x'] = [x]
    df_input['x'] = df_input['x'].apply(cleanup)

    dataset['train'] = dataset['Text'].apply(cleanup)

    tfidf_vect = TfidfVectorizer(min_df=100).fit(dataset['train'])

    X = tfidf_vect.transform(df_input['x'])

    model = joblib.load(model_path)
    y = list(model.predict(X))

    os.remove(dataset_path)
    os.remove(model_path)

    t8 = time.time()

    return {"startTime": startTime, "functionTime": t8-startTime}

