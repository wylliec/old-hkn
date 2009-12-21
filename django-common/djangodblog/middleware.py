import traceback
import socket
import warnings
import logging
import hashlib

from django.conf import settings
from django.http import Http404
from djangodblog.models import Error, ErrorBatch

__all__ = ('DBLogMiddleware', 'DBLOG_CATCH_404_ERRORS')

DBLOG_CATCH_404_ERRORS = getattr(settings, 'DBLOG_CATCH_404_ERRORS', False)

class DBLogMiddleware(object):
    def process_response(self, request, response):
        agent = request.META.get('HTTP_USER_AGENT', '<none>')
        for crawler in ("msnbot", "Yahoo!", "Googlebot", "crawler", "Crawler", "Baiduspider"):
            if agent.find(crawler) != -1:
                return response

        if not hasattr(request, 'session'):
            identifier = "<none>"
        elif request.user.is_authenticated():
            identifier =  "%s:%s" % (request.META.get('REMOTE_ADDR', '<none>'), request.user.username)
        else:
            identifier =  "%s:%s" % (request.META.get('REMOTE_ADDR', '<none>'), request.session._session_key)

        message = "[%s] [%s] [%d] %s" %  (identifier, agent, response.status_code, request.get_full_path())
        logging.getLogger('special.access').info(message)
        if response.status_code == 404:
            message = "[%s] [%s] [%s] %s" %  (identifier, agent, request.META.get('REFERRER', '<none>'), request.get_full_path())
            logging.getLogger('special.404').warning(message)
        return response


    def process_exception(self, request, exception):
        if isinstance(exception, Http404):
            message = "[%s] [%s] [%s] %s [%s]" %  (request.META.get('REMOTE_ADDR', '<none>'), request.META.get('HTTP_USER_AGENT', '<none>'), request.META.get('REFERRER', '<none>'), request.get_full_path(), unicode(exception))
            logging.getLogger('special.404').warning(message)
        if not DBLOG_CATCH_404_ERRORS and isinstance(exception, Http404):
            return
        server_name = socket.gethostname()
        tb_text     = traceback.format_exc()
        class_name  = exception.__class__.__name__
        checksum    = hashlib.md5(tb_text).hexdigest()
        logging.getLogger("special.exceptions").error("at %s: %s\n%s" % (request.path, getattr(exception, 'message', ''), tb_text))

        defaults = dict(
            class_name  = class_name,
            message     = getattr(exception, 'message', ''),
            url         = request.build_absolute_uri(),
            server_name = server_name,
            traceback   = tb_text,
        )

        try:
            Error.objects.create(**defaults)
            batch, created = ErrorBatch.objects.get_or_create(
                class_name = class_name,
                server_name = server_name,
                checksum = checksum,
                defaults = defaults
            )
            if not created:
                batch.times_seen += 1
                batch.resolved = False
                batch.save()
        except Exception, exc:
            logging.getLogger("special.exceptions").critical("DBLog Error:\n%s" % traceback.format_exc())
            warnings.warn(unicode(exc))
