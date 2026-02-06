# view_data.py
import sqlite3
from tabulate import tabulate  # pip install tabulate

def view_database():
    conn = sqlite3.connect('the_vault.db')
    cursor = conn.cursor()
    
    print("=" * 60)
    print("THE VAULT - VISUALIZADOR DE BANCO DE DADOS")
    print("=" * 60)
    
    # 1. Mostrar tabelas disponíveis
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n📊 TABELAS DISPONÍVEIS:")
    for table in tables:
        print(f"  • {table[0]}")
    
    # 2. Mostrar usuários
    print("\n👥 USUÁRIOS CADASTRADOS:")
    cursor.execute("SELECT id, username, email, created_at, last_login FROM users")
    users = cursor.fetchall()
    
    if users:
        headers = ["ID", "Username", "Email", "Criado em", "Último login"]
        print(tabulate(users, headers=headers, tablefmt="grid"))
    else:
        print("Nenhum usuário cadastrado.")
    
    # 3. Mostrar tentativas falhas
    print("\n⚠️ TENTATIVAS FALHAS DE LOGIN:")
    cursor.execute("""
        SELECT id, username, ip_address, attempted_at 
        FROM failed_login_attempts 
        ORDER BY attempted_at DESC 
        LIMIT 10
    """)
    attempts = cursor.fetchall()
    
    if attempts:
        headers = ["ID", "Username", "IP", "Data/Hora"]
        print(tabulate(attempts, headers=headers, tablefmt="grid"))
    else:
        print("Nenhuma tentativa falha registrada.")
    
    # 4. Estatísticas
    print("\n📈 ESTATÍSTICAS:")
    
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]
    print(f"Total de usuários: {total_users}")
    
    cursor.execute("SELECT COUNT(DISTINCT username) FROM failed_login_attempts")
    users_with_failed = cursor.fetchone()[0]
    print(f"Usuários com tentativas falhas: {users_with_failed}")
    
    cursor.execute("SELECT COUNT(*) FROM failed_login_attempts")
    total_failed = cursor.fetchone()[0]
    print(f"Total de tentativas falhas: {total_failed}")
    
    conn.close()
    print("\n" + "=" * 60)

if __name__ == "__main__":
    view_database()