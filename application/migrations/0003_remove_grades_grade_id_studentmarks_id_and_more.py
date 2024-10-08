# Generated by Django 5.0.6 on 2024-06-20 08:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0002_remove_studentmarks_grade_id_studentmarks_grade_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='grades',
            name='grade_id',
        ),
        migrations.AddField(
            model_name='studentmarks',
            name='id',
            field=models.BigAutoField(auto_created=True, default=2, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='grades',
            name='grade_name',
            field=models.CharField(max_length=10, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='studentmarks',
            name='student_id',
            field=models.IntegerField(default=2),
        ),
        migrations.AlterUniqueTogether(
            name='studentmarks',
            unique_together={('student_id', 'subcode')},
        ),
    ]
