# Generated by Django 5.0.1 on 2024-04-12 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('depenses', '0004_expensesheet_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expensesheet',
            name='statut',
            field=models.CharField(choices=[('VALIDATION CONFORMITE', 'VALIDATION_CONFORMITE'), ('REJET CONFORMITE', 'REJET_CONFORMITE'), ('VALIDATION BUDGETAIRE', 'VALIDATION_BUDGETAIRE'), ('REJET BUDGETAIRE', 'REJET_BUDGETAIRE'), ('VALIDATION ORDONNATEUR', 'VALIDATION_ORDONNATEUR'), ('REJET ORDONNATEUR', 'REJET_ORDONNATEUR'), ('VALIDATION DECAISSEMENT', 'VALIDATION_DECAISSEMENT'), ('REJET', 'REJET'), ('EN EXECUTION', 'EN_EXECUTION'), ('EXECUTE', 'ARCHIVE')], default='VALIDATION CONFORMITE', max_length=255),
        ),
        migrations.AlterField(
            model_name='historicalexpensesheet',
            name='statut',
            field=models.CharField(choices=[('VALIDATION CONFORMITE', 'VALIDATION_CONFORMITE'), ('REJET CONFORMITE', 'REJET_CONFORMITE'), ('VALIDATION BUDGETAIRE', 'VALIDATION_BUDGETAIRE'), ('REJET BUDGETAIRE', 'REJET_BUDGETAIRE'), ('VALIDATION ORDONNATEUR', 'VALIDATION_ORDONNATEUR'), ('REJET ORDONNATEUR', 'REJET_ORDONNATEUR'), ('VALIDATION DECAISSEMENT', 'VALIDATION_DECAISSEMENT'), ('REJET', 'REJET'), ('EN EXECUTION', 'EN_EXECUTION'), ('EXECUTE', 'ARCHIVE')], default='VALIDATION CONFORMITE', max_length=255),
        ),
        migrations.AlterField(
            model_name='historicalreturntocashier',
            name='statut',
            field=models.CharField(choices=[('VALIDATION CONFORMITE', 'VALIDATION_CONFORMITE'), ('REJET CONFORMITE', 'REJET_CONFORMITE'), ('VALIDATION BUDGETAIRE', 'VALIDATION_BUDGETAIRE'), ('REJET BUDGETAIRE', 'REJET_BUDGETAIRE'), ('VALIDATION ORDONNATEUR', 'VALIDATION_ORDONNATEUR'), ('REJET ORDONNATEUR', 'REJET_ORDONNATEUR'), ('VALIDATION DECAISSEMENT', 'VALIDATION_DECAISSEMENT'), ('REJET', 'REJET'), ('EN EXECUTION', 'EN_EXECUTION'), ('EXECUTE', 'ARCHIVE')], default='VALIDATION CAISSE', max_length=255),
        ),
        migrations.AlterField(
            model_name='returntocashier',
            name='statut',
            field=models.CharField(choices=[('VALIDATION CONFORMITE', 'VALIDATION_CONFORMITE'), ('REJET CONFORMITE', 'REJET_CONFORMITE'), ('VALIDATION BUDGETAIRE', 'VALIDATION_BUDGETAIRE'), ('REJET BUDGETAIRE', 'REJET_BUDGETAIRE'), ('VALIDATION ORDONNATEUR', 'VALIDATION_ORDONNATEUR'), ('REJET ORDONNATEUR', 'REJET_ORDONNATEUR'), ('VALIDATION DECAISSEMENT', 'VALIDATION_DECAISSEMENT'), ('REJET', 'REJET'), ('EN EXECUTION', 'EN_EXECUTION'), ('EXECUTE', 'ARCHIVE')], default='VALIDATION CAISSE', max_length=255),
        ),
    ]
