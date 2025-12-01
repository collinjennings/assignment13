"""
Playwright E2E tests for FastAPI Calculator authentication.
These tests match your actual HTML templates with JavaScript form submissions.
"""
import pytest
from playwright.sync_api import Page, expect
from faker import Faker
import time

fake = Faker()


def test_registration_flow(page: Page, fastapi_server: str):
    """
    Test complete user registration flow.
    Your form uses JavaScript fetch() to submit, so we wait for network response.
    """
    # Generate unique test data
    username = f"testuser_{fake.random_int(min=1000, max=9999)}"
    email = f"{username}@example.com"
    password = "TestPass123!"
    first_name = fake.first_name()
    last_name = fake.last_name()
    
    print(f"\n🔍 Testing registration for: {username}")
    
    # Navigate to registration page
    page.goto(f"{fastapi_server}register")
    page.wait_for_load_state("networkidle")
    
    # Verify we're on the registration page
    expect(page).to_have_title("Register")
    expect(page.locator("h2")).to_contain_text("Create Account")
    
    # Fill out the registration form (matching your HTML id attributes)
    page.fill('#username', username)
    page.fill('#email', email)
    page.fill('#first_name', first_name)
    page.fill('#last_name', last_name)
    page.fill('#password', password)
    page.fill('#confirm_password', password)
    
    print("✓ Filled registration form")
    
    # Click the register button
    page.click('button[type="submit"]:has-text("Register")')
    
    # Wait for the success message to appear (your JS shows this)
    success_alert = page.locator('#successAlert')
    expect(success_alert).to_be_visible(timeout=5000)
    expect(success_alert).to_contain_text("Registration successful")
    
    print("✓ Registration successful message displayed")
    
    # Wait for automatic redirect to login page (happens after 2 seconds in your JS)
    page.wait_for_url("**/login", timeout=5000)
    expect(page).to_have_title("Login")
    
    print(f"✅ Registration test passed for {username}")


def test_login_flow(page: Page, fastapi_server: str):
    """
    Test complete login flow - register first, then login.
    """
    # Setup: Register a user first
    username = f"loginuser_{fake.random_int(min=1000, max=9999)}"
    email = f"{username}@example.com"
    password = "TestPass123!"
    first_name = "Test"
    last_name = "User"
    
    print(f"\n🔍 Testing login for: {username}")
    
    # Step 1: Register the user
    print("📝 Registering user first...")
    page.goto(f"{fastapi_server}register")
    page.wait_for_load_state("networkidle")
    
    page.fill('#username', username)
    page.fill('#email', email)
    page.fill('#first_name', first_name)
    page.fill('#last_name', last_name)
    page.fill('#password', password)
    page.fill('#confirm_password', password)
    page.click('button[type="submit"]:has-text("Register")')
    
    # Wait for redirect to login
    page.wait_for_url("**/login", timeout=5000)
    print("✓ User registered successfully")
    
    # Step 2: Now test login
    print("🔐 Testing login...")
    
    # Fill login form
    page.fill('#username', username)
    page.fill('#password', password)
    
    # Click sign in button
    page.click('button[type="submit"]:has-text("Sign in")')
    
    # Wait for success message
    success_alert = page.locator('#successAlert')
    expect(success_alert).to_be_visible(timeout=5000)
    expect(success_alert).to_contain_text("Login successful")
    
    print("✓ Login successful message displayed")
    
    # Wait for redirect to dashboard (happens after 1 second in your JS)
    page.wait_for_url("**/dashboard", timeout=5000)
    
    print(f"✅ Login test passed for {username}")


def test_login_with_invalid_credentials(page: Page, fastapi_server: str):
    """
    Test that invalid credentials show an error message.
    """
    print("\n🔍 Testing invalid login")
    
    page.goto(f"{fastapi_server}login")
    page.wait_for_load_state("networkidle")
    
    # Try to login with invalid credentials
    page.fill('#username', "nonexistent_user_12345")
    page.fill('#password', "wrongpassword")
    page.click('button[type="submit"]:has-text("Sign in")')
    
    # Wait for error alert to appear
    error_alert = page.locator('#errorAlert')
    expect(error_alert).to_be_visible(timeout=5000)
    expect(error_alert).to_contain_text("Invalid username or password")
    
    # Should still be on login page
    expect(page).to_have_url(f"{fastapi_server}login")
    
    print("✅ Invalid login correctly rejected")


def test_registration_with_mismatched_passwords(page: Page, fastapi_server: str):
    """
    Test that mismatched passwords show an error.
    """
    print("\n🔍 Testing mismatched passwords")
    
    page.goto(f"{fastapi_server}register")
    page.wait_for_load_state("networkidle")
    
    username = f"testuser_{fake.random_int(min=1000, max=9999)}"
    
    page.fill('#username', username)
    page.fill('#email', f"{username}@example.com")
    page.fill('#first_name', "Test")
    page.fill('#last_name', "User")
    page.fill('#password', "TestPass123!")
    page.fill('#confirm_password', "DifferentPass123!")
    
    page.click('button[type="submit"]:has-text("Register")')
    
    # Wait for error alert
    error_alert = page.locator('#errorAlert')
    expect(error_alert).to_be_visible(timeout=5000)
    expect(error_alert).to_contain_text("Passwords do not match")
    
    # Should still be on register page
    expect(page).to_have_url(f"{fastapi_server}register")
    
    print("✅ Mismatched passwords correctly rejected")


def test_registration_with_weak_password(page: Page, fastapi_server: str):
    """
    Test that weak passwords are rejected.
    """
    print("\n🔍 Testing weak password validation")
    
    page.goto(f"{fastapi_server}register")
    page.wait_for_load_state("networkidle")
    
    username = f"testuser_{fake.random_int(min=1000, max=9999)}"
    weak_password = "weak"  # Too short, no uppercase, no numbers
    
    page.fill('#username', username)
    page.fill('#email', f"{username}@example.com")
    page.fill('#first_name', "Test")
    page.fill('#last_name', "User")
    page.fill('#password', weak_password)
    page.fill('#confirm_password', weak_password)
    
    page.click('button[type="submit"]:has-text("Register")')
    
    # Wait for error alert about password requirements
    error_alert = page.locator('#errorAlert')
    expect(error_alert).to_be_visible(timeout=5000)
    expect(error_alert).to_contain_text("Password must be at least 8 characters")
    
    print("✅ Weak password correctly rejected")


def test_page_titles_and_navigation(page: Page, fastapi_server: str):
    """
    Test that all pages load with correct titles and have proper navigation links.
    """
    print("\n🔍 Testing page navigation")
    
    # Test home page
    page.goto(fastapi_server)
    expect(page).to_have_title("Home")
    print("✓ Home page loads")
    
    # Test register page
    page.goto(f"{fastapi_server}register")
    expect(page).to_have_title("Register")
    expect(page.locator("h2")).to_contain_text("Create Account")
    
    # Check for link to login page
    login_link = page.locator('a[href="/login"]')
    expect(login_link).to_be_visible()
    expect(login_link).to_contain_text("Log in")
    print("✓ Register page loads with navigation")
    
    # Test login page
    page.goto(f"{fastapi_server}login")
    expect(page).to_have_title("Login")
    expect(page.locator("h2")).to_contain_text("Welcome Back")
    
    # Check for link to register page
    register_link = page.locator('a[href="/register"]')
    expect(register_link).to_be_visible()
    expect(register_link).to_contain_text("Register now")
    print("✓ Login page loads with navigation")
    
    print("✅ All pages load correctly with navigation")


def test_complete_user_journey(page: Page, fastapi_server: str):
    """
    Test a complete user journey: home -> register -> login -> dashboard.
    """
    username = f"journey_{fake.random_int(min=1000, max=9999)}"
    email = f"{username}@example.com"
    password = "JourneyPass123!"
    
    print(f"\n🔍 Testing complete user journey for: {username}")
    
    # Step 1: Start at home page
    print("📄 Step 1: Visit home page")
    page.goto(fastapi_server)
    expect(page).to_have_title("Home")
    
    # Step 2: Navigate to register page
    print("📄 Step 2: Navigate to register")
    page.goto(f"{fastapi_server}register")
    expect(page).to_have_title("Register")
    
    # Step 3: Register
    print("📝 Step 3: Complete registration")
    page.fill('#username', username)
    page.fill('#email', email)
    page.fill('#first_name', "Journey")
    page.fill('#last_name', "Test")
    page.fill('#password', password)
    page.fill('#confirm_password', password)
    page.click('button[type="submit"]:has-text("Register")')
    
    # Wait for success and redirect
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    page.wait_for_url("**/login", timeout=5000)
    
    # Step 4: Login
    print("🔐 Step 4: Login with new account")
    page.fill('#username', username)
    page.fill('#password', password)
    page.click('button[type="submit"]:has-text("Sign in")')
    
    # Wait for success and redirect to dashboard
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    page.wait_for_url("**/dashboard", timeout=5000)
    
    print(f"✅ Complete user journey successful for {username}")


# Quick standalone tests
def test_quick_registration(page: Page, fastapi_server: str):
    """Quick registration test."""
    username = f"quick_{fake.random_int(min=1000, max=9999)}"
    password = "QuickPass123!"
    
    page.goto(f"{fastapi_server}register")
    page.fill('#username', username)
    page.fill('#email', f"{username}@example.com")
    page.fill('#first_name', "Quick")
    page.fill('#last_name', "Test")
    page.fill('#password', password)
    page.fill('#confirm_password', password)
    page.click('button[type="submit"]:has-text("Register")')
    
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    print(f"✅ Quick registration passed for {username}")


def test_quick_login(page: Page, fastapi_server: str):
    """Quick login test - register then login."""
    username = f"quicklogin_{fake.random_int(min=1000, max=9999)}"
    password = "QuickLogin123!"
    
    # Register
    page.goto(f"{fastapi_server}register")
    page.fill('#username', username)
    page.fill('#email', f"{username}@example.com")
    page.fill('#first_name', "Quick")
    page.fill('#last_name', "Login")
    page.fill('#password', password)
    page.fill('#confirm_password', password)
    page.click('button[type="submit"]:has-text("Register")')
    page.wait_for_url("**/login", timeout=5000)
    
    # Login
    page.fill('#username', username)
    page.fill('#password', password)
    page.click('button[type="submit"]:has-text("Sign in")')
    
    expect(page.locator('#successAlert')).to_be_visible(timeout=5000)
    page.wait_for_url("**/dashboard", timeout=5000)
    
    print(f"✅ Quick login passed for {username}")