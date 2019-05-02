# Generated by Django 2.2 on 2019-05-02 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('words', '0002_auto_20190501_1639'),
    ]

    operations = [
        migrations.CreateModel(
            name='WordSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a name for this set of words', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Enter a description for this set of words')),
                ('private', models.BooleanField(default=False)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('words', models.ManyToManyField(blank=True, related_query_name='word', to='words.Word')),
            ],
        ),
    ]
