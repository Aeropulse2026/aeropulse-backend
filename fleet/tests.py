from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from .models import Aircraft, TelemetryImport
from .globalmilitary import parse_iaf_inventory


class FleetApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("planner", password="test-password")
        self.client.force_authenticate(self.user)

    def test_fleet_overview(self):
        Aircraft.objects.create(aircraft_id="AF-117", aircraft_type="Trainer-X", age_years=8,
                                total_flight_hours=4820, total_cycles=6370, base="Base-A", health_score=82)
        response = self.client.get("/api/fleet/overview")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["mission_ready"], 1)

    def test_csv_import_is_saved_and_checked(self):
        data = b"timestamp,aircraft_id,subsystem,vibration_mm_s,temperature_c,pressure_psi,oil_level_pct\n2026-01-01,AF-117,hydraulic_pump,2.1,60,2500,80\n"
        upload = SimpleUploadedFile("telemetry.csv", data, content_type="text/csv")
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post("/api/fleet/imports/telemetry", {"file": upload}, format="multipart")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TelemetryImport.objects.get().status, TelemetryImport.Status.COMPLETE)

    def test_globalmilitary_table_parser(self):
        html = """<p>Updated 26 Sep 2026</p><p>operates 2,338 military aircraft and 691 more aircraft on order</p>
        <h3>Indian Air Force</h3><table><tr><th>Aircraft</th></tr><tr><td>Combat</td></tr>
        <tr><td>Tejas</td><td>India</td><td>2015</td><td>37</td><td>+5</td><td>+180</td></tr></table>"""
        metadata, aircraft = parse_iaf_inventory(html)
        self.assertEqual(metadata["active_aircraft_total"], 2338)
        self.assertEqual(aircraft[0]["name"], "Tejas")
        self.assertEqual(aircraft[0]["ordered"], 180)

    def test_globalmilitary_parser_ignores_leading_empty_cell(self):
        html = """<h3>Indian Air Force</h3><table><tr><td>Combat</td></tr>
        <tr><td></td><td>Tejas</td><td>India</td><td>2015</td><td>37</td><td>+5</td><td>+180</td></tr></table>"""
        _, aircraft = parse_iaf_inventory(html)
        self.assertEqual(aircraft[0]["name"], "Tejas")
        self.assertEqual(aircraft[0]["yoy_change"], 5)

    def test_bearer_token_authentication(self):
        self.client.force_authenticate(user=None)
        login = self.client.post("/api/auth/login", {"username": "planner", "password": "test-password"}, format="json")
        self.assertIn("aeropulse_access", login.cookies)
        response = self.client.get("/api/fleet/overview")
        self.assertEqual(response.status_code, 200)

    def test_signup_login_and_refresh(self):
        sign_up = self.client.post("/api/auth/signup", {"username": "new-planner", "password": "safe-demo-password-987"}, format="json")
        self.assertEqual(sign_up.status_code, 201)
        self.assertIn("aeropulse_refresh", sign_up.cookies)
        login = self.client.post("/api/auth/login", {"username": "new-planner", "password": "safe-demo-password-987"}, format="json")
        self.assertEqual(login.status_code, 200)
        refresh = self.client.post("/api/auth/refresh")
        self.assertEqual(refresh.status_code, 204)
        self.assertIn("aeropulse_access", refresh.cookies)
