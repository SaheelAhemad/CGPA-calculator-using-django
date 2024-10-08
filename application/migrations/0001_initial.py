# Generated by Django 5.0.6 on 2024-06-20 07:44

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grades',
            fields=[
                ('grade_id', models.AutoField(primary_key=True, serialize=False)),
                ('grade_name', models.CharField(max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='StudentMarks',
            fields=[
                ('student_id', models.IntegerField(primary_key=True, serialize=False)),
                ('subcode', models.CharField(max_length=20)),
                ('marks', models.IntegerField()),
                ('grade_id', models.CharField(max_length=20)),
                ('grade_credits', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Subjects',
            fields=[
                ('subcode', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('subname', models.CharField(max_length=100)),
                ('credits', models.IntegerField()),
            ],
        ),
    ]
