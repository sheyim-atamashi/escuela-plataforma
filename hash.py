from argon2 import PasswordHasher
ph = PasswordHasher(time_cost=2, memory_cost=1024, parallelism=2, hash_len=32, salt_len=16)
print(ph.hash("ppaafhadppaafhadppaafhad"))
