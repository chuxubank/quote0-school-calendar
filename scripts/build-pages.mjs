import { cp, mkdir, rm, writeFile } from "node:fs/promises";
import { pathToFileURL } from "node:url";
import path from "node:path";

const root = process.cwd();
const clientDirectory = path.join(root, "dist", "client");
const outputDirectory = path.join(root, "dist", "pages");
const workerUrl = pathToFileURL(path.join(root, "dist", "server", "index.js"));
workerUrl.searchParams.set("pages-build", String(Date.now()));

const { default: worker } = await import(workerUrl.href);
const response = await worker.fetch(
  new Request("http://localhost/", { headers: { accept: "text/html" } }),
  {
    ASSETS: {
      fetch: async () => new Response("Not found", { status: 404 }),
    },
  },
  {
    waitUntil() {},
    passThroughOnException() {},
  },
);

if (!response.ok) {
  throw new Error(`Unable to render the landing page: HTTP ${response.status}`);
}

const html = await response.text();
if (!html.includes("沪上校历") || !html.includes("/_next/")) {
  throw new Error("Rendered landing page is missing expected content or assets");
}

await rm(outputDirectory, { recursive: true, force: true });
await mkdir(outputDirectory, { recursive: true });
await cp(clientDirectory, outputDirectory, { recursive: true });
await writeFile(path.join(outputDirectory, "index.html"), html);
await writeFile(path.join(outputDirectory, "404.html"), html);
await writeFile(path.join(outputDirectory, ".nojekyll"), "");

console.log(outputDirectory);
