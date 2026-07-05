from django.core.management.base import BaseCommand
import requests
from io import BytesIO
from PIL import Image
from portfolio.models import Brand

class Command(BaseCommand):
    help = 'Add sample brands to the database'

    def handle(self, *args, **options):
        sample_brands = [
            {
                'name': 'Nike',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/a/a6/Logo_NIKE.svg',
                'order': 1
            },
            {
                'name': 'Apple',
                'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg',
                'order': 2
            },
            # ... rest of brands
        ]

        self.stdout.write(self.style.SUCCESS('Adding sample brands...'))
        
        for brand_data in sample_brands:
            try:
                if Brand.objects.filter(name=brand_data['name']).exists():
                    self.stdout.write(f"Brand '{brand_data['name']}' already exists, skipping...")
                    continue
                
                self.stdout.write(f"Downloading logo for {brand_data['name']}...")
                response = requests.get(brand_data['logo_url'], timeout=10)
                response.raise_for_status()
                
                if brand_data['logo_url'].endswith('.svg'):
                    try:
                        img = Image.open(BytesIO(response.content))
                        if img.mode == 'RGBA':
                            img = img.convert('RGB')
                        
                        img_io = BytesIO()
                        img.save(img_io, 'PNG')
                        img_io.seek(0)
                        
                        filename = f"{brand_data['name'].lower().replace(' ', '_')}.png"
                        brand = Brand.objects.create(
                            name=brand_data['name'],
                            order=brand_data['order'],
                            is_active=True
                        )
                        brand.logo.save(filename, img_io, save=True)
                        self.stdout.write(self.style.SUCCESS(f"✓ Added brand: {brand_data['name']}"))
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Failed to convert SVG for {brand_data['name']}: {e}"))
                else:
                    filename = f"{brand_data['name'].lower().replace(' ', '_')}.png"
                    brand = Brand.objects.create(
                        name=brand_data['name'],
                        order=brand_data['order'],
                        is_active=True
                    )
                    brand.logo.save(filename, BytesIO(response.content), save=True)
                    self.stdout.write(self.style.SUCCESS(f"✓ Added brand: {brand_data['name']}"))
                    
            except requests.RequestException as e:
                self.stdout.write(self.style.ERROR(f"Failed to download logo for {brand_data['name']}: {e}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed to add brand {brand_data['name']}: {e}"))
        
        self.stdout.write(self.style.SUCCESS("Done! Sample brands have been added."))