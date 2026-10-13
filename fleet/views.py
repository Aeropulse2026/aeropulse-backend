from django.db import transaction
from django.db.models import Avg, F
from rest_framework.permissions import AllowAny
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.conf import settings
from .models import Aircraft, ExternalFleetSnapshot, InventoryPart, MaintenanceRecommendation, TelemetryImport, UserProfile, WorkOrder
from .serializers import (AircraftSerializer, ExternalFleetAircraftSerializer, InventoryPartSerializer, LoginSerializer,
                          LogoutSerializer, RecommendationSerializer, SignUpSerializer, TelemetryImportSerializer,
                          WorkOrderSerializer)
from .services import refresh_features_and_predictions


class TelemetryImportView(generics.CreateAPIView):
    serializer_class = TelemetryImportSerializer

    def perform_create(self, serializer):
        # Django streams larger uploads to a temporary file, then stores it via FileField.
        import_record = serializer.save(uploaded_by=self.request.user)
        # A Celery/RQ worker can call this same function later.  Keeping the hook
        # after commit prevents it from reading a file that has not been saved yet.
        transaction.on_commit(lambda: refresh_features_and_predictions(import_record.id))


class FleetOverviewView(APIView):
    def get(self, request):
        aircraft = Aircraft.objects.all()
        return Response({
            "aircraft_total": aircraft.count(),
            "mission_ready": aircraft.filter(health_score__gte=70).count(),
            "at_risk": aircraft.filter(health_score__lt=50).count(),
            "average_health_score": aircraft.aggregate(value=Avg("health_score"))["value"],
            "pending_work_orders": WorkOrder.objects.filter(status=WorkOrder.Status.PENDING).count(),
        })


class AircraftDetailView(generics.RetrieveAPIView):
    queryset = Aircraft.objects.prefetch_related("work_orders")
    serializer_class = AircraftSerializer
    lookup_field = "aircraft_id"
    lookup_url_kwarg = "aircraft_id"


class MaintenanceQueueView(generics.ListAPIView):
    serializer_class = WorkOrderSerializer
    queryset = WorkOrder.objects.select_related("aircraft").order_by("-priority_score", "created_at")


class WorkOrderCreateView(generics.CreateAPIView):
    serializer_class = WorkOrderSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, status=WorkOrder.Status.PENDING)


class IafFleetView(APIView):
    def get(self, request):
        snapshot = ExternalFleetSnapshot.objects.prefetch_related("aircraft").first()
        if not snapshot:
            return Response({"detail": "No IAF snapshot is available. Run scrape_iaf_fleet first."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "source": {"name": snapshot.source_name, "url": snapshot.source_url,
                       "source_updated_on": snapshot.source_updated_on, "retrieved_at": snapshot.retrieved_at},
            "active_aircraft_total": snapshot.active_aircraft_total,
            "aircraft_on_order_total": snapshot.aircraft_on_order_total,
            "aircraft": ExternalFleetAircraftSerializer(snapshot.aircraft.all(), many=True).data,
        })

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.user
        response = Response({"user": user_payload(user)})
        set_auth_cookies(response, serializer.validated_data)
        return response


class SignUpView(generics.CreateAPIView):
    serializer_class = SignUpSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        UserProfile.objects.create(user=user)
        response = Response({"user": user_payload(user)}, status=status.HTTP_201_CREATED)
        set_auth_cookies(response, {"access": str(refresh.access_token), "refresh": str(refresh)})
        return response

class LogoutView(APIView):
    def post(self, request):
        serializer = LogoutSerializer(data={"refresh": request.COOKIES.get(settings.JWT_REFRESH_COOKIE)})
        serializer.is_valid(raise_exception=True)
        try:
            RefreshToken(serializer.validated_data["refresh"]).blacklist()
        except Exception:
            return Response({"detail": "Invalid refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        response = Response(status=status.HTTP_205_RESET_CONTENT)
        clear_auth_cookies(response)
        return response


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.COOKIES.get(settings.JWT_REFRESH_COOKIE)
        if not refresh:
            return Response({"detail": "Refresh cookie is missing."}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = TokenRefreshSerializer(data={"refresh": refresh})
        serializer.is_valid(raise_exception=True)
        response = Response(status=status.HTTP_204_NO_CONTENT)
        set_auth_cookies(response, serializer.validated_data)
        return response


def user_payload(user):
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return {"id": user.id, "username": user.username, "email": user.email, "role": profile.role}


def set_auth_cookies(response, tokens):
    cookie_options = {"httponly": True, "secure": settings.JWT_COOKIE_SECURE, "samesite": settings.JWT_COOKIE_SAMESITE}
    response.set_cookie(settings.JWT_ACCESS_COOKIE, tokens["access"], max_age=15 * 60, **cookie_options)
    if "refresh" in tokens:
        response.set_cookie(settings.JWT_REFRESH_COOKIE, tokens["refresh"], max_age=7 * 24 * 60 * 60, **cookie_options)


def clear_auth_cookies(response):
    response.delete_cookie(settings.JWT_ACCESS_COOKIE, samesite=settings.JWT_COOKIE_SAMESITE)
    response.delete_cookie(settings.JWT_REFRESH_COOKIE, samesite=settings.JWT_COOKIE_SAMESITE)

class AircraftTelemetryView(APIView):
    def get(self, request, aircraft_id):
        rows = Aircraft.objects.get(aircraft_id=aircraft_id).components.prefetch_related("telemetry").all()
        return Response([{"component": c.subsystem.code, "readings": [{"observed_at": t.observed_at, "vibration_mm_s": t.vibration_mm_s, "temperature_c": t.temperature_c, "pressure_psi": t.pressure_psi, "oil_level_pct": t.oil_level_pct} for t in c.telemetry.order_by("-observed_at")[:100]]} for c in rows])

class AircraftRiskView(APIView):
    def get(self, request, aircraft_id):
        aircraft = Aircraft.objects.get(aircraft_id=aircraft_id)
        predictions = [c.predictions.order_by("-scored_at").first() for c in aircraft.components.all()]
        return Response([{"component": p.component.subsystem.code, "model_version": p.model_version, "health_score": p.health_score, "priority_score": p.priority_score, "explanation_factors": p.explanation_factors} for p in predictions if p])

class InventoryView(generics.ListAPIView):
    queryset = InventoryPart.objects.all().order_by("part_id"); serializer_class = InventoryPartSerializer
class InventoryForecastView(APIView):
    def get(self, request):
        return Response(InventoryPartSerializer(InventoryPart.objects.filter(stock_on_hand__lte=F("reorder_point")), many=True).data)
class WorkOrderDetailView(generics.RetrieveUpdateAPIView):
    queryset = WorkOrder.objects.all(); serializer_class = WorkOrderSerializer
class RecommendationView(generics.ListAPIView):
    queryset = MaintenanceRecommendation.objects.all().order_by("-priority_score"); serializer_class = RecommendationSerializer
