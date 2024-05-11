import boto3
import time
import cv2

tmp = '/tmp/'

FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 2

def s3_connection():
    s3 = boto3.client(
        service_name="",
        region_name="",
        aws_access_key_id="",
        aws_secret_access_key="",
    )
    return s3

def s3_put_video(s3, bucket, filepath, access_key):
    s3.upload_file(
        Filename=filepath,
        Bucket=bucket,
        Key=access_key
    )

def s3_get_video(s3, bucket, filepath, access_key):
    s3.download_file(
        Filename=filepath,
        Bucket=bucket,
        Key=access_key
    )

def video_processing(object_key, video_path):
    file_name = object_key.split(".")[FILE_NAME_INDEX]
    result_file_path = tmp+file_name+'-output.avi'

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height))

    start = time.time()
    while video.isOpened():
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tmp_file_path = tmp+'tmp.jpg'
            cv2.imwrite(tmp_file_path, gray_frame)
            gray_frame = cv2.imread(tmp_file_path)
            out.write(gray_frame)
        else:
            break

    latency = time.time() - start

    video.release()
    out.release()
    return latency, result_file_path

s3 = s3_connection()

def main(args):
    download_key = args.get("file", "earth.mp4")
    filepath = '/tmp/'+download_key

    s3_get_video(s3, '', filepath, download_key)

    startTime = time.time()
    video_processing_latency, upload_key = video_processing(download_key, filepath)
    t8 = time.time()

    s3_put_video(s3, '', filepath, upload_key)

    return {"startTime": startTime, "functionTime": t8-startTime, "latency": video_processing_latency}
