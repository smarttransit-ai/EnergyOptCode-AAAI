from common.configs.model_types import ElectricBusType, GasBusType, DummyBusType, BusMovementType, LocationType

electric_bus_type = ElectricBusType()
gas_bus_type = GasBusType()
dummy_bus_type = DummyBusType()

serving = BusMovementType("Serving")
moving = BusMovementType("Moving")
charging = BusMovementType("Charging")

route_location_type = LocationType("route_point")
charging_location_type = LocationType("charging_location")
