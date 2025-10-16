### 1. Instal npm and Node.js
```
sudo apt install -y npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
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