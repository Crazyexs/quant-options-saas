from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import RequireTier
from . import services


class GexView(APIView):
    """Free tier: ES only. Pro+: any symbol."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sym = request.query_params.get("symbol", "ES").upper()
        if sym != "ES" and not request.user.has_tier("pro"):
            return Response({"detail": "Pro plan required for symbols other than ES."},
                            status=403)
        return Response(services.gex_symbol(sym))


class GexAllView(APIView):
    permission_classes = [IsAuthenticated, RequireTier("pro")]

    def get(self, _request):
        return Response(services.gex_all())


class ExposureView(APIView):
    permission_classes = [IsAuthenticated, RequireTier("pro")]

    def get(self, request):
        sym = request.query_params.get("symbol", "ES").upper()
        greek = request.query_params.get("greek", "GEX").upper()
        if greek not in ("DEX", "GEX", "VEX", "VEGA", "CHARM"):
            return Response({"detail": "greek must be DEX/GEX/VEX/VEGA/CHARM."}, status=400)
        return Response(services.exposure(sym, greek))


class ChainView(APIView):
    permission_classes = [IsAuthenticated, RequireTier("pro")]

    def get(self, request):
        sym = request.query_params.get("symbol", "ES").upper()
        return Response(services.chain(sym))


class VolSurfaceView(APIView):
    """Elite: full IV surface payload (frontend renders the 3-D)."""
    permission_classes = [IsAuthenticated, RequireTier("elite")]

    def get(self, request):
        sym = request.query_params.get("symbol", "ES").upper()
        return Response(services.chain(sym))


class MacroNqView(APIView):
    permission_classes = [IsAuthenticated, RequireTier("pro")]

    def get(self, _request):
        return Response(services.macro_nq())


class MacroEventsView(APIView):
    permission_classes = [IsAuthenticated]   # free tier

    def get(self, _request):
        return Response(services.macro_events())


class FundamentalsView(APIView):
    permission_classes = [IsAuthenticated, RequireTier("pro")]

    def get(self, request):
        sym = request.query_params.get("symbol", "NVDA").upper()
        disc = request.query_params.get("discount")
        disc = float(disc) / 100.0 if disc else None
        return Response(services.fundamentals(sym, discount=disc))


class PriceView(APIView):
    """OHLC candles for the price chart (futures ES/NQ/GC or any ticker)."""
    permission_classes = [IsAuthenticated, RequireTier("pro")]

    def get(self, request):
        sym = request.query_params.get("symbol", "ES").upper()
        interval = request.query_params.get("interval", "15m")
        period = request.query_params.get("period", "5d")
        return Response(services.price(sym, interval=interval, period=period))
