from django.urls import path

from .views import (ChainView, ExposureView, FundamentalsView, GexAllView,
                    GexView, MacroEventsView, MacroNqView, PriceView, VolSurfaceView)

urlpatterns = [
    path("gex/", GexView.as_view()),
    path("gex/all/", GexAllView.as_view()),
    path("exposure/", ExposureView.as_view()),
    path("chain/", ChainView.as_view()),
    path("oi/", ChainView.as_view()),
    path("vol/surface/", VolSurfaceView.as_view()),
    path("macro/nq-bias/", MacroNqView.as_view()),
    path("macro/events/", MacroEventsView.as_view()),
    path("fundamentals/", FundamentalsView.as_view()),
    path("price/", PriceView.as_view()),
]
