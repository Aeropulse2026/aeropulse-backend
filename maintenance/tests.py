from rest_framework.test import APITestCase

from fleet.models import Aircraft, InventoryPart, Subsystem


class AssetPartApiTests(APITestCase):
    def setUp(self):
        subsystem = Subsystem.objects.create(code="hydraulic_pump", name="Hydraulic pump")
        self.aircraft = Aircraft.objects.create(
            aircraft_id="AF-117",
            aircraft_type="Trainer-X",
            age_years=8,
            total_flight_hours=4820,
            total_cycles=6370,
            base="Base-A",
        )
        self.spare_part = InventoryPart.objects.create(
            part_id="HYD-PUMP-001",
            name="Hydraulic Pump Assembly",
            compatible_subsystem=subsystem,
            stock_on_hand=4,
            reserved_stock=1,
            reorder_point=2,
            lead_days=21,
        )

    def test_create_and_filter_asset_parts_by_aircraft(self):
        payload = {
            "aircraft": self.aircraft.aircraft_id,
            "spare_part": self.spare_part.part_id,
            "serial_number": "HYD-SN-0001",
            "installed_location": "Port hydraulic bay",
            "installed_on": "2026-01-15",
            "last_maintained_on": "2026-09-15",
            "next_maintenance_on": "2026-12-15",
            "status": "installed",
        }

        response = self.client.post("/api/maintenance/asset-parts/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["aircraft"], "AF-117")
        self.assertEqual(response.data["spare_part"], "HYD-PUMP-001")
        self.assertEqual(response.data["spare_part_details"]["name"], "Hydraulic Pump Assembly")
        response = self.client.get("/api/maintenance/asset-parts/?aircraft=AF-117")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_create_update_and_delete_spare_part_catalogue_record(self):
        payload = {
            "part_id": "HYD-VALVE-001",
            "name": "Hydraulic Control Valve",
            "compatible_subsystem": "hydraulic_pump",
            "stock_on_hand": 8,
            "reserved_stock": 2,
            "reorder_point": 3,
            "lead_days": 14,
        }

        response = self.client.post("/api/maintenance/spare-parts/", payload, format="json")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["available_stock"], 6)
        response = self.client.patch(
            "/api/maintenance/spare-parts/HYD-VALVE-001/",
            {"stock_on_hand": 10},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["available_stock"], 8)
        response = self.client.delete("/api/maintenance/spare-parts/HYD-VALVE-001/")
        self.assertEqual(response.status_code, 204)
