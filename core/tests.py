import time
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from core.models import UserProfile, Donation, Review
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from django.utils import timezone
from django.db.models import Avg
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DRIVER_PATH = r'D:\Downloads\edgedriver_win64\msedgedriver.exe'

class TestE2EWorkflows(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        service = Service(DRIVER_PATH)
        cls.driver = webdriver.Edge(service=service)
        cls.driver.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.donor_user = User.objects.create_user(
            username='testdonor',
            password='testpass123',
            email='donor@test.com'
        )
        self.donor_profile = UserProfile.objects.create(
            user=self.donor_user,
            role='donor',
            phone_number='1111111111',
            is_approved=True
        )

        self.ngo_user = User.objects.create_user(
            username='testngo',
            password='testpass123',
            email='ngo@test.com'
        )
        self.ngo_profile = UserProfile.objects.create(
            user=self.ngo_user,
            role='ngo',
            phone_number='2222222222',
            is_approved=True
        )

    def test_login_fail_wrong_password(self):
        self.driver.get(f"{self.live_server_url}/login/")
        self.driver.find_element(By.NAME, "username").send_keys("testdonor")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpassword")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        alert = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
        )
        self.assertIn("Please enter a correct username and password.", alert.text)

    def test_login_fail_unapproved_user(self):
        unapproved_user = User.objects.create_user(
            username='newuser',
            password='testpass123'
        )
        UserProfile.objects.create(
            user=unapproved_user,
            role='donor',
            phone_number='3333333333',
            is_approved=False
        )

        self.driver.get(f"{self.live_server_url}/login/")
        self.driver.find_element(By.NAME, "username").send_keys("newuser")
        self.driver.find_element(By.NAME, "password").send_keys("testpass123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        alert = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
        )
        self.assertIn("Your account is pending approval", alert.text)

    def test_data_analytics_page_accuracy(self):
        donation = Donation.objects.create(
            donor=self.donor_user,
            food_item="Test Data Donation",
            category="packaged",
            quantity="100",
            pickup_location="Test",
            status="completed",
            pickup_by=timezone.now()
        )

        Review.objects.create(
            donation=donation,
            reviewer=self.ngo_user,
            reviewed_user=self.donor_user,
            rating=3
        )

        self.donor_profile.recalculate_rating()

        self.driver.get(f"{self.live_server_url}/login/")
        self.driver.find_element(By.NAME, "username").send_keys("testdonor")
        self.driver.find_element(By.NAME, "password").send_keys("testpass123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        self.driver.get(f"{self.live_server_url}/impact/")

        total_donations = self.driver.find_element(By.ID, "total_donations").text
        total_donors = self.driver.find_element(By.ID, "total_donors").text
        avg_donor_rating = self.driver.find_element(By.ID, "avg_donor_rating").text

        expected_total_donations = str(Donation.objects.filter(status='completed').count())
        expected_total_donors = str(UserProfile.objects.filter(role='donor', is_approved=True).count())

        avg_val = UserProfile.objects.filter(role='donor').aggregate(
            Avg('average_rating')
        )['average_rating__avg'] or 0.0
        expected_avg = f"{avg_val:.1f}"

        self.assertEqual(total_donations, expected_total_donations)
        self.assertEqual(total_donors, expected_total_donors)
        self.assertEqual(avg_donor_rating, expected_avg)
