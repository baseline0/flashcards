# GitHub Pages Deployment

This project includes automated GitHub Pages deployment. The landing page showcases the flashcards project and provides quick navigation to the repository and documentation.

## Setup

After pushing to GitHub, enable GitHub Pages in your repository settings:

1. Go to **Settings** → **Pages**
2. Under "Build and deployment", select:
   - **Source**: Deploy from a branch
   - **Branch**: `main` (or `master`)
   - **Folder**: `/docs`
3. Click **Save**

GitHub Pages will automatically deploy whenever you push changes to the `docs/` folder.

## Architecture

- **`docs/index.html`** — Landing page with features, quick start, and demo info
- **`.nojekyll`** — Tells GitHub Pages to skip Jekyll processing
- **`.github/workflows/deploy-pages.yml`** — Automated deployment workflow

## Automatic Deployment

The GitHub Actions workflow (`deploy-pages.yml`) will:

- **Trigger on:** Push to `main`/`master` branch (if `docs/` changes)
- **Manual trigger:** Click "Run workflow" in GitHub Actions tab
- **Deploy to:** `https://baseline0.github.io/flashcards/` (or your custom domain)

## Customization

To customize the landing page:

1. Edit `docs/index.html` directly
2. Commit and push to `main`
3. Wait ~1 minute for deployment
4. Visit your GitHub Pages URL

## Custom Domain (Optional)

To use a custom domain (e.g., `flashcards.example.com`):

1. Create a `docs/CNAME` file with your domain
2. Update DNS records to point to GitHub Pages
3. Enable HTTPS in repository settings

See [GitHub Pages documentation](https://docs.github.com/en/pages) for details.
