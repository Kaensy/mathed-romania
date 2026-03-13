from apps.content.models import Lesson
import json, os

output_dir = "lesson_exports"
os.makedirs(output_dir, exist_ok=True)

for lesson in Lesson.objects.exclude(blocks=[]).order_by("unit__order", "order"):
    filename = f"lesson_{lesson.unit.order}_{lesson.order}_blocks.json"
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(lesson.blocks, f, ensure_ascii=False, indent=2)
    print(f"Saved {filepath}")

print("Done!")
