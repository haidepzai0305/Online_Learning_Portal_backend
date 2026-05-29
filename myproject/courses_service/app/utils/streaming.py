import os
import re
from django.http import StreamingHttpResponse

def get_range_response(file_path, request_range, content_type='video/mp4'):
    """
    Handles the Range header and returns a StreamingHttpResponse.
    """
    file_size = os.path.getsize(file_path)
    
    # Parse Range header: bytes=start-end
    range_match = re.match(r'bytes=(\d+)-(\d*)', request_range)
    if not range_match:
        return None
        
    start = int(range_match.group(1))
    end = range_match.group(2)
    end = int(end) if end else file_size - 1
    
    if start >= file_size:
        return None # Should be 416 Requested Range Not Satisfiable
        
    chunk_size = 8192 * 1024 # 8MB chunks or smaller
    content_length = end - start + 1
    
    def file_iterator(path, offset, length):
        with open(path, 'rb') as f:
            f.seek(offset)
            remaining = length
            while remaining > 0:
                to_read = min(remaining, chunk_size)
                data = f.read(to_read)
                if not data:
                    break
                remaining -= len(data)
                yield data

    response = StreamingHttpResponse(
        file_iterator(file_path, start, content_length),
        status=206,
        content_type=content_type
    )
    
    response['Content-Length'] = str(content_length)
    response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
    response['Accept-Ranges'] = 'bytes'
    
    return response
