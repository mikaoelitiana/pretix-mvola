from django.urls import include, re_path

from .views import callback

event_patterns = [
    re_path(
        r"^mvola/",
        include(
            [
                re_path(r"^callback/$", callback, name="callback"),
            ]
        ),
    ),
]
