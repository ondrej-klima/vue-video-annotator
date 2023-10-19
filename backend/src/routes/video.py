import mimetypes
import os
import re
from typing import List, Dict
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse


router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)


@router.get('/')
def get_video_stream(request: Request):
    """ Returns coco of image and annotations """

    # check video and format
    path = "out.mp4"
    BUFF_SIZE = 1024 * 1024
    file_size = os.path.getsize(path)

    range = request.headers.get('Range')
    start = 0
    end = file_size - 1
    if range is not None:
        m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
        if m:
            start = int(m.group('start'))
            if m.group('end') is not None:
                end = int(m.group('end'))

    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)

    return StreamingResponse(
        chunk_generator(path, BUFF_SIZE, start, end - start + 1),
        headers={
            "Accept-Ranges": "bytes",
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Content-Type": mimetypes.guess_type(path)[0]
        },
        status_code=206
    )


def chunk_generator(path, chunk_size, start, size):
    with open(path, 'rb') as fd:
        bytes_read = 0
        fd.seek(start)
        while bytes_read < size:
            bytes_to_read = min(chunk_size,
                                size - bytes_read)
            yield fd.read(bytes_to_read)
            bytes_read = bytes_read + bytes_to_read
