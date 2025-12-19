# Welcome to [Slidev](https://github.com/slidevjs/slidev)!

To start the slide show:

- `pnpm install`
- `pnpm dev`
- visit <http://localhost:3030>

Edit the [slides.md](./slides.md) to see the changes.

Learn more about Slidev at the [documentation](https://sli.dev/).



### 1. Instal npm and Node.js
```
sudo apt install -y npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

or

```
sudo apt install nodejs npm
```

### 2. Make new Slidev project
```
npm init slidev@latest my-slidev
```

**note*** my-sliver is your project name

```
cd my-slidev
```

### 3. Run Slidev locally
```
npm run dev
```
it will appear here 
`http://localhost:3030/`

### 4. Build static
```
npm run build
```
or

```
NODE_OPTIONS="--max-old-space-size=4096" npm run build

```
dist folder will appear

### 5. add git action folder and workflow file

```
cd my-slidev
mkdir -p .github/workflows
```

### 6. add workflow file
make new file
```
touch .github/workflows/deploy.yml

```
open it
```
nano.github/workflows/deploy.yml

```
and put this sintax
```
name: Deploy Slidev to GitHub Pages
on:
  push:
    branches: [ main ]

jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist

```


or example single slide deploy

```
name: Deploy Slidev to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  build-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
      - name: Install dependencies
        working-directory: ./Algo2/algo2-slidev
        run: npm install
      - name: Build Slidev
        working-directory: ./Algo2/algo2-slidev
        # base path di-set ke /TEUKU_zikri/ agar cocok dengan GitHub Pages
        run: npm run build -- --base /TEUKU_zikri/
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          personal_token: ${{ secrets.PERSONAL_TOKEN }}
          publish_dir: ./Algo2/algo2-slidev/dist
          publish_branch: gh-pages
          user_name: github-actions[bot]
          user_email: github-actions[bot]@users.noreply.github.com

```
example multiple slide deploy
```
name: Deploy Slidev to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  build-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20

      # Build Algo1 Slidev
      - name: Install & build Algo1
        working-directory: ./Algo1/algo1-slidev
        run: |
          npm install
          npm install -D playwright-chromium
          npm run build -- --base /TEUKU_zikri/Algo1/

      # Build Algo2 Slidev
      - name: Install & build Algo2
        working-directory: ./Algo2/algo2-slidev
        run: |
          npm install
          npm install -D playwright-chromium
          npm run build -- --base /TEUKU_zikri/Algo2/

      # Build Algo3 Slidev
      - name: Install & build Algo3
        working-directory: ./Algo3/algo3-slidev
        run: |
          npm install
          npm install -D playwright-chromium
          npm run build -- --base /TEUKU_zikri/Algo3/

      # Build Algo4 Slidev
      - name: Install & build Algo4
        working-directory: ./Algo4/algo4-slidev
        run: |
          npm install
          npm install -D playwright-chromium
          npm run build -- --base /TEUKU_zikri/Algo4/

      # Gabungkan output ke folder publik untuk gh-pages
      - name: Prepare deploy directory
        run: |
          rm -rf public
          mkdir -p public/Algo1 public/Algo2 public/Algo3 public/Algo4

          cp -r Algo1/algo1-slidev/dist/* public/Algo1/
          cp -r Algo2/algo2-slidev/dist/* public/Algo2/
          cp -r Algo3/algo3-slidev/dist/* public/Algo3/
          cp -r Algo4/algo4-slidev/dist/* public/Algo4/

          # index.html di root (optional, daftar link)
          cat > public/index.html << 'EOF'
          <!DOCTYPE html>
          <html lang="en">
          <head>
            <meta charset="UTF-8" />
            <title>TEUKU_zikri Slides</title>
          </head>
          <body>
            <h1>TEUKU_zikri Slidev Collections</h1>
            <ul>
              <li><a href="./Algo1/">Algo1 Slides</a></li>
              <li><a href="./Algo2/">Algo2 Slides</a></li>
              <li><a href="./Algo3/">Algo3 Slides</a></li>
              <li><a href="./Algo4/">Algo4 Slides</a></li>
            </ul>
          </body>
          </html>
          EOF

      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          personal_token: ${{ secrets.PERSONAL_TOKEN }}
          publish_dir: ./public
          publish_branch: gh-pages
          user_name: github-actions[bot]
          user_email: github-actions[bot]@users.noreply.github.com

```

push it to github
### 7. Activate GitHub Pages
Go to your repository page on GitHub.

Click Settings → Pages.

In the Build and deployment section, select:

Source: “Deploy from a branch”

Branch: gh-pages

Then click Save.

### 8. Result

Wait for 1–2 minutes

GitHub will automatically build your Slidev project.

Once it’s done, you’ll get a link like this:

`https://username.github.io/your-repo-name/`


