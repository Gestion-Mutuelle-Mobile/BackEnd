import pandas as pd
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from members.models import User, Member, Administrator

class Command(BaseCommand):
    help = 'Import members from Excel file with default password 0000'

    def handle(self, *args, **options):
        # Chemin vers le fichier Excel (dans le même dossier que manage.py)
        excel_file = 'membres_format_import.xlsx'

        try:
            df = pd.read_excel(excel_file)

            for index, row in df.iterrows():
                data = {
                    "name": row['name'],
                    "first_name": row['first_name'],
                    "email": row['email'],
                    "password": "0000",  # Mot de passe par défaut
                    "type": "member",
                    "sex": "M",  # À ajuster si nécessaire
                    "address": "",
                    "tel": "",
                }

                if User.objects.filter(email=data['email']).exists():
                    self.stdout.write(self.style.WARNING(f'User {data["email"]} already exists'))
                    continue

                try:
                    # Hacher le mot de passe avant création
                    hashed_password = make_password(data['password'])

                    # Création de l'utilisateur avec mot de passe haché
                    user = User.objects.create(
                        first_name=data['first_name'],
                        name=data['name'],
                        email=data['email'],
                        password=hashed_password,
                        sex=data['sex'],
                        tel=data['tel'],
                        address=data['address'],
                        type=data['type'],
                        create_at=timezone.now()
                    )

                    # Création du membre associé
                    admin = Administrator.objects.first()
                    if not admin:
                        raise Exception("No administrator found in database")

                    Member.objects.create(
                        user_id=user,
                        username=data['name'],
                        administrator_id=admin,
                        active=True,
                        inscription="10000.00"
                    )

                    self.stdout.write(self.style.SUCCESS(
                        f'Successfully created {data["email"]} with password 0000'
                    ))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error creating {data["email"]}: {str(e)}'))

            self.stdout.write(self.style.SUCCESS('Import completed successfully'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error reading Excel file: {str(e)}'))