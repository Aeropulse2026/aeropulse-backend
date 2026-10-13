from django.contrib.auth import get_user_model
from django.test import SimpleTestCase
from rest_framework.test import APITestCase

from squadron.bharat_rakshak import parse_iaf_squadrons
from squadron.models import Squadron


class BharatRakshakParserTests(SimpleTestCase):
    def test_extracts_only_flying_squadrons_and_roles(self):
        html = """
        <h2><a>Flying Units</a></h2>
        <h3>Fighter/ Bomber</h3>
        <a>No. 1 Squadron</a><a>No. 101 PR Flight</a>
        <h3>Transport</h3><a>No. 11 Squadron</a>
        <h3>RPA</h3><a>No. 34 Sqn</a>
        <h2><a>Missile Units</a></h2>
        <h3>SA-2</h3><a>No. 34 Squadron</a>
        """

        records = parse_iaf_squadrons(html)

        self.assertEqual([record["name"] for record in records], [
            "No. 1 Squadron", "No. 11 Squadron", "No. 34 Sqn",
        ])
        self.assertEqual(records[0]["operational_role"], "Fighter/ Bomber")
        self.assertEqual(records[1]["operational_role"], "Transport")
        self.assertTrue(records[0]["squadron_id"].startswith("iaf-no-1-squadron-"))


class SquadronAircraftApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user("squadron-manager", password="test-password")
        self.client.force_authenticate(self.user)
        self.squadron = Squadron.objects.create(
            squadron_id="iaf-no-1-squadron-000001",
            name="No. 1 Squadron",
        )

    def test_create_and_filter_individual_squadron_aircraft(self):
        payload = {
            "squadron": self.squadron.squadron_id,
            "aircraft_number": "SB-001",
            "aircraft_name": "Su-30MKI",
            "country_of_origin": "India / Russia",
            "year_inducted": 2002,
            "flight_hours": "1842.5",
            "last_maintenance_on": "2026-09-30",
            "next_maintenance_on": "2026-12-30",
            "operational_role": "Air superiority",
        }

        response = self.client.post("/api/fleet/squadron-aircraft/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["squadron"], self.squadron.squadron_id)
        self.assertEqual(response.data["aircraft_number"], "SB-001")
        response = self.client.get(f"/api/fleet/squadron-aircraft/?squadron={self.squadron.squadron_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
