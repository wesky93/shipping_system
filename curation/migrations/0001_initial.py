# Generated by Django 3.1.4 on 2020-12-11 03:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Curation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('calorie', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='curation.category')),
            ],
        ),
        migrations.CreateModel(
            name='SetMenu',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('menus', models.ManyToManyField(to='curation.Menu')),
            ],
        ),
        migrations.CreateModel(
            name='CurationPriority',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(default=0)),
                ('curation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curation.curation')),
                ('set_menu', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='curation.setmenu')),
            ],
            options={
                'ordering': ('priority',),
            },
        ),
        migrations.AddField(
            model_name='curation',
            name='set_menus',
            field=models.ManyToManyField(through='curation.CurationPriority', to='curation.SetMenu'),
        ),
    ]