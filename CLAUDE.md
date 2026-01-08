# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Jekyll-based personal resume website hosted on GitHub Pages. The site is a static resume template that uses YAML data files to populate content dynamically through Jekyll's Liquid templating system.

## Development Commands

### Local Development
```bash
bundle install                    # Install dependencies
bundle exec jekyll serve          # Start local server at localhost:4000
```

**Important**: Changes to `_config.yml` require restarting the Jekyll server to take effect.

### Branch Information
- Primary branch: `gh-pages` (GitHub Pages deployment branch)
- Site is automatically deployed when changes are pushed to `gh-pages`

## Architecture

### Content Data Structure
All resume content is stored in YAML files in `/_data/`:
- `experience.yml` - Work history with company, position, duration, and summary
- `education.yml` - Educational background
- `skills.yml` - Technical skills and descriptions
- `projects.yml` - Personal projects (optional section)
- `recognitions.yml` - Awards and recognition (optional section)
- `associations.yml` - Professional associations (optional section)
- `interests.yml` - Personal interests (optional section)
- `links.yml` - Additional links (optional section)

### Layout System
- `/_layouts/resume.html` - Main resume layout that renders all sections conditionally based on `_config.yml` flags
- `/index.html` - Entry point (minimal, just specifies layout)
- `/_includes/` - Reusable components (head, icon links, social links)

### Styling Architecture
SCSS files in `/_sass/` are imported via `/css/main.scss`:
- `_normalize.scss` - CSS reset
- `_variables.scss` - SASS variables for theming
- `_mixins.scss` - Reusable SASS mixins
- `_base.scss` - Base element styles
- `_layout.scss` - Layout structure
- `_resume.scss` - Resume-specific styles

### Configuration (`_config.yml`)
Controls all site metadata and resume sections:
- Personal info: name, title, contact details, bio
- Section toggles: Enable/disable sections by commenting out flags (e.g., `resume_section_projects`)
- Social links: Configure which social media links to display
- Theme: Currently uses `default` theme

## Key Patterns

### Adding/Editing Resume Content
1. Edit the appropriate YAML file in `/_data/`
2. Follow the existing data structure (array of objects with specific keys)
3. HTML markup is supported in summary/description fields using `>` multiline syntax
4. Tech stack is typically added as a paragraph at the end of summaries

### Conditional Section Rendering
Sections are rendered only if their flag is set in `_config.yml`:
```yaml
resume_section_experience: true   # Shows section
# resume_section_projects: true   # Commented = hidden
```

### Print Optimization
- Classes with `no-print` are hidden when printing
- Classes with `print-only` are only visible when printing
- Avatar and interactive elements are hidden in print view

## File Organization
```
/
├── _config.yml          # Site configuration and resume metadata
├── _data/              # Resume content (YAML)
├── _layouts/           # HTML templates
├── _includes/          # Reusable HTML components
├── _sass/              # SCSS partials
├── css/                # Main SCSS entry point
├── images/             # Images (avatar, favicon)
└── index.html          # Site entry point
```
