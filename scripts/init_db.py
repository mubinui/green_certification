#!/usr/bin/env python
"""
Database initialization script to create initial data for testing and development.
This script creates sample tree species and geographical suitability rules.
"""
import asyncio
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.database.session import get_db
from src.database.models import TreeSpecies, GeoSuitabilityRule
from sqlalchemy.ext.asyncio import AsyncSession


async def create_tree_species(db: AsyncSession) -> None:
    """Create sample tree species data"""
    species = [
        TreeSpecies(
            name="Oak",
            scientific_name="Quercus robur",
            description="A common deciduous tree with lobed leaves and acorns",
            average_lifespan=800,
            average_height=25.0,
            average_width=25.0,
            carbon_sequestration_rate=26.0,
            oxygen_production_rate=260.0,
            habitat_value=9,
            endangered_status="LC",  # Least Concern
        ),
        TreeSpecies(
            name="Maple",
            scientific_name="Acer saccharum",
            description="A deciduous tree with distinctive palmate leaves",
            average_lifespan=300,
            average_height=20.0,
            average_width=15.0,
            carbon_sequestration_rate=22.0,
            oxygen_production_rate=220.0,
            habitat_value=7,
            endangered_status="LC",  # Least Concern
        ),
        TreeSpecies(
            name="Pine",
            scientific_name="Pinus sylvestris",
            description="An evergreen coniferous tree with needle-shaped leaves",
            average_lifespan=450,
            average_height=30.0,
            average_width=10.0,
            carbon_sequestration_rate=20.0,
            oxygen_production_rate=200.0,
            habitat_value=6,
            endangered_status="LC",  # Least Concern
        ),
        TreeSpecies(
            name="Redwood",
            scientific_name="Sequoia sempervirens",
            description="One of the tallest tree species on Earth",
            average_lifespan=2000,
            average_height=90.0,
            average_width=7.0,
            carbon_sequestration_rate=45.0,
            oxygen_production_rate=450.0,
            habitat_value=10,
            endangered_status="EN",  # Endangered
        ),
        TreeSpecies(
            name="Cherry",
            scientific_name="Prunus avium",
            description="A flowering tree known for its spring blossoms",
            average_lifespan=100,
            average_height=12.0,
            average_width=10.0,
            carbon_sequestration_rate=15.0,
            oxygen_production_rate=150.0,
            habitat_value=5,
            endangered_status="LC",  # Least Concern
        ),
    ]
    
    db.add_all(species)
    await db.commit()
    print(f"Added {len(species)} tree species to the database")


async def create_geo_rules(db: AsyncSession) -> None:
    """Create sample geographical suitability rules"""
    rules = [
        GeoSuitabilityRule(
            tree_species_name="Oak",
            region="North America",
            min_latitude=25.0,
            max_latitude=65.0,
            min_longitude=-125.0,
            max_longitude=-65.0,
            min_altitude=0.0,
            max_altitude=1000.0,
            min_annual_rainfall=600.0,
            max_annual_rainfall=2000.0,
            min_temperature=-30.0,
            max_temperature=40.0,
            soil_types=["clay", "loam"],
        ),
        GeoSuitabilityRule(
            tree_species_name="Maple",
            region="North America",
            min_latitude=30.0,
            max_latitude=60.0,
            min_longitude=-120.0,
            max_longitude=-70.0,
            min_altitude=0.0,
            max_altitude=1200.0,
            min_annual_rainfall=700.0,
            max_annual_rainfall=1800.0,
            min_temperature=-40.0,
            max_temperature=38.0,
            soil_types=["loam", "sandy loam"],
        ),
        GeoSuitabilityRule(
            tree_species_name="Pine",
            region="Europe",
            min_latitude=40.0,
            max_latitude=70.0,
            min_longitude=-10.0,
            max_longitude=40.0,
            min_altitude=0.0,
            max_altitude=2500.0,
            min_annual_rainfall=300.0,
            max_annual_rainfall=1500.0,
            min_temperature=-45.0,
            max_temperature=35.0,
            soil_types=["sandy", "rocky"],
        ),
        GeoSuitabilityRule(
            tree_species_name="Redwood",
            region="North America",
            min_latitude=35.0,
            max_latitude=42.0,
            min_longitude=-124.0,
            max_longitude=-122.0,
            min_altitude=0.0,
            max_altitude=1000.0,
            min_annual_rainfall=1000.0,
            max_annual_rainfall=2500.0,
            min_temperature=-5.0,
            max_temperature=30.0,
            soil_types=["loam", "clay loam"],
        ),
        GeoSuitabilityRule(
            tree_species_name="Cherry",
            region="Asia",
            min_latitude=30.0,
            max_latitude=50.0,
            min_longitude=120.0,
            max_longitude=145.0,
            min_altitude=0.0,
            max_altitude=1500.0,
            min_annual_rainfall=800.0,
            max_annual_rainfall=2000.0,
            min_temperature=-15.0,
            max_temperature=35.0,
            soil_types=["loam", "well-drained"],
        ),
    ]
    
    db.add_all(rules)
    await db.commit()
    print(f"Added {len(rules)} geographical suitability rules to the database")


async def main() -> None:
    """Initialize the database with sample data"""
    print("Initializing database with sample data...")
    
    # Get database session
    async for db in get_db():
        # Create sample data
        await create_tree_species(db)
        await create_geo_rules(db)
        break
    
    print("Database initialization complete!")


if __name__ == "__main__":
    asyncio.run(main())