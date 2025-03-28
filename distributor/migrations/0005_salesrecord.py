# Generated by Django 5.1.7 on 2025-03-28 02:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('distributor', '0004_stockinventory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SalesRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_sales', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('revenue', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('date', models.DateField(auto_now_add=True)),
                ('distributor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sales', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
