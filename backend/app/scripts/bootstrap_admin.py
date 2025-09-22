def main():
    import os
    email = os.environ.get("BOOTSTRAP_ADMIN_EMAIL")
    pwd   = os.environ.get("BOOTSTRAP_ADMIN_PASSWORD")
    if email and pwd:
        print(f"[bootstrap_admin] Ready to create admin {email} (stub)")
if __name__ == "__main__":
    main()
