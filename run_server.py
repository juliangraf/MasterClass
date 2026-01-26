import os
import socket
import sys
import threading
import time
import tkinter as tk
from datetime import timedelta, timezone
from tkinter import filedialog

import django
import webview
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.db import connections
from django.db.utils import OperationalError
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "masterclass.settings")
django.setup()
from resources.models import Role, Resource, Project, Event


def populate_test_data():
    # Abbruch, wenn schon Rollen existieren
    if Role.objects.count() > 0:
        return

    # Projekt anlegen (von heute eine Woche)
    today = timezone.now().date()
    Project.objects.create(label="MeinName", start_date=today, end_date=today + timedelta(days=5))

    # Rollen anlegen
    role_teacher = Role.objects.create(label="Lehrer", plural_label="Lehrer", weight=1)
    role_student = Role.objects.create(label="Schüler", plural_label="Schüler", weight=2)
    role_room = Role.objects.create(label="Raum", plural_label="Räume", weight=3)

    # Ressourcen anlegen
    teacher_anna = Resource.objects.create(label="Anna Müller", description="Mathematiklehrerin", role=role_teacher)
    teacher_peter = Resource.objects.create(label="Peter Schmidt", description="Physiklehrer", role=role_teacher)

    student_lisa = Resource.objects.create(label="Lisa Meier", description="Schülerin", role=role_student)
    student_max = Resource.objects.create(label="Max Bauer", description="Schüler", role=role_student)
    student_emma = Resource.objects.create(label="Emma Schulz", description="Schülerin", role=role_student)

    room_101 = Resource.objects.create(label="Raum 101", description="Klassenzimmer", role=role_room)
    room_lab = Resource.objects.create(label="Labor", description="Physiklabor", role=role_room)

    # Projekt anlegen (von heute eine Woche)
    today = timezone.now().date()
    project = Project.objects.create(label="Schulwoche", start_date=today, end_date=today + timedelta(days=2))

    # Termine anlegen
    now = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Globales Event
    Event.objects.create(
        label="Schulversammlung",
        start=now + timedelta(days=1, hours=9),
        end=now + timedelta(days=1, hours=10),
        is_global=True
    )

    # Einzelne Termine mit Ressourcen
    e1 = Event.objects.create(
        label="Mathematik",
        start=now + timedelta(days=1, hours=10),
        end=now + timedelta(days=1, hours=11),
        is_global=False,
    )
    e1.dependencies.add(teacher_anna, student_lisa, student_max, room_101)

    # Einzelne Termine mit Ressourcen
    e1 = Event.objects.create(
        label="Sprechstunde",
        start=now + timedelta(days=1, hours=15),
        end=now + timedelta(days=1, hours=16),
        is_global=False,
    )
    e1.dependencies.add(teacher_anna, student_lisa, room_101)

    e2 = Event.objects.create(
        label="Physik",
        start=now + timedelta(days=2, hours=11),
        end=now + timedelta(days=2, hours=12, minutes=30),
        is_global=False,
    )
    e2.dependencies.add(teacher_peter, student_emma, room_lab)

    e3 = Event.objects.create(
        label="Sport",
        start=now + timedelta(days=3, hours=14),
        end=now + timedelta(days=3, hours=15),
        is_global=False,
    )
    e3.dependencies.add(student_lisa, student_max, student_emma, room_101)


def choose_or_create_project() -> tuple[str, bool]:
    """
    Shows a dialog asking whether the user wants to open an existing
    project (SQLite database) or create a new project.

    Returns:
        (database_path, created_new)
    """
    root = tk.Tk()
    root.title("Projekt auswählen")
    root.resizable(False, False)
    root.configure(padx=16, pady=14)

    result: dict[str, object] = {"choice": None}

    title = tk.Label(root, text="Projekt auswählen", font=("Segoe UI", 12, "bold"))
    title.grid(row=0, column=0, columnspan=2, sticky="w")

    text = tk.Label(
        root,
        text=(
            "Möchten Sie ein bestehendes Projekt öffnen\n"
            "oder ein neues Projekt anlegen?"
        ),
        justify="left",
    )
    text.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 12))

    def open_project() -> None:
        result["choice"] = "open"
        root.destroy()

    def create_project() -> None:
        result["choice"] = "new"
        root.destroy()

    btn_open = tk.Button(root, text="Projekt öffnen", width=24, command=open_project)
    btn_new = tk.Button(root, text="Neues Projekt anlegen", width=24, command=create_project)
    btn_open.grid(row=2, column=0, padx=(0, 10))
    btn_new.grid(row=2, column=1)

    root.update_idletasks()
    w, h = 420, 170
    x = (root.winfo_screenwidth() - w) // 2
    y = (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()

    choice = result["choice"]
    if choice is None:
        raise RuntimeError("Abgebrochen: Es wurde keine Auswahl getroffen.")

    if choice == "open":
        path = filedialog.askopenfilename(
            title="Projekt öffnen",
            filetypes=[("Projekt (SQLite)", "*.sqlite3"), ("Alle Dateien", "*.*")],
        )
        if not path:
            raise RuntimeError("Abgebrochen: Es wurde kein Projekt ausgewählt.")
        return os.path.abspath(path), False

    path = filedialog.asksaveasfilename(
        title="Neues Projekt anlegen",
        defaultextension=".sqlite3",
        filetypes=[("Projekt (SQLite)", "*.sqlite3")],
    )
    if not path:
        raise RuntimeError("Abgebrochen: Es wurde kein Speicherort ausgewählt.")
    return os.path.abspath(path), True


def ensure_database_ready():
    """Selects or creates the project database and runs migrations."""
    db_path, created_new = choose_or_create_project()

    # Must be set BEFORE django.setup()
    settings.DATABASES["default"]["NAME"] = db_path

    django.setup()

    db_conn = connections["default"]
    try:
        db_conn.cursor()
    except OperationalError:
        print("Database will be created …")

    call_command("makemigrations", interactive=False)
    call_command("migrate", interactive=False)

    if created_new:
        populate_test_data()

    print(f"Project database ready: {db_path}")


def ensure_superuser():
    """Erstellt einen Admin, falls keiner existiert."""
    User = get_user_model()
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser("admin", "admin@example.com", "admin")
        print("Superuser 'admin' (Passwort: admin) erstellt.")


def start_django():
    """Startet den Django-Server ohne Autoreload."""
    call_command("runserver", "127.0.0.1:8000", use_reloader=False)


def wait_for_port(host: str, port: int, timeout: float = 10.0):
    """Wartet, bis der Django-Server erreichbar ist."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.3)
    raise TimeoutError("Django-Server ist nicht erreichbar.")


def main():
    root = tk.Tk()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()
    base = getattr(sys, '_MEIPASS', os.path.abspath("."))

    ensure_database_ready()
    ensure_superuser()

    # Django im Hintergrund starten
    server_thread = threading.Thread(target=start_django, daemon=True)
    server_thread.start()

    # Warten bis Django läuft
    wait_for_port("127.0.0.1", 8000)

    # Jetzt das Webview-Fenster im Hauptthread starten
    window_width = round(screen_width * 0.9)
    window_height = round(screen_height * 0.9)
    # Calculate top-left coordinates to center
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2
    webview.create_window(
        "Masterclass",
        "http://127.0.0.1:8000/",
        width=window_width,
        height=window_height,
        resizable=True,
        x=x,
        y=y
    )
    icon_path = os.path.join(base, "img/icon.png")

    webview.start(icon=icon_path)
    sys.exit()


if __name__ == "__main__":
    main()
