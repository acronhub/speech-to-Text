class Config(object):
  DEBUG = False
  TESTING = False
  UPLOAD_FOLDER = './uploads'
  OUTPUT_FOLDER = './outputs'
  GCS_BUCKET_NAME = 'example-bucket'

  ALLOWED_EXTENSIONS = ['mp4', 'm4a', 'mp3', 'wav']
  SELECTED_HERTZ = [48000, 44100, 22100,]
  SELECTED_CHANNEL = [1, 2, 4,]
  SELECTED_PHRASES = []

class ProductionConfig(Config):
  DEBUG = False

class DevelopmentConfig(Config):
  DEBUG = True

class TestingConfig(Config):
  TESTING = True
