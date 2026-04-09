from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_codefile_content_type_codefile_is_binary_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeFileVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('version_number', models.PositiveIntegerField()),
                ('content', models.TextField(blank=True)),
                ('change_note', models.CharField(blank=True, default='', max_length=255)),
                ('tag_name', models.CharField(blank=True, default='', max_length=100)),
                ('is_snapshot', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='core.codefile')),
            ],
            options={
                'ordering': ['-version_number'],
                'unique_together': {('file', 'version_number')},
            },
        ),
    ]
