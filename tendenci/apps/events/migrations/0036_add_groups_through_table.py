# Generated by Django 4.2.14 on 2024-08-15 21:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0035_addon_description'),
    ]
    
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                # Old table name from checking with sqlmigrate, new table
                # name from EventGoup._meta.db_table.
                migrations.RunSQL(
                    sql="ALTER TABLE events_event_groups RENAME TO events_eventgroup",
                    reverse_sql="ALTER TABLE events_eventgroup RENAME TO events_event_groups",
                ),
            ],
            state_operations=[
                migrations.CreateModel(
                    name="EventGroup",
                    fields=[
                        (
                            "id",
                            models.AutoField(
                                auto_created=True,
                                primary_key=True,
                                serialize=False,
                                verbose_name="ID",
                            ),
                        ),
                        (
                            "event",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name='group_relations',
                                to='events.event'),
                        ),
                        (
                            "group",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                to="user_groups.group",
                            ),
                        ),
                    ],
                ),
                migrations.AlterField(
                    model_name="event",
                    name="groups",
                    field=models.ManyToManyField(
                        to="user_groups.group",
                        through="events.EventGroup",
                    ),
                ),
            ],
        ),
        
        migrations.AddField(
            model_name="eventgroup",
            name="is_primary",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterUniqueTogether(
            name='eventgroup',
            unique_together={('event', 'group')},
        ),
    ]
