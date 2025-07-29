import os

num_users = 100

def generate_rdf_data(base_path):
    with open(os.path.join(base_path, "social_network.ttl"), "w", encoding="utf-8") as f:
        f.write("""@prefix ex: <http://example.org/> .\n""")
        f.write("""@prefix foaf: <http://xmlns.com/foaf/0.1/> .\n""")
        f.write("""@prefix dc: <http://purl.org/dc/elements/1.1/> .\n\n""")

        for i in range(1, num_users + 1):
            u = f"User{i}"
            next1 = f"User{(i % num_users) + 1}"
            next2 = f"User{((i + 1) % num_users) + 1}"
            post = f"Post{i}"
            comment = f"Comment{i}"
            comment_target_post = f"Post{((i + 1) % num_users) + 1}"

            # Korisnik
            f.write(f"ex:{u} a foaf:Person ;\n")
            f.write(f"  foaf:name \"{u}\" ;\n")
            f.write(f"  ex:knows ex:{next1}, ex:{next2} ;\n")
            f.write(f"  ex:created ex:{post} .\n\n")

            # Post
            f.write(f"ex:{post} a ex:Post ;\n")
            f.write(f"  dc:title \"Post by {u}\" ;\n")
            f.write(f"  ex:author ex:{u} .\n\n")

            # Komentar
            f.write(f"ex:{comment} a ex:Comment ;\n")
            f.write(f"  dc:content \"Comment by {u}\" ;\n")
            f.write(f"  ex:author ex:{u} ;\n")
            f.write(f"  ex:onPost ex:{comment_target_post} .\n\n")

if __name__ == "__main__":
    generate_rdf_data("data")