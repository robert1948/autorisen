# Split the original app.css content into SCSS module files

scss_files = {
    "_buttons.scss": """
.hero-button,
.btn-hero {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
  background-color: #ffc107;
  color: #212529;
  border: none;
  border-radius: 0.5rem;
  text-decoration: none;
  transition: all 0.2s ease-in-out;
}
.hero-button:hover,
.btn-hero:hover {
  background-color: #e0a800;
  color: #212529;
}
""",
    "_layout.scss": """
.fullscreen-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 1.5rem;
  background-color: #fff;
}
.centered-content {
  text-align: center;
  max-width: 640px;
  margin: auto;
  padding: 2rem 1rem;
}
""",
    "_navbar.scss": """
.navbar-dark .navbar-brand {
  font-size: 1.8rem;
  font-weight: 600;
  color: #ff5722;
  transition: color 0.3s ease;
}
.navbar-dark .navbar-brand:hover {
  color: #2ae619;
}
.navbar-dark .navbar-nav .nav-link {
  font-size: 1.15rem;
  color: #ff5722;
  padding: 0.5rem 1rem;
  transition: color 0.3s ease;
}
.navbar-dark .navbar-nav .nav-link:hover {
  color: #22ff6c;
}
""",
    "_responsive.scss": """
@media (max-width: 575.98px) {
  .fullscreen-container {
    align-items: flex-start;
    padding-top: 2rem;
    min-height: auto;
  }
  .title {
    font-size: 2.25rem;
  }
  .subtitle {
    font-size: 1.125rem;
  }
  .homepage-header {
    padding: 2rem 1rem;
  }
}
@media (min-width: 576px) and (max-width: 991.98px) {
  .title {
    font-size: 3rem;
  }
  .subtitle {
    font-size: 1.4rem;
  }
  .homepage-header {
    padding: 3rem 1.5rem;
  }
}
@media (min-width: 992px) {
  .fullscreen-container {
    padding: 0 3rem;
  }
  .title {
    font-size: 4.5rem;
  }
  .homepage-header {
    padding: 5rem 2rem;
  }
}
""",
    "_typography.scss": """
.title {
  font-size: 3.5rem;
  font-weight: 700;
  color: #007bff;
  margin-bottom: 0.5rem;
}
.subtitle {
  font-size: 1.25rem;
  color: #6c757d;
}
.homepage-header {
  background-color: #212529;
  color: #fff;
  padding: 4rem 1.5rem;
  text-align: center;
}
.homepage-header h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}
""",
    "app.scss": """
@import 'buttons';
@import 'layout';
@import 'navbar';
@import 'responsive';
@import 'typography';
"""
}

# Output as confirmation
import pandas as pd

df_scss = pd.DataFrame({"SCSS Files": list(scss_files.keys())})
