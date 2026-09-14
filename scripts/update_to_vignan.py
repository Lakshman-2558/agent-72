import sys
import os
sys.path.insert(0, os.path.abspath("."))

from agent72.infrastructure.database.session import SessionLocal
from agent72.infrastructure.database.models import InstitutionModel, StrategicPlanModel

def update_to_vignan():
    db = SessionLocal()
    try:
        for inst in db.query(InstitutionModel).all():
            if "Apex" in inst.name or "APEX" in inst.code:
                old_name = inst.name
                inst.name = "Vignan's University"
                inst.code = inst.code.replace("APEX", "VIGNAN")
                print("Updated institution:", old_name, "->", inst.name, "Code:", inst.code)
        
        for plan in db.query(StrategicPlanModel).all():
            if "Apex" in plan.institution_name or "Apex" in plan.title:
                plan.institution_name = "Vignan's University"
                plan.title = plan.title.replace("Apex Institute of Technology", "Vignan's University").replace("Apex University", "Vignan's University")
                print("Updated plan:", plan.title)
                
        db.commit()
        print("Database updated with Vignan's University successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    update_to_vignan()

