from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE UNIQUE INDEX uniq_products_sku_lower
                ON products_product (LOWER(sku));
            """,
            reverse_sql="""
                DROP INDEX uniq_products_sku_lower;
            """
        ),
    ]
