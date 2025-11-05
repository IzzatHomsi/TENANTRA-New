import express from "express";
import compression from "compression";
import fs from "node:fs/promises";
import fssync from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import http from "node:http";
import https from "node:https";
import { renderToPipeableStream } from "react-dom/server";
import { dehydrate } from "@tanstack/react-query";
import { runLoaders } from "./loaders.mjs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const rootDir = path.resolve(__dirname, "..");
const distDir = path.resolve(rootDir, "dist");
const ssrDir = path.resolve(rootDir, "dist-ssr");

async function readTemplate() {
  return fs.readFile(path.resolve(distDir, "index.html"), "utf-8");
}

async function loadSsrBundle() {
  const entry = path.resolve(ssrDir, "entry-server.js");
  return import(pathToFileURL(entry));
}

async function createServer() {
  const app = express();
  app.disable("x-powered-by");
  app.use(compression());

  app.use(
    "/assets",
    express.static(path.resolve(distDir, "assets"), {
      immutable: true,
      maxAge: "1y",
    })
  );

  app.use(
    "/catalog-remote",
    express.static(path.resolve(distDir, "catalog-remote"), {
      immutable: true,
      maxAge: "1h",
    })
  );

  const template = await readTemplate();
  const { createApp } = await loadSsrBundle();

  app.use("*", async (req, res) => {
    const url = req.originalUrl || "/";
    try {
      const { app: appElement, queryClient } = await createApp({
        url,
        headers: req.headers,
      });

      let html = template;
      const [head, tail] = html.split('<div id="root"></div>');
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
      console.error("[SSR] render failed", error);
      res.status(500).end("Internal Server Error");
    }
  });

  const port = Number(process.env.SSR_PORT) || 4173;
  const host = process.env.SSR_HOST || "0.0.0.0";
  const keyPath = process.env.SSR_SSL_KEY;
  const certPath = process.env.SSR_SSL_CERT;

  if (keyPath && certPath && fssync.existsSync(keyPath) && fssync.existsSync(certPath)) {
    const credentials = {
      key: await fs.readFile(keyPath),
      cert: await fs.readFile(certPath),
    };
    https.createServer(credentials, app).listen(port, host, () => {
      // eslint-disable-next-line no-console
      console.log(`SSR production server (HTTPS) running at https://${host}:${port}`);
    });
  } else {
    http.createServer(app).listen(port, host, () => {
      // eslint-disable-next-line no-console
      console.log(`SSR production server running at http://${host}:${port}`);
    });
  }
}

createServer();
