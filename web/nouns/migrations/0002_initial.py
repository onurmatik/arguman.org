# Generated by Django 3.2.7 on 2021-09-10 18:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('nouns', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='relation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='noun',
            unique_together={('text', 'language')},
        ),
        migrations.AddField(
            model_name='keyword',
            name='noun',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='keywords', to='nouns.noun'),
        ),
        migrations.AddField(
            model_name='channel',
            name='nouns',
            field=models.ManyToManyField(blank=True, null=True, to='nouns.Noun'),
        ),
    ]