import esbuild from "esbuild";
import fs from "fs";
import path from "path";

async function build() {
  if (!fs.existsSync("dist")) {
    fs.mkdirSync("dist", { recursive: true });
  }

  await esbuild.build({
    entryPoints: ["src/main.jsx"],
    bundle: true,
    outfile: "dist/bundle.js",
    jsx: "automatic",
    loader: { ".js": "jsx" },
    minify: false,
    sourcemap: true,
  });

  let html = fs.readFileSync("index.html", "utf8");
  html = html.replace(
    '<script type="module" src="/src/main.jsx"></script>',
    '<link rel="stylesheet" href="/bundle.css">\n    <script type="module" src="/bundle.js"></script>'
  );
  fs.writeFileSync("dist/index.html", html);
  console.log("Frontend built successfully in dist/");
}

build().catch((err) => {
  console.error(err);
  process.exit(1);
});
