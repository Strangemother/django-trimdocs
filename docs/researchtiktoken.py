"""An example of caching tiktoken data, so I can count tokens offline.
"""
import tiktoken

import hashlib
from pathlib import Path
import shutil
import os

# from tiktoken_ext 
blobs = (
    # uri (blobpath), expected hash (unrequired)
("https://openaipublic.blob.core.windows.net/encodings/r50k_base.tiktoken",
    "306cd27f03c1a714eca7108e03d66b7dc042abe8c258b44c199a7ed9838dd930",),
("https://openaipublic.blob.core.windows.net/encodings/p50k_base.tiktoken",
    "94b5ca7dff4d00767bc256fdd1b27e5b17361d7b8a5f968547f9f23eb70d2069",),
("https://openaipublic.blob.core.windows.net/encodings/p50k_base.tiktoken",
    "94b5ca7dff4d00767bc256fdd1b27e5b17361d7b8a5f968547f9f23eb70d2069",),
("https://openaipublic.blob.core.windows.net/encodings/cl100k_base.tiktoken",
    "223921b76ee99bde995b7ff738513eef100fb51d18c93597a113bcffe865b2a7",),
("https://openaipublic.blob.core.windows.net/encodings/o200k_base.tiktoken",
    "446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d",),
)

DIR = Path("./tiktoken_cache").absolute()
os.environ["TIKTOKEN_CACHE_DIR"] = str(DIR.absolute())


for blobpath, expected in blobs:
    cache_key = hashlib.sha1(blobpath.encode()).hexdigest()
    filename = Path(blobpath).name
    new_filename = cache_key
    shutil.copyfile(dir_path / filename, DIR / new_filename)
    print(filename, ': ', cache_key)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens
