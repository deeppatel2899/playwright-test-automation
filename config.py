"""Central settings. Every value can be overridden with an environment variable,
so the same suite can point at another environment without code changes."""

import os

UI_BASE_URL = os.getenv("UI_BASE_URL", "https://www.saucedemo.com")
API_BASE_URL = os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")

# Public demo credentials published by each site.
STANDARD_USER = os.getenv("STANDARD_USER", "standard_user")
LOCKED_OUT_USER = os.getenv("LOCKED_OUT_USER", "locked_out_user")
PROBLEM_USER = os.getenv("PROBLEM_USER", "problem_user")
PERFORMANCE_GLITCH_USER = os.getenv("PERFORMANCE_GLITCH_USER", "performance_glitch_user")
UI_PASSWORD = os.getenv("UI_PASSWORD", "secret_sauce")

API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "password123")
