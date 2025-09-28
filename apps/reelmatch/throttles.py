# reelmatch/throttles.py
from rest_framework.throttling import SimpleRateThrottle

class TMDBRateThrottle(SimpleRateThrottle):
    """
    Custom throttle for endpoints that call the TMDb API.
    Ensures we don't exceed TMDb's rate limits by restricting
    how often users can hit these views.
    """
    scope = "tmdb"

    def get_cache_key(self, request, view):
        """
        Create a unique cache key per user (if authenticated)
        or per IP address (if anonymous).
        """
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)

        return self.cache_format % {
            "scope": self.scope,
            "ident": ident
        }
