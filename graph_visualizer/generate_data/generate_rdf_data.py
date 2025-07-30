import os
import random
from datetime import datetime, timedelta

num_users = 100

def generate_simple_rdf_users(base_path):
    os.makedirs(base_path, exist_ok=True)
    with open(os.path.join(base_path, "simple_users.ttl"), "w", encoding="utf-8") as f:
        f.write("""@prefix ex: <http://example.org/> .\n""")
        f.write("""@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n""")
        f.write("""@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n""")

        for i in range(1, num_users + 1):
            user_id = f"User{i}"
            age = random.randint(18, 65)
            rating = round(random.uniform(1.0, 5.0), 2)
            reg_date = (datetime(2020, 1, 1) + timedelta(days=i)).date()

            f.write(f"ex:{user_id} a foaf:Person ;\n")
            f.write(f"  foaf:name \"{user_id}\" ;\n")
            f.write(f"  ex:age \"{age}\"^^xsd:int ;\n")
            f.write(f"  ex:rating \"{rating}\"^^xsd:float ;\n")
            f.write(f"  ex:registeredOn \"{reg_date}\"^^xsd:date .\n\n")

if __name__ == "__main__":
    generate_simple_rdf_users("data")
