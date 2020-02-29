from django.http import JsonResponse


def resp(code=200, msg='success', **kwargs):
    return JsonResponse({'code': code, 'msg': msg, **kwargs})
