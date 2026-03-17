from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("content", "0006_test_scope_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="exercise",
            name="exercise_type",
            field=models.CharField(
                choices=[
                    ("multiple_choice", "Multiple Choice"),
                    ("fill_blank", "Fill in the Blank"),
                    ("multi_fill_blank", "Multi Fill in the Blank"),
                    ("expression", "Expression Input"),
                    ("true_false", "True/False"),
                    ("drag_order", "Drag to Order"),
                    ("click_select", "Click to Select"),
                    ("comparison", "Comparison (<, =, >)"),
                ],
                max_length=20,
            ),
        ),
    ]
