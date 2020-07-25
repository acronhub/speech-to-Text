from flask import Flask, jsonify, request, render_template, redirect, make_response
from google.cloud import storage
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types

import os
import ffmpeg
import codecs
import datetime

from app import app

@app.route('/')
def index():
    return render_template(
        'index.html',
        select_blobs=list_gcs(),
        select_hertz=set(app.config['SELECTED_HERTZ']),
        select_channels=set(app.config['SELECTED_CHANNEL'])
    )

@app.route('/upload', methods=['POST'])
def uploads_file():
    if 'uploadFile' not in request.files:
        make_response(jsonify({'result':'uploadFile is required.'}))

    file = request.files['uploadFile']
    filename = file.filename

    if filename == '':
        make_response(jsonify({'result':'filename must not empty.'}))

    if file and allwed_file(filename):
        filepath, filename = convert_wav(file, filename)
        upload_gcs(filepath, filename)
        return redirect("/")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    gcs_uri = os.path.join("gs://", app.config['GCS_BUCKET_NAME'], request.form.get('filename'))
    transcribe_gcs(gcs_uri, request.form.get('hertz'), request.form.get('channel'))
    return redirect("/")

# .があるかどうかのチェックと、拡張子の確認
def allwed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# WAVファイルのコンバート
def convert_wav(file, filename):
    inputfilepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    outputfile = filename.rsplit('.', 1)[0].lower()
    today = datetime.datetime.today().strftime("%Y%m%d-%H%M%S")
    outputfilename = '{0}-{1}.flac'.format(today, outputfile)
    outputfilepath = os.path.join(app.config['UPLOAD_FOLDER'], outputfilename)

    # ファイルの保存
    file.save(inputfilepath)

    # WAVファイル変換＆保存
    stream = ffmpeg.input(inputfilepath)
    stream = ffmpeg.output(stream, outputfilepath)
    ffmpeg.run(stream)

    os.remove(inputfilepath)

    return outputfilepath, outputfilename

# 文字起こし
def transcribe_gcs(gcs_uri, hertz, channel):
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.FLAC, # flacの設定
        sample_rate_hertz=int(hertz), # ヘルツは音声ファイルに合わせる
        audio_channel_count = int(channel),
        language_code='ja-JP', # 日本語音声の場合
        enable_speaker_diarization=True, # 異なる話者の分離
        enable_automatic_punctuation=True, # 句読点
        speech_contexts=app.config['SELECTED_PHRASES'] # 音声適応ブースト
    )
    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    operationResult = operation.result()

    filename = gcs_uri.rsplit('/', 1)[1].split('.')[0] + ".txt"
    outputfilepath = os.path.join(app.config['OUTPUT_FOLDER'], filename)
    fout = codecs.open(outputfilepath, 'a', 'utf-8')
    for result in operationResult.results:
        for alternative in result.alternatives:
            fout.write(u'{}\n'.format(alternative.transcript))
    fout.close()

# GCS ファイル取得
def list_gcs():
    storage_client = storage.Client()
    blobs = storage_client.list_blobs(app.config['GCS_BUCKET_NAME'])
    return blobs

# GCS ファイルアップロード
def upload_gcs(filepath, filename):
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(app.config['GCS_BUCKET_NAME'])
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename=filepath)
    os.remove(filepath)
