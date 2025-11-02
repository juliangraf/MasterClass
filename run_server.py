import os
import socket
import sys
import threading
import time
import tkinter as tk
from datetime import timedelta, timezone

import django
import webview
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


def ensure_database_ready():
    """Erstellt oder aktualisiert die Datenbank."""
    db_conn = connections['default']
    try:
        db_conn.cursor()
    except OperationalError:
        print("Datenbank wird erstellt ...")
    finally:
        django.setup()
        call_command("makemigrations", interactive=False)
        call_command("migrate", interactive=False)
        print("Datenbank ist bereit.")
        populate_test_data()


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
    webview.create_window(
        "Masterclass",
        "http://127.0.0.1:8000/",
        width=screen_width,
        height=screen_height,
        resizable=True,
    )
    icon_path = os.path.join(base, "img/icon.png")

    webview.start(icon=icon_path)
    sys.exit()


if __name__ == "__main__":
    main()
