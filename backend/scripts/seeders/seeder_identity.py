import random
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.enums import UserRole
from app.models.identity import Role, User
from app.models.organization import Department, Building, Floor, Room, University, Campus, Faculty
from app.models.asset import AssetCategory, AssetSubCategory, Vendor
from scripts.seeder_core import check_table_empty, fake

async def seed_identity_org(session: AsyncSession):
    print("Seeding Identity and Organization (AEGON Industries Pvt. Ltd.)...")
    
    if await check_table_empty(session, Role):
        roles = []
        for r_enum in UserRole:
            roles.append(Role(id=uuid.uuid4(), name=r_enum.value, description=f"{r_enum.value} Role"))
        
        # Add required enterprise roles
        extra_roles = [
            "Enterprise Admin", "Operations Manager", "Maintenance Engineer", 
            "Technician", "Finance Analyst", "Inventory Manager", 
            "Procurement Officer", "Executive"
        ]
        for er in extra_roles:
            roles.append(Role(id=uuid.uuid4(), name=er, description=f"{er} Role"))
            
        session.add_all(roles)
        await session.commit()
        print(f"Inserted {len(roles)} Roles")

    if await check_table_empty(session, University):
        # Company
        uni = University(id=uuid.uuid4(), name="AEGON Industries Pvt. Ltd.", code="AEGON")
        session.add(uni)
        await session.commit()
        
        # Locations (Campuses)
        location_names = [
            "Head Office", "Manufacturing Plant A", "Manufacturing Plant B", 
            "Warehouse", "Regional Office", "Data Center"
        ]
        locations = []
        for loc in location_names:
            locations.append(Campus(
                id=uuid.uuid4(), 
                name=loc, 
                code=loc[:4].upper().replace(" ", "") + str(random.randint(10, 99)), 
                university_id=uni.id
            ))
        session.add_all(locations)
        await session.commit()
        
        # Divisions (Faculties)
        div_names = ["Corporate Division", "Operations Division", "Logistics Division"]
        divs = [Faculty(id=uuid.uuid4(), name=d, code=d[:4].upper()) for d in div_names]
        session.add_all(divs)
        await session.commit()

    if await check_table_empty(session, Department):
        facs = (await session.execute(select(Faculty.id))).scalars().all()
        departments = []
        dept_names = [
            "Operations", "Manufacturing", "IT", "Procurement", 
            "Finance", "Logistics", "Facilities", "Human Resources"
        ]
        for name in dept_names:
            departments.append(Department(
                id=uuid.uuid4(), 
                name=name, 
                code=name[:3].upper(), 
                faculty_id=random.choice(facs) if facs else None
            ))
        session.add_all(departments)
        await session.commit()
        print(f"Inserted {len(departments)} Departments")

    if await check_table_empty(session, User):
        from app.core.security import get_password_hash
        users = []
        roles = (await session.execute(select(Role.id))).scalars().all()
        depts = (await session.execute(select(Department.id))).scalars().all()
        
        # Generate 100 enterprise users
        for i in range(100):
            users.append(User(
                id=uuid.uuid4(),
                email=f"{fake.first_name().lower()}.{fake.last_name().lower()}@aegon.com",
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                hashed_password=get_password_hash("StrongPass1!"),
                is_active=True,
                role_id=random.choice(roles),
                department_id=random.choice(depts)
            ))
        session.add_all(users)
        await session.commit()
        print(f"Inserted {len(users)} Users")

    if await check_table_empty(session, Vendor):
        vendors = []
        for _ in range(50):
            vendor_name = fake.company()
            if not any(x in vendor_name for x in ["Inc", "LLC", "Corp", "Ltd"]):
                vendor_name += " " + random.choice(["Inc.", "LLC", "Corp.", "Ltd."])
            
            vendors.append(Vendor(
                id=uuid.uuid4(),
                name=vendor_name,
                code=fake.unique.bothify('VEND-####'),
                contact_email=fake.company_email(),
                contact_phone=fake.phone_number()[:20]
            ))
        session.add_all(vendors)
        await session.commit()
        print(f"Inserted {len(vendors)} Vendors")

    if await check_table_empty(session, AssetCategory):
        categories = []
        cat_names = [
            "Servers", "Networking", "Laptops", "Printers", 
            "Industrial Machines", "Robotic Arms", "HVAC", "UPS", 
            "Generators", "Forklifts", "Vehicles", "Security Cameras", 
            "Sensors", "IoT Devices"
        ]
        for name in cat_names:
            categories.append(AssetCategory(
                id=uuid.uuid4(),
                name=name,
                code=name[:4].upper() + str(random.randint(10, 99)),
                description=f"Category for {name}"
            ))
        session.add_all(categories)
        await session.commit()
        
        subcats = []
        for cat in categories:
            for j in range(3):
                subcats.append(AssetSubCategory(
                    id=uuid.uuid4(),
                    name=f"{cat.name} Type {chr(65+j)}",
                    code=f"SUB_{cat.code}_{j}",
                    category_id=cat.id
                ))
        session.add_all(subcats)
        await session.commit()
        print(f"Inserted {len(categories)} Asset Categories and {len(subcats)} Subcategories")

    if await check_table_empty(session, Building):
        campuses = (await session.execute(select(Campus.id))).scalars().all()
        # Buildings
        buildings = []
        for i, c_id in enumerate(campuses):
            buildings.append(Building(id=uuid.uuid4(), name=f"Main Facility {i+1}", code=f"MF{i+1}", campus_id=c_id))
        session.add_all(buildings)
        await session.commit()
        
        # Floors
        floors = []
        for b in buildings:
            for i in range(3): # 3 floors per building
                floors.append(Floor(id=uuid.uuid4(), building_id=b.id, level=i, code=f"F{i}"))
        session.add_all(floors)
        await session.commit()
        
        # Rooms
        rooms = []
        for f in floors:
            for i in range(5): # 5 rooms per floor
                rooms.append(Room(id=uuid.uuid4(), floor_id=f.id, number=f"R-{f.level}-{i}", code=f"RC{uuid.uuid4().hex[:4]}", room_type="Workspace"))
        session.add_all(rooms)
        await session.commit()
        print(f"Inserted Locations (Buildings, Floors, Rooms)")
