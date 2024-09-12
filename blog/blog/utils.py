import uuid
import os
import requests
import datetime
import calendar
import json

from io import BytesIO
from PIL import Image
from uuid import uuid4
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework.pagination import PageNumberPagination
from django.core.files.base import ContentFile
from django.utils.deconstruct import deconstructible


@deconstructible
class UploadToClass(object):
    def __init__(self, sub_path):
        self.path = sub_path
        
    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.path, filename)
    

def upload_to(path):
    return UploadToClass(path)

def change_size(image):
    img_io = BytesIO()
    im = Image.open(image).convert('RGB')
    if im.height > 1920 or im.width > 1080:
        im.thumbnail((1920,1080))
    im.save(img_io, format='JPEG')
    name = image.path.split('.')[0] + '.jpg'
    image.close()
    return ContentFile(img_io.getvalue(), name)

def my_custom_upload_to_func(instance, filename):
    ext = filename.split(".")[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return os.path.join("uploads_summernote", filename)

def check_recaptcha(request):
    if (
        request.method == "POST"
        or request.method == "PATCH"
        or request.method == "DELETE"
    ):
        # API or classic request
        recaptcha_response = request.POST.get(
            "g_recaptcha_response"
        ) or request.data.get("g_recaptcha_response")

        data = {
            "secret": settings.GOOGLE_RECAPTCHA_PRIVATE_KEY,
            "response": recaptcha_response,
        }
        r = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
        result = r.json()
        if result["success"]:
            request.recaptcha_is_valid = True
        else:
            request.recaptcha_is_valid = False

    return request


def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)

# Router is not working with types params in url_path
def custom_get_object_or_404(Query, **kwargs):
    try:
        return get_object_or_404(Query, **kwargs)
    except ValueError as e:
        raise Http404()
    
def get_request_data(request_data):
    if request_data.__class__.__name__ == 'QueryDict':
        # QueryDict not working with nested serializers (AnswerSerilaizer)
        data = request_data.dict()
        try:
            data["answers_set"] = json.loads(data["answers_set"])
        except (json.JSONDecodeError, KeyError):
            pass
    else:
        data = request_data
    
    return data

def set_deleted_photos(request_data):
    if request_data.get('deleted_photos_set') and type(request_data['deleted_photos_set']) is str:
        try:
            request_data['deleted_photos_set'] = json.loads(request_data['deleted_photos_set'])
        except (json.JSONDecodeError, KeyError):
            pass
    return request_data

def set_files_data(request_data, files):
    try:
        files_list = files.getlist('photos_set')
        if files_list:
            files_dict = []
            for file in files_list:
                files_dict.append({'photo': file})
            request_data['photos_set'] = files_dict
    except Exception as e:
        pass
    return request_data

def set_language_to_user(request):
    if not hasattr(request.user, 'language'):
        request.user.language = 'any'
    return request


class MyPagination(PageNumberPagination):
    page_size = 5
    max_page_size = 1000