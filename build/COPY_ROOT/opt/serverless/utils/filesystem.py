import glob
import magic
import mimetypes

class Filesystem:
    def __init__(self):
        pass

    @staticmethod
    def find_input_file(directory, str_hash):
      # Hashed url should have only one result
      try:
          matched = glob.glob(f'{directory}/{str_hash}*')
          if len(matched) > 0:
              return matched[0]
          return None
      except:
          return None
          
    @staticmethod
    def get_file_extension(filepath):
        mime_str = magic.from_file(filepath, mime=True)
        return mimetypes.guess_extension(mime_str)
        