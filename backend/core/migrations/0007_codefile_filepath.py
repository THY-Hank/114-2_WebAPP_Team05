# Generated migration for adding filepath field to CodeFile

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_filecomment_comment_type_filecomment_end_line_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='codefile',
            name='filepath',
            field=models.CharField(blank=True, default='', max_length=500),
        ),
    ]
