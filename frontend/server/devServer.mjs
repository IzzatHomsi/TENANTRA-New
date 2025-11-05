import express from "express";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { createServer as createViteServer } from "vite";
import { renderToPipeableStream } from "react-dom/server";
import { dehydrate } from "@tanstack/react-query";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");

async function createServer() {
  const app = express();
  app.disable("x-powered-by");

  app.use(
    "/catalog-remote",
    express.static(path.resolve(rootDir, "dist/catalog-remote"), {
      immutable: true,
      maxAge: "1h",
    })
  );

  const vite = await createViteServer({
    root: rootDir,
    server: { middlewareMode: true },
    appType: "custom",
  });

  app.use(vite.middlewares);

  app.use("*", async (req, res) => {
    const url = req.originalUrl || "/";

    try {
      const templatePath = path.resolve(rootDir, "index.html");
      let template = await fs.readFile(templatePath, "utf-8");
      template = await vite.transformIndexHtml(url, template);

      const { createApp } = await vite.ssrLoadModule("/src/entry-server.jsx");
      const { app: appElement, queryClient } = await createApp({ url, headers: req.headers });

      const [head, tail] = template.split('<div id="root"></div>');
      if (!head || tail === undefined) {
        throw new Error("Template missing <div id=\"root\"></div> placeholder.");
      }

      let shellError;
      const { pipe, abort } = renderToPipeableStream(appElement, {
        onShellError(err) {
          shellError = err;
        },
        onShellReady() {
          if (shellError) {
            res.status(500).send("Server render failed.");
            return;
          }

          res.status(200);
          res.setHeader("Content-Type", "text/html");
          res.write(head);
          res.write('<div id="root">');
          pipe(res, { end: false });
        },
        onAllReady() {
          const serializedState = JSON.stringify(dehydrate(queryClient)).replace(/</g, "\\u003c");
          res.write("</div>");
          res.write(`<script>window.__TANSTACK_DEHYDRATED_STATE__=${serializedState};</script>`);
          res.write(tail);
          res.end();
        },
        onError(err) {
          console.error(err);
        },
      });

      setTimeout(() => abort(), 10_000).unref();
    } catch (error) {
      vite.ssrFixStacktrace(error);
      console.error(error);
      res.status(500).end(error.stack);
    }
  });

  const port = Number(process.env.SSR_PORT) || 4173;
  app.listen(port, () => {
    // eslint-disable-next-line no-console
    console.log(`SSR dev server running at http://localhost:${port}`);
  });
}

createServer();
