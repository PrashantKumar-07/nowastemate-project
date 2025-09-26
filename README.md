# NoWasteMate - A Smart Food Donation Platform

NoWasteMate is a web-based platform designed to connect college messes, canteens, and restaurants with NGOs and community shelters. The primary goal is to efficiently redirect surplus food to those in need, reducing food waste and supporting local communities. This project was developed using Python and the Django framework.

The project's development emphasizes Functional Suitability as defined by the ISO/IEC 25010 software quality model, ensuring that all features are reliable, complete, and operate as intended.

## 🚀 Key Features

- **Role-Based Registration**: Separate, intuitive registration flows for Donors and NGOs, including phone number collection for verification
- **Admin Verification System**: A secure Django admin panel where an administrator must approve all new user accounts before they can log in
- **Detailed Donation Posting**: Donors can post surplus food with specific details, including:
  - Food Item Name
  - Food Category (Cooked Meal, Bakery Goods, Produce, Packaged Items, Other)
  - Quantity
  - "Pickup Before" date and time
  - Pickup Address
- **Visually Rich Donation Listings**: NGOs can browse available donations presented in a modern card-based UI, with clear details and contact information
- **Donation Claiming System**: A simple one-click system for verified NGOs to claim an available donation
- **Personalized User Dashboards**:
  - Donors can track the status of their posted donations and see the contact details of the NGO who claimed their food
  - NGOs can track their claimed donations and see the contact details of the donor for pickup coordination
- **Full-Featured "About Us" and "Contact Us" Pages**: To provide project background, build trust, and offer a clear communication channel

## 🏛️ System Architecture

The application is built using Django's Model-Template-View (MTV) architecture, ensuring a clean separation of concerns:

- **Model**: Defines the database schema for user profiles and food donations
- **View**: Contains the Python logic to handle all user requests and business logic
- **Template**: Renders the user interface using HTML, CSS, and Bootstrap

## 🛠️ Technology Stack

- **Backend**: Python, Django
- **Frontend**: HTML, CSS, Bootstrap 5
- **Database**: SQLite 3
- **Version Control**: Git & GitHub

## ⚙️ Setup and Installation

To get a local copy up and running, follow these steps.

### Prerequisites

- Python (3.8+)
- pip

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/PrashantKumar-07/nowastemate-project.git
   cd nowastemate-project
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Mac/Linux
   ```

3. Install dependencies:
   ```
   pip install django
   ```

4. Apply database migrations:
   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Run the server:
   ```
   python manage.py runserver
   ```

7. Navigate to `http://127.0.0.1:8000` in your browser.

## 📁 Project Structure

```
nowastemate-project/
├── core/                    # Main Django app
│   ├── models.py           # Database models (UserProfile, Donation)
│   ├── views.py            # View functions for handling requests
│   ├── forms.py            # Custom forms
│   ├── urls.py             # URL patterns
│   ├── admin.py            # Admin interface configuration
│   ├── templates/core/     # HTML templates
│   └── migrations/         # Database migrations
├── nowastemate/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py               # Django management script
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
