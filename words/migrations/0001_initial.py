# Generated by Django 2.2 on 2019-05-14 18:46

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import words.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('name', models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], help_text='Language', max_length=2, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PartOfSpeech',
            fields=[
                ('name', models.CharField(choices=[('n', 'noun'), ('v', 'verb'), ('adj', 'adjective'), ('adv', 'adverb')], help_text='Part of speech', max_length=3, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Word',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('frequency', models.DecimalField(blank=True, decimal_places=6, max_digits=12, null=True)),
                ('definitions', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('ant', models.ManyToManyField(related_name='_word_ant_+', related_query_name='antonym', to='words.Word', verbose_name='antonyms')),
                ('bga', models.ManyToManyField(help_text='words that frequently follow this (i.e. wreak followed by havoc', related_name='frequently_follows', to='words.Word', verbose_name='frequent followers')),
                ('bgb', models.ManyToManyField(help_text='words that frequently precede this(i.e. havoc preceding wreak', related_name='frequently_precedes', to='words.Word', verbose_name='frequent predecessors')),
                ('cns', models.ManyToManyField(help_text='i.e. sample and simple', related_name='_word_cns_+', related_query_name='consonant_match', to='words.Word', verbose_name='consonant matches')),
                ('com', models.ManyToManyField(help_text='things which this is composed of(a car has an accelerator, a steering wheel, etc.', related_name='part_of', to='words.Word', verbose_name='comprises')),
                ('gen', models.ManyToManyField(help_text='words with a similar, but more specific meaning (i.e. gondola is a hyponym of boat)', related_name='hypernyms', related_query_name='hypernym', to='words.Word', verbose_name='direct hyponyms')),
                ('hom', models.ManyToManyField(help_text='sound-alike words', related_name='_word_hom_+', related_query_name='homophone', to='words.Word', verbose_name='homophones')),
                ('jja', models.ManyToManyField(related_name='related_by_jja', to='words.Word', verbose_name='popular related noun')),
                ('jjb', models.ManyToManyField(related_name='related_by_jjb', to='words.Word', verbose_name='popular related adjective')),
                ('language', models.ForeignKey(default=words.models.default_language, on_delete=django.db.models.deletion.PROTECT, to='words.Language')),
                ('nry', models.ManyToManyField(help_text='approximate rhymes', related_name='_word_nry_+', related_query_name='near_rhyme', to='words.Word', verbose_name='near rhymes')),
                ('par', models.ManyToManyField(help_text='things of which this is a part of(a window is a part of a car, a house, a boat, etc.)', related_name='comprises', to='words.Word', verbose_name='part of')),
                ('parts_of_speech', models.ManyToManyField(blank=True, to='words.PartOfSpeech')),
                ('rhy', models.ManyToManyField(help_text='perfect rhymes', related_name='_word_rhy_+', related_query_name='rhyme', to='words.Word', verbose_name='rhymes')),
                ('spc', models.ManyToManyField(help_text='words with a similar, but broader meaning (i.e. boat is a hypernym of gondola)', related_name='hyponyms', related_query_name='hyponym', to='words.Word', verbose_name='direct hypernyms')),
                ('syn', models.ManyToManyField(related_name='_word_syn_+', related_query_name='synonym', to='words.Word', verbose_name='synonym')),
                ('trg', models.ManyToManyField(related_name='words_is_trigger_for', related_query_name='is_trigger_for', to='words.Word', verbose_name='triggers')),
            ],
        ),
        migrations.CreateModel(
            name='WordSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Enter a name for this set of words', max_length=100)),
                ('description', models.TextField(blank=True, help_text='Enter a description for this set of words')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('words', models.ManyToManyField(blank=True, related_query_name='word', to='words.Word')),
            ],
        ),
    ]
