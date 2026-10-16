# NER Annotator — Frontend  
  
A customizable Named Entity Recognition (NER) annotation tool built with  
Vue.js (Vue 3 + Quasar). It lets users annotate text with entity labels,  
compare initial and updated annotations, and pairs with the `backend`
Flask backend (port `8081`) which annotates culture-specific items (CSIs)  
in web text.  
  
## Usage  
  
1. **Start Page** — upload or paste a URL/text for annotation.  
2. **Annotation Page**  
   - Select text to create entity annotations  
   - View and edit existing annotations  
   - Track added and removed spans  
   - View explanations for annotations  
3. **Comparison Page** — compare initial and updated annotations side by side.

  
## 1. Install Node 14 via nvm  
  
Node 14 is EOL and the nodejs.org installer may fail — `nvm` fetches working  
binaries directly and lets you keep a newer Node version side-by-side.  
  
**macOS / Linux:**  
  
```sh  
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash  
# restart terminal  [header-3](#header-3)
nvm install 14.21.3  
nvm use 14.21.3  
node -v    # → v14.21.3  
```  
  
**Windows (nvm-windows):**  
  
1. GitHub → `coreybutler/nvm-windows` → Releases → run `nvm-setup.exe`.  
2. If prompted about an existing Node install, choose **adopt/Yes**.  
3. Open a **new terminal as Administrator**, then:  
  
```bat  
nvm install 14.21.3  
nvm use 14.21.3  
node -v   # → v14.21.3  
npm install -g yarn  
yarn -v   # → 1.22.x  
```  
  
> **Note:** global npm packages are **per Node version** under nvm — you must  
> run `npm install -g yarn` *while* `nvm use 14.21.3` is active, in an  
> admin terminal.  
  
## 2. Run the App  
  
```sh  
cd ner-annotator  
yarn --ignore-engines   # needed on Node 14 — see Troubleshooting  
yarn serve  
```  
  
Open the URL printed under `App running at:` — it **must include the `/ner-annotator/` suffix** because `publicPath` is `/ner-annotator/` in `vue.config.js`.  
- e.g. `http://localhost:8080/ner-annotator/`  
- If 8080 is busy, it auto-bumps to 8081/8082 — use whatever is printed.  

### Try the Application
Once NER Annotator opens in your browser, select a country, age group, region and paste one of these sample URLs into the input field:
- https://www.bbc.com/news/world-us-canada-67285325
- https://www.bbc.com/news/world-us-canada-67949560
- https://abcnews.go.com/US/culture-wars-identity-center-politics-america/story?id=100768380
- https://www.thenationalnews.com/lifestyle/food/2024/09/19/michelin-guide-abu-dhabi-food-festival/
- https://www.dayoutdubai.ae/blog/safari/traditional-food-of-uae/
- https://www.khaleejtimes.com/uae/education/in-love-with-arab-culture-why-abu-dhabi-is-attracting-students-from-the-us

Then click the arrow button to analyze the article.


## 3. Backend
  
URL analysis requires the Flask backend. It **must** bind port **8081**  
because `src/components/StartPage.vue` hardcodes  
`fetch("http://127.0.0.1:8081/gateway")`.  
  
> **Startup order matters:** start `backend` FIRST (it takes 8081), then run
> `yarn serve` — otherwise the frontend grabs 8081 and Flask fails to bind.  
  
```sh  
# Terminal 1 — backend  [header-4](#header-4)
cd backend
python -m app.main          # occupies 0.0.0.0:8081
# verify: http://127.0.0.1:8081/live → {"health_status":"live"}  [header-5](#header-5)
  
# Terminal 2 — frontend  [header-6](#header-6)
cd ner-annotator  
yarn serve                  # lands on 8080 or 8082 — either works  
```  
  
No config needed — the frontend calls `127.0.0.1:8081` regardless of its own port.  
  
## Troubleshooting  
  
### `'"node"' is not recognized` when running `yarn`  
  
`node.exe` isn't on PATH **in that terminal**. Causes and fixes:  
  
- Terminal opened *before* `nvm use 14.21.3` → close ALL terminals/VS Code,  
  reopen as admin, re-run `nvm use 14.21.3`.  
- Yarn was installed under a different Node version → run  
  `npm install -g yarn` after `nvm use 14.21.3`.  
- Diagnose in the same terminal: `node -v`, `where node`, `where yarn`.  
  
### `error commander@11.1.0: The engine "node" is incompatible... Expected ">=16"`  
  
A transitive dep now requires Node ≥16 (no `yarn.lock` exists — the repo ships  
only `package-lock.json`, so yarn resolves `^` ranges to newest versions).  
  
```sh  
yarn --ignore-engines  
  
# or persist it:  [header-7](#header-7)
yarn config set ignore-engines true && yarn  
```  
  
### Frontend opened on 8081; backend fails with "access a socket in a way forbidden"  
  
Port conflict — the frontend stole the backend's 8081. Stop `yarn serve`  
(Ctrl+C), start `python -m app.main` first, then restart `yarn serve`.
  
```bat  
netstat -ano | findstr ":808"      :: find the PID  
taskkill /PID <pid> /F             :: kill it if needed  
```  
  
### Blank page after submitting a URL  
  
Backend `POST /gateway` returns `null`. Resolved by the backend-side  
`backend_endpoint` default in `backend/app/main.py`.
If it recurs, check DevTools → Network → the `/gateway` response body.  
  
### Cosmetic warnings on `yarn serve` — safe to ignore  
  
- 136 eslint warnings (indentation, attribute order)  
- Sass `slash-div` deprecations from `node_modules/quasar`  
- `caniuse-lite is outdated`