import os
import django
import requests
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vitamin_backend.settings')
django.setup()

from portfolio.models import Brand

# Sample brand data with logo URLs
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
    {
        'name': 'Google',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/2/2f/Google_2015_logo.svg',
        'order': 3
    },
    {
        'name': 'Amazon',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/a/a9/Amazon_logo.svg',
        'order': 4
    },
    {
        'name': 'Meta',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/7/7b/Meta_Platforms_Inc._logo.svg',
        'order': 5
    },
    {
        'name': 'Netflix',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/0/08/Netflix_2015_logo.svg',
        'order': 6
    },
    {
        'name': 'Spotify',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/2/26/Spotify_logo_with_text.svg',
        'order': 7
    },
    {
        'name': 'Airbnb',
        'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/6/69/Airbnb_Logo_B%C3%A9lo.svg',
        'order': 8
    }
]

def add_sample_brands():
    """Add sample brands to the database"""
    print("Adding sample brands...")
    
    for brand_data in sample_brands:
        try:
            # Check if brand already exists
            if Brand.objects.filter(name=brand_data['name']).exists():
                print(f"Brand '{brand_data['name']}' already exists, skipping...")
                continue
            
            # Download the logo image
            print(f"Downloading logo for {brand_data['name']}...")
            response = requests.get(brand_data['logo_url'], timeout=10)
            response.raise_for_status()
            
            # Convert to PNG if it's SVG (Django ImageField works better with raster formats)
            if brand_data['logo_url'].endswith('.svg'):
                # For SVG, we'll save it as-is but Django might need special handling
                # Let's try to convert it to PNG using PIL
                try:
                    img = Image.open(BytesIO(response.content))
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    
                    # Save to BytesIO
                    img_io = BytesIO()
                    img.save(img_io, 'PNG')
                    img_io.seek(0)
                    
                    # Create filename
                    filename = f"{brand_data['name'].lower().replace(' ', '_')}.png"
                    
                    # Create brand with image
                    brand = Brand.objects.create(
                        name=brand_data['name'],
                        order=brand_data['order'],
                        is_active=True
                    )
                    brand.logo.save(filename, img_io, save=True)
                    print(f"✓ Added brand: {brand_data['name']}")
                    
                except Exception as e:
                    print(f"✗ Failed to convert SVG for {brand_data['name']}: {e}")
                    # Fallback: save as SVG directly
                    filename = f"{brand_data['name'].lower().replace(' ', '_')}.svg"
                    brand = Brand.objects.create(
                        name=brand_data['name'],
                        order=brand_data['order'],
                        is_active=True
                    )
                    brand.logo.save(filename, BytesIO(response.content), save=True)
                    print(f"✓ Added brand: {brand_data['name']} (SVG)")
            else:
                # For non-SVG images
                filename = f"{brand_data['name'].lower().replace(' ', '_')}.png"
                brand = Brand.objects.create(
                    name=brand_data['name'],
                    order=brand_data['order'],
                    is_active=True
                )
                brand.logo.save(filename, BytesIO(response.content), save=True)
                print(f"✓ Added brand: {brand_data['name']}")
                
        except requests.RequestException as e:
            print(f"✗ Failed to download logo for {brand_data['name']}: {e}")
        except Exception as e:
            print(f"✗ Failed to add brand {brand_data['name']}: {e}")
    
    print("\nDone! Sample brands have been added to the database.")

if __name__ == '__main__':
    add_sample_brands()
