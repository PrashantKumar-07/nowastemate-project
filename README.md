# NoWasteMate: An Integrated Food Rescue Platform

NoWasteMate is a mature, web-based platform designed to bridge the critical logistical gap between institutional food surplus (from college messes, canteens, etc.) and local food insecurity (faced by NGOs and shelters).

This platform acts as an intelligent, real-time hub to ensure that potential food waste is efficiently and reliably redirected to those in need, building a more sustainable and supportive community.

## 🚀 Project Goals & Quality Focus

The project's development focused on key software quality attributes (as defined by ISO/IEC 25010). Initially, the focus was on **Functional Suitability** to build a secure, reliable, and 100% functional application with all core features.

Subsequently, the project evolved to enhance **Usability** and **Performance Efficiency**. This resulted in a mature, professional-grade application that is "smart" (proactive notifications), "trustworthy" (bi-directional ratings), and "insightful" (data analytics).

## ✨ Key Features

### Advanced Features

  * **Impact Analytics Dashboard:** A data-driven dashboard demonstrating high performance. It runs complex, real-time aggregation queries on the PostgreSQL database to visualize key metrics:
      * Total Donations Completed
      * Top 5 Donors (Bar Chart)
      * Donations Over Last 30 Days (Line Chart)
      * Average User Ratings
  * **Real-Time Notification System:** A proactive "push" model to enhance usability. Users receive in-app and email notifications for critical events:
      * NGOs are alerted when a new donation is posted.
      * Donors are alerted when their donation is claimed.
      * Users are alerted when their review is received or their account is approved.
  * **Bi-directional User Ratings:** A trust-building system. After a donation is marked "Completed," both the Donor and the NGO can rate each other (1-5 stars) and leave a comment, building platform-wide accountability.

### Core Features

  * **Role-Based Registration:** Separate, intuitive registration flows for "Donors" (food providers) and "NGOs" (charities).
  * **Admin Verification System:** A critical security feature. New users cannot log in until an administrator manually reviews and approves their account via the Django admin panel.
  * **Complete Donation Lifecycle:** A robust state-tracking system for all donations: `Available` -\> `Claimed` -\> `Completed`.
  * **Personalized User Dashboards:** Role-specific dashboards for Donors (to track their posts) and NGOs (to track their claims).
  * **Modern UI:** A clean, professional, and responsive user interface built with Bootstrap 5, including custom-designed login and registration pages.

## 🏛️ System Architecture

The application is built using Django's **Model-Template-View (MTV)** architecture, ensuring a clean separation of concerns for high maintainability.

  * **Model:** The logical data structure (the "data layer"), defined in `core/models.py`. This includes tables like `UserProfile`, `Donation`, `Review`, and `Notification`, all managed in PostgreSQL.
  * **Template:** The presentation layer (the "frontend"), comprised of HTML files and Bootstrap 5.
  * **View:** The business logic (the "backend"), defined in `core/views.py`. This is the "brain" that handles all HTTP requests, interacts with the Models, and renders the Templates.

## 🛠️ Technology Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | Python (v3.10), Django (v5.2) |
| **Database** | PostgreSQL (Migrated from SQLite for scalability) |
| **Frontend** | HTML5, CSS3, Bootstrap 5 |
| **Visualization** | JavaScript (Chart.js) |
| **Testing** | Django's built-in Test Suite |
| **Version Control** | Git & GitHub |

## ⚙️ Setup and Installation

To get a local copy up and running, follow these steps.

### Prerequisites

  * Python (3.8+)
  * pip
  * PostgreSQL (running as a service)

### Installation

1.  Clone the repository:

    ```bash
    git clone https://github.com/PrashantKumar-07/nowastemate-project.git
    cd nowastemate-project
    ```

2.  Create and activate a virtual environment:

    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate  # Mac/Linux
    ```

3.  Install dependencies:

    ```bash
    # Install Django and the PostgreSQL connector
    pip install django psycopg2-binary
    ```

4.  **Configure Database:**

      * Create a new PostgreSQL database (e.g., `nowastemate_db`).
      * Open `nowastemate/settings.py` and update the `DATABASES` setting with your PostgreSQL credentials (User, Password, Host, Port).

5.  Apply database migrations:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6.  Create a superuser (for admin access):

    ```bash
    python manage.py createsuperuser
    ```

7.  Run the server:

    ```bash
    python manage.py runserver
    ```

8.  Navigate to `http://127.0.0.1:8000` in your browser.

## 🧪 Running Tests

This project includes an automated test suite to ensure maintainability and code quality. To run the tests:

```bash
python manage.py test core
```

## 📁 Project Structure

```
nowastemate-project/
├── core/                   # Main Django app
│   ├── models.py           # Database models (UserProfile, Donation, Review, Notification)
│   ├── views.py            # View functions for handling requests
│   ├── forms.py            # Custom forms
│   ├── urls.py             # URL patterns
│   ├── admin.py            # Admin interface configuration
│   ├── tests.py            # Automated unit tests
│   ├── templates/core/     # HTML templates
│   └── migrations/         # Database migrations
├── nowastemate/            # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py               # Django management script
└── README.md
```

## Future Work

  * **Geolocation & Route Optimization:** Implement a map-based "Donation Cart" for NGOs to claim multiple donations and calculate the most efficient pickup route.
  * **"Smart Matching" / NGO Needs Profile:** Allow NGOs to specify their needs (e.g., "only vegetables," "needs 50+ meals"). Notifications would then be intelligently routed only to NGOs whose needs match the donation.
  * **Deployment:** Move the application to a public cloud-hosting platform (like Heroku or AWS) and configure a real email service (like SendGrid) for production use.

## Contributing

1.  Fork the repository
2.  Create a feature branch
3.  Make your changes
4.  Test thoroughly
5.  Submit a pull request

## 📄 License

This project is licensed under the MIT License.