# Generated by Django 5.0.6 on 2024-07-18 18:27

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0006_userprofile_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='semester',
            name='sgpa',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='mark',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marks', to='application.student'),
        ),
        migrations.AlterField(
            model_name='mark',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='marks', to='application.subject'),
        ),
    ]
