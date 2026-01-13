from django.core.management.base import BaseCommand
from game.models import Word

class Command(BaseCommand):
    help = "Import words from a text file. Format: word|category (category optional). One per line."

    def add_arguments(self, parser):
        parser.add_argument("file", type=str, help="Path to words file (e.g. words_500.txt)")

    def handle(self, *args, **kwargs):
        path = kwargs["file"]
        created = 0
        updated = 0
        unchanged = 0

        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                if "|" in line:
                    text, category = [x.strip() for x in line.split("|", 1)]
                else:
                    text, category = line, ""

                if not text:
                    continue

                obj, was_created = Word.objects.get_or_create(
                    text=text,
                    defaults={"category": category[:50], "active": True},
                )
                if was_created:
                    created += 1
                else:
                    changed = False
                    if category and obj.category != category:
                        obj.category = category[:50]
                        changed = True
                    if not obj.active:
                        obj.active = True
                        changed = True

                    if changed:
                        obj.save(update_fields=["category", "active"])
                        updated += 1
                    else:
                        unchanged += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. created={created}, updated={updated}, unchanged={unchanged}"
        ))

