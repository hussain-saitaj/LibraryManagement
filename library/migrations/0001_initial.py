# Generated by Django 4.0.6 on 2022-07-12 13:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(blank=True, max_length=10)),
                ('title', models.CharField(blank=True, max_length=10)),
                ('price', models.CharField(blank=True, max_length=10)),
                ('category', models.CharField(blank=True, choices=[('general', 'general'), ('novel', 'novel'), ('story', 'story')], default='novel', max_length=10)),
                ('edition', models.CharField(blank=True, max_length=10)),
                ('details', models.CharField(blank=True, max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(blank=True, max_length=100)),
                ('uname', models.CharField(blank=True, max_length=50)),
                ('phone_no', models.CharField(blank=True, max_length=10)),
                ('address', models.TextField(blank=True)),
                ('role', models.CharField(blank=True, choices=[('staff', 'staff'), ('publisher', 'publisher'), ('reader', 'reader')], default='reader', max_length=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Issued_details',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issued_date', models.DateField(auto_now_add=True)),
                ('return_date', models.DateField()),
                ('book_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='library.book')),
                ('user_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='library.customuser')),
            ],
        ),
        migrations.AddField(
            model_name='book',
            name='publisher_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.customuser'),
        ),
    ]