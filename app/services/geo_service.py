from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class GeoResult:
    country: str | None
    city: str | None


class GeoService:

    @staticmethod
    def enrich(
        ip_address: str | None
    ) -> GeoResult | None:

        if ip_address is None:
            return None

        if settings.geo_mode == "mock":
            return GeoService._mock_enrich()

        return GeoService._real_enrich(
            ip_address
        )

    @staticmethod
    def _mock_enrich() -> GeoResult | None:

        if settings.geo_provider_a_enabled:
            return GeoResult(
                country="Turkey",
                city="Izmir"
            )

        if settings.geo_provider_b_enabled:
            return GeoResult(
                country="Germany",
                city="Berlin"
            )

        return None

    @staticmethod
    def _real_enrich(
        ip_address: str
    ) -> GeoResult | None:

        result = GeoService._try_provider_a(
            ip_address
        )

        if result is not None:
            return result

        result = GeoService._try_provider_b(
            ip_address
        )

        if result is not None:
            return result

        return None

    @staticmethod
    def _try_provider_a(
        ip_address: str
    ) -> GeoResult | None:

        if not settings.geo_provider_a_enabled:
            return None

        try:
            response = httpx.get(
                f"{settings.geo_provider_a_url}/{ip_address}",
                params={
                    "fields": "status,country,city"
                },
                timeout=2.0
            )

            response.raise_for_status()

            data = response.json()

            if data.get("status") != "success":
                return None

            return GeoResult(
                country=data.get("country"),
                city=data.get("city")
            )

        except (
            httpx.HTTPError,
            ValueError
        ):
            return None

    @staticmethod
    def _try_provider_b(
        ip_address: str
    ) -> GeoResult | None:

        if not settings.geo_provider_b_enabled:
            return None

        try:
            response = httpx.get(
                f"{settings.geo_provider_b_url}/{ip_address}/json/",
                timeout=2.0
            )

            response.raise_for_status()

            data = response.json()

            if data.get("error"):
                return None

            return GeoResult(
                country=data.get("country_name"),
                city=data.get("city")
            )

        except (
            httpx.HTTPError,
            ValueError
        ):
            return None